import copy
import os
import shutil
from typing import Set, Iterable, Dict, List, Optional, Tuple

from dew.projectproperties import ProjectProperties
from dew.dependencygraph import DependencyGraph
from dew.dependencyprocessor import DependencyProcessor
from dew.depstate import DependencyStateController
from dew.dewfile import DewFile, Dependency
from dew.exceptions import BuildError, DewfileError
from dew.storage import StorageController, BuildType, BUILD_TYPE_NAMES
from dew.view import View


class ProjectProcessor(object):

    def __init__(self, storage: StorageController, properties: ProjectProperties, view: View,
                 depstates: DependencyStateController):
        self.storage = storage
        self.root_dewfile: Optional[DewFile] = None
        self.properties = properties
        self.view = view
        self.depstates = depstates

    def set_data(self, dewfile: DewFile):
        self.root_dewfile = copy.deepcopy(dewfile)

    def process(self):
        dewfile_stack: List[Tuple[DewFile, Optional[str]]] = [(self.root_dewfile, None)]

        # Dependency processors by label
        dependency_processors: Dict[str, DependencyProcessor] = {}

        graph = DependencyGraph()
        deps_needing_build: Set[str] = set()

        while len(dewfile_stack) > 0:
            dewfile, parent_name = dewfile_stack.pop()
            for dep in dewfile.dependencies:
                dep_processor = self.make_processor(dep, dewfile)
                label = dep_processor.get_label()
                dependency_processors[label] = dep_processor
                graph.add_dependency(label, parent_name)

                # Connect manual dewfile dependencies
                for dfdep in dep.dependson:
                    graph.add_dependency(dfdep.get_label(), label)

                # if the dependency is up to date, don't bother pulling, as it's already been pulled.
                if not self.depstates.get_state(label):
                    self.view.info('Pulling dependency {0}...'.format(label))
                    dep_processor.pull()
                else:
                    self.view.info(f'Dependency {label} already pulled.')

                if dep_processor.has_dewfile():
                    try:
                        child_dewfile = dep_processor.get_dewfile()
                    except DewfileError as e:
                        self.view.dewfile_error(e)
                        raise

                    dewfile_stack.append((child_dewfile, label))

        for name, processor in dependency_processors.items():
            label = processor.get_label()
            if not self.depstates.get_state(label):
                deps_needing_build.add(label)

        labels_in_order = graph.resolve()

        for label in labels_in_order:
            dep_processor = dependency_processors[label]

            self.view.info('Building dependency {0}...'.format(label))

            node = graph.nodes[label]
            parent_node = node.parent

            while parent_node and parent_node.name:
                self.view.info(f'* which is needed by {parent_node.name}')
                parent_node = parent_node.parent

            if label not in deps_needing_build:
                self.view.info(f'Dependency {label} already built.')
                continue

            # Prepare output prefixes
            child_labels = [n.name for n in node.children]

            for build_type in self.properties.active_build_types():
                self.view.info(f'Building {BUILD_TYPE_NAMES[build_type]}...')
                output_prefix = self.get_isolated_prefix(label, build_type)
                shutil.rmtree(output_prefix)

                input_prefixes = [self.get_isolated_prefix(l, build_type) for l in child_labels]

                # Build and install
                dep_processor.build(output_prefix, input_prefixes, build_type)

            self.depstates.add(label)

        if len(deps_needing_build) > 0:
            for build_type in self.properties.active_build_types():
                self.view.info(f'Updating final {BUILD_TYPE_NAMES[build_type]} prefix')
                self.update_final_prefix(labels_in_order, build_type)

    def make_processor(self, dep: Dependency, dewfile: DewFile) -> DependencyProcessor:
        local_override = dewfile.local_overrides.get(dep.name)
        if local_override:
            dep = copy.deepcopy(dep)
            dep.type = 'local'
            dep.url = local_override
            dep_processor = DependencyProcessor(self.storage, self.view, dep, dewfile, self.properties)
            dep.ref = dep_processor.get_remote().get_latest_ref()

        dep_processor = DependencyProcessor(self.storage, self.view, dep, dewfile, self.properties)
        return dep_processor

    def get_isolated_prefix(self, label: str, type: BuildType) -> str:
        path = os.path.join(self.storage.get_output_prefix_dir(type), label)
        os.makedirs(path, exist_ok=True)
        return path

    def update_final_prefix(self, labels: Iterable[str], build_type: BuildType):
        success = True
        dst_prefix = self.storage.get_install_dir(build_type)
        installed_files: Dict[str, str] = {}

        for label in labels:
            src_prefix = self.get_isolated_prefix(label, build_type)

            for dirpath, dirnames, filenames in os.walk(src_prefix):
                relpath = os.path.relpath(dirpath, src_prefix)
                dst_dir = os.path.join(dst_prefix, relpath)

                for dirname in dirnames:
                    os.makedirs(os.path.join(dst_dir, dirname), exist_ok=True)

                for filename in filenames:
                    src_path = os.path.join(dirpath, filename)
                    dst_path = os.path.join(dst_dir, filename)

                    prefix_neutral_path = os.path.join(relpath, filename)

                    shutil.copy2(src_path, dst_path)

                    if prefix_neutral_path in installed_files:
                        self.view.error(f'Conflicting prefix files found! file: {prefix_neutral_path}, first occurance: {installed_files[prefix_neutral_path]}, current occurance: {label}')
                        success = False
                    else:
                        # Only copy files if we are currently succeding.
                        if success:
                            shutil.copy2(src_path, dst_path)
                        installed_files[prefix_neutral_path] = label

        if not success:
            raise BuildError(f'Failed while installing files')

    def update_refs(self) -> Tuple[DewFile, bool]:
        have_refs_changed = False
        for dep in self.root_dewfile.dependencies:
            if not dep.ref:
                self.view.info(f'Dependency {dep.name} does not have an assigned ref, fetching one now.')
                processor = DependencyProcessor(self.storage, self.view, dep, self.root_dewfile, self.properties)
                dep.ref = processor.get_remote().get_latest_ref()
                have_refs_changed = True
        return self.root_dewfile, have_refs_changed
