import os

import json
from typing import List, Any, Dict


class DewFile(object):
    def __init__(self) -> None:
        self.options: List[Option] = []
        self.dependencies: List[Dependency] = []


class Option(object):
    def __init__(self) -> None:
        self.name = ''
        self.default = False
        self.cmake_option = ''


class Dependency(object):
    def __init__(self) -> None:
        self.name = ''
        self.url = ''
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
        options = []
        dependencies = []
        options_obj = self.data.get('options', [])
        dependencies_obj = self.data['dependencies']
        for option in options_obj:
            options.append(self.parse_option(option))
        for dep in dependencies_obj:
            dependencies.append(self.parse_dependency(dep))

        dewfile = DewFile()
        dewfile.options = options
        dewfile.dependencies = dependencies
        return dewfile

    def parse_option(self, obj: Dict[str, Any]) -> Option:
        option = Option()
        option.name = obj['name']
        option.default = bool(obj.get('default', False))
        option.cmake_option = obj.get('cmake_option', '')
        return option

    def parse_dependency(self, obj: Dict[str, Any]) -> Dependency:
        dep = Dependency()
        dep.name = obj['name']
        dep.url = obj['url']
        dep.type = obj['type']
        dep.ref = obj['ref']
        dep.buildfile_dir = obj.get('buildfile_dir', '')
        dep.execute_after_fetch = obj.get('execute_after_fetch', '')

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


def overlay_dewfile(base: DewFile, overlay: DewFile) -> None:
    for dependency in overlay.dependencies:
        index = -1
        for i, base_dependency in enumerate(base.dependencies):
            if base_dependency.name == dependency.name:
                index = i
                break

        if index != -1:
            base.dependencies[index] = dependency


def parse_dewfile_with_local_overlay(path: str) -> DewFile:
    dewfile_parser = DewFileParser()
    with open(path) as file:
        dewfile_data = json.load(file)
    dewfile_parser.set_data(dewfile_data)
    dewfile = dewfile_parser.parse()

    local_overlay_path = os.path.normpath(os.path.join(path, '..', 'dewfile.local.json'))
    if os.path.isfile(local_overlay_path):
        dewfile_parser = DewFileParser()
        with open(local_overlay_path) as file:
            overlaw_dewfile_data = json.load(file)
        dewfile_parser.set_data(overlaw_dewfile_data)
        local_dewfile = dewfile_parser.parse()
        overlay_dewfile(dewfile, local_dewfile)

    return dewfile
