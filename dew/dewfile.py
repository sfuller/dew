import sys
import os
import json
from typing import List, Any, Dict

from dew.exceptions import DewfileError


class DewFile(object):
    def __init__(self) -> None:
        self.options: List[Option] = []
        self.dependencies: List[Dependency] = []
        self.local_overrides: Dict[str, str] = {}


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
        self.head = ''
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
        self.data: Dict[str, Any] = {}
        self.refs: Dict[str, str] = {}

    def set_data(self, data: Dict[str, Any], refs: Dict[str, str]) -> None:
        self.data = data
        self.refs = refs

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
        dep.head = obj['head']
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

        dep.ref = self.refs.get(dep.name)

        return dep

    def parse_fix(self, obj) -> Fix:
        fix = Fix()
        fix.type = obj['type']
        fix.params = obj['params']
        return fix


def overlay_dewfile(base: DewFile, overlay: DewFile) -> None:
    for dependency in overlay.dependencies:
        base.local_overrides[dependency.name] = dependency.url


def parse_refs(path: str) -> Dict[str, str]:
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def parse_dewfile(path: str) -> DewFile:
    dewfile_parser = DewFileParser()
    dewfile_data = load_json(path)
    refs = parse_refs(get_ref_file_path(path))
    dewfile_parser.set_data(dewfile_data, refs)
    try:
        return dewfile_parser.parse()
    except Exception as e:
        raise DewfileError(path, sys.exc_info()[2]) from e


def parse_dewfile_with_local_overlay(path: str) -> DewFile:
    dewfile = parse_dewfile(path)
    local_overlay_path = os.path.normpath(os.path.join(path, '..', 'dewfile.local.json'))

    if os.path.isfile(local_overlay_path):
        dewfile_parser = DewFileParser()
        overlaw_dewfile_data = load_json(local_overlay_path)
        dewfile_parser.set_data(overlaw_dewfile_data, {})
        try:
            local_dewfile = dewfile_parser.parse()
        except Exception as e:
            raise DewfileError(local_overlay_path, sys.exc_info()[2]) from e
        overlay_dewfile(dewfile, local_dewfile)

    return dewfile


def save_refs(dewfile: DewFile, dewfile_path: str) -> None:
    refs: Dict[str, str] = {}
    for dep in dewfile.dependencies:
        refs[dep.name] = dep.ref
    refs_path = get_ref_file_path(dewfile_path)
    with open(refs_path, 'w') as f:
        json.dump(refs, f, indent=4)


def get_ref_file_path(dewfile_path: str) -> str:
    return os.path.normpath(os.path.join(dewfile_path, '..', 'dewfile.refs.json'))


def load_json(path: str) -> Dict[str, Any]:
    with open(path) as file:
        contents = file.read()

    lines = contents.split('\n')
    final_lines = []
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith('#') or stripped.startswith('//'):
            final_lines.append('')
        else:
            final_lines.append(line)

    return json.loads('\n'.join(final_lines))
