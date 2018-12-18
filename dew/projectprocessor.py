import os
import shutil
from typing import Set, Iterable, Dict

from dew.buildoptions import BuildOptions
from dew.dependencygraph import DependencyGraph
from dew.dependencyprocessor import DependencyProcessor
from dew.depstate import DependencyStateController
from dew.dewfile import DewFile
from dew.exceptions import BuildError
from dew.storage import StorageController
from dew.view import View


class ProjectProcessor(object):

    def __init__(self, storage: StorageController, options: BuildOptions, view: View,
                 depstates: DependencyStateController):
        self.storage = storage
        self.root_dewfile = None
        self.options = options
        self.view = view
        self.depstates = depstates

    def set_data(self, dewfile: DewFile):
        self.root_dewfile = dewfile

    def process(self):
        dewfile_stack = [(self.root_dewfile, None)]

        # Dependency processors by label
        dependency_processors = {}

        graph = DependencyGraph()
        deps_needing_rebuild: Set[str] = set()

        while len(dewfile_stack) > 0:
            dewfile, parent_name = dewfile_stack.pop()
            for dep in dewfile.dependencies:
                dep_processor = DependencyProcessor(self.storage, self.view, dep, dewfile, self.options)
                label = self.get_label(dep.name, dep_processor.get_version())
                dep_processor.set_label(label)
                dependency_processors[label] = dep_processor

                graph.add_dependency(label, parent_name)

                if self.depstates.get_state(label):
                    self.view.verbose(f'{label} is up to date.')
                    continue

                deps_needing_rebuild.add(label)

                self.view.info('Pulling dependency {0}...'.format(label))
                dep_processor.pull()

                if dep_processor.has_dewfile():
                    dewfile_stack.append((dep_processor.get_dewfile(), label))

        labels_in_order = graph.resolve()

        for label in labels_in_order:
            dep_processor = dependency_processors[label]

            if label not in deps_needing_rebuild:
                continue

            self.view.info('Building dependency {0}...'.format(dep_processor.dependency.name))

            # Prepare output prefix
            child_labels = [n.name for n in graph.nodes[label].children]
            output_prefix = self.get_isolated_prefix(label)
            shutil.rmtree(output_prefix)

            input_prefixes = [self.get_isolated_prefix(l) for l in child_labels]

            # Build and install
            dep_processor.build(output_prefix, input_prefixes)

            self.depstates.add(label)

        if len(deps_needing_rebuild) > 0:
            self.update_final_prefix(labels_in_order)

    def get_isolated_prefix(self, label: str) -> str:
        path = os.path.join(self.storage.get_output_prefix_dir(), label)
        os.makedirs(path, exist_ok=True)
        return path

    def copy_prefix(self, src_prefix: str, dst_prefix: str) -> None:
        for dirpath, dirnames, filenames in os.walk(src_prefix):
            relpath = os.path.relpath(dirpath, src_prefix)
            dst_dir = os.path.join(dst_prefix, relpath)

            for dirname in dirnames:
                os.makedirs(os.path.join(dst_dir, dirname), exist_ok=True)

            for filename in filenames:
                src_path = os.path.join(dirpath, filename)
                dst_path = os.path.join(dst_dir, filename)

                shutil.copy2(src_path, dst_path)

    def update_final_prefix(self, labels: Iterable[str]):
        success = True
        dst_prefix = self.storage.get_install_dir()
        installed_files: Dict[str, str] = {}

        for label in labels:
            src_prefix = self.get_isolated_prefix(label)

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

    def get_label(self, name: str, version: str) -> str:
        return f'{name}_{version}'
