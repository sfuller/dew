

class DewFile(object):
    def __init__(self):
        self.dependencies = []


class Dependency(object):
    def __init__(self):
        self.name = ''
        self.url = '',
        self.type = ''
        self.ref = ''
        self.buildfile_dir = ''
        self.build_arguments = []
        self.fixes = []


class Fix(object):
    def __init__(self):
        self.type = ''
        self.params = {}


class DewFileParser(object):
    def __init__(self):
        self.data = None

    def set_data(self, data) -> None:
        self.data = data

    def parse(self) -> DewFile:
        dependencies = []
        dependencies_obj = self.data['dependencies']
        for dep in dependencies_obj:
            dependencies.append(self.parse_dependency(dep))

        dewfile = DewFile()
        dewfile.dependencies = dependencies
        return dewfile

    def parse_dependency(self, obj) -> Dependency:
        dep = Dependency()
        dep.name = obj['name']
        dep.url = obj['url']
        dep.type = obj['type']
        dep.ref = obj['ref']
        dep.buildfile_dir = obj.get('buildfile_dir', '')

        build_arguments = obj.get('build_arguments', [])
        if isinstance(build_arguments, str):
            build_arguments = [build_arguments]

        for arg in build_arguments:
            dep.build_arguments.append(str(arg))

        fixes_obj = obj.get('fixes', [])
        for fix in fixes_obj:
            dep.fixes.append(self.parse_fix(fix))

        return dep

    def parse_fix(self, obj) -> Fix:
        fix = Fix()
        fix.type = obj['type']
        fix.params = obj['params']
        return fix
