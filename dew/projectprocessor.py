from dew.buildoptions import BuildOptions
from dew.dependencygraph import DependencyGraph
from dew.dependencyprocessor import DependencyProcessor
from dew.dewfile import DewFile
from dew.storage import StorageController
from dew.view import View


class ProjectProcessor(object):

    def __init__(self, storage: StorageController, options: BuildOptions, view: View):
        self.storage = storage
        self.root_dewfile = None
        self.options = options
        self.view = view

    def set_data(self, dewfile: DewFile):
        self.root_dewfile = dewfile

    def process(self):
        dewfile_stack = [(self.root_dewfile, None)]

        # Dependency processors by name
        dependency_processors = {}

        graph = DependencyGraph()

        while len(dewfile_stack) > 0:
            dewfile, parent_name = dewfile_stack.pop()
            for dep in dewfile.dependencies:
                graph.add_dependency(dep.name, parent_name)

                dep_processor = DependencyProcessor(self.storage, self.view)
                dependency_processors[dep.name] = dep_processor

                dep_processor.set_data(dep, dewfile, self.options)

                self.view.info('Pulling dependency {0}...'.format(dep.name))
                dep_processor.pull()

                if dep_processor.has_dewfile():
                    dewfile_stack.append((dep_processor.get_dewfile(), dep.name))

        names_in_order = graph.resolve()

        for name in names_in_order:
            dep_processor = dependency_processors[name]
            self.view.info('Building dependency {0}...'.format(dep_processor.dependency.name))
            dep_processor.build()
