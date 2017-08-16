

class DewFile(object):
    def __init__(self):
        self.dependencies = []
        self.cmake_generator = ''

class Dependency(object):
    def __init__(self):
        self.name = ""
        self.url = "",
        self.type = ""
        self.ref = ""


class DewFileParser(object):
    def __init__(self):
        self.data = None

    def set_data(self, data):
        self.data = data

    def parse(self):
        dependencies = []
        dependencies_obj = self.data['dependencies']
        for dep in dependencies_obj:
            dependencies.append(self.parse_dependency(dep))

        dewfile = DewFile()
        dewfile.dependencies = dependencies
        dewfile.cmake_generator = self.data['cmake_generator']
        return dewfile

    def parse_dependency(self, obj):
        dep = Dependency()
        dep.name = obj['name']
        dep.url = obj['url']
        dep.type = obj['type']
        dep.ref = obj['ref']
        return dep

