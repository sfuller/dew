import sys
import os
import json
from typing import List, Any, Dict

from dew.exceptions import DewfileError, DewError

class Dependency(object):
    def __init__(self) -> None:
        self.name: str = ''
        self.url: str = ''
        self.type: str = ''
        self.head: str = ''
        self.ref: str = ''
        self.buildfile_dir: str = ''
        self.dependson: List[Dependency] = []
        self.cmake_defines: Dict[str, str] = {}

    def get_version(self) -> str:
        return f'{self.type}_{self.ref}'

    def get_label(self) -> str:
        name = self.name
        version = self.get_version()
        return f'{name}_{version}'

class DewFile(object):
    def __init__(self, path: str) -> None:
        self.path = path
        self.dependencies: List[Dependency] = []
        self.local_overrides: Dict[str, str] = {}

    def find_dependency(self, name: str) -> Dependency:
        try:
            return next(d for d in self.dependencies if d.name == name)
        except Exception as e:
            raise DewfileError(self.path, sys.exc_info()[2], f'"{name}" not found') from e

def _parse_dewfile(data: Dict[str, Any], path: str) -> DewFile:
    dependencies = []
    dependencies_obj = data['dependencies']

    # 1st pass: parse dependencies
    for dep in dependencies_obj:
        dependencies.append(parse_dependency(dep))

    dewfile = DewFile(path)
    dewfile.dependencies = dependencies

    # 2nd pass: resolve manual dependencies
    for dep in dewfile.dependencies:
        resolved_deps = []
        for dfdep in dep.dependson:
            resolved_deps.append(dewfile.find_dependency(dfdep))
        dep.dependson = resolved_deps

    return dewfile


def serialize_dewfile(dewfile: DewFile) -> Dict[str, Any]:
    data = {}
    dependencies = []
    for dep in dewfile.dependencies:
        dependencies.append(serialize_dependency(dep))
    data['dependencies'] = dependencies
    return data


def parse_dependency(obj: Dict[str, Any]) -> Dependency:
    dep = Dependency()
    dep.name = obj['name']
    dep.url = obj['url']
    dep.type = obj['type']
    dep.head = obj['head']
    dep.ref = obj['ref']
    dep.buildfile_dir = obj.get('buildfile_dir', '')
    dependson = obj.get('dependson', [])
    if dependson: # Resolved into List[Dependency] in _parse_dewfile
        dep.dependson = [str(d) for d in dependson]
    cmake_defines = obj.get('cmake_defines', {})
    if cmake_defines:
        dep.cmake_defines = {str(k):str(v) for k, v in cmake_defines.items()}
    return dep


def serialize_dependency(dep: Dependency) -> Dict[str, Any]:
    data = {
        'name': dep.name,
        'url': dep.url,
        'type': dep.type,
        'head': dep.head
    }

    if dep.ref:
        data['ref'] = dep.ref
    if dep.buildfile_dir:
        data['buildfile_dir'] = dep.buildfile_dir
    if dep.dependson:
        data['dependson'] = [d.name for d in dep.dependson]
    if dep.cmake_defines:
        data['cmake_defines'] = dep.cmake_defines

    return data


def parse_dewfile(path: str) -> DewFile:
    try:
        dewfile_data = load_json(path)
        dewfile = _parse_dewfile(dewfile_data, path)
    except Exception as e:
        raise DewfileError(path, sys.exc_info()[2]) from e
    return dewfile


def parse_local_work_file(path: str) -> Dict[str, str]:
    if not os.path.isfile(path):
        return {}

    with open(path) as f:
        try:
            data = json.load(f)
        except Exception as e:
            raise DewfileError(path, sys.exc_info()[2]) from e

    if not isinstance(data, dict):
        raise DewError('fContents of {path} is misformatted.')

    return {name: str(path) for name, path in data.items()}


def save_dewfile(dewfile: DewFile, path: str) -> None:
    with open(path, 'w') as f:
        json.dump(serialize_dewfile(dewfile), f, indent=4)


def save_local_work(dewfile: DewFile, path: str) -> None:
    with open(path, 'w') as f:
        json.dump(dewfile.local_overrides, f, indent=4)


def load_json(path: str) -> Dict[str, Any]:
    with open(path) as file:
        return json.load(file)


class ProjectFilesParser(object):
    def __init__(self, dewfile_path: str):
        self.dewfile_path = dewfile_path

        path_without_ext, ext = os.path.splitext(self.dewfile_path)
        self.local_work_path = path_without_ext + '.local' + ext

    def parse(self) -> DewFile:
        dewfile = parse_dewfile(self.dewfile_path)
        dewfile.local_overrides = parse_local_work_file(self.local_work_path)
        return dewfile

    def save(self, dewfile: DewFile) -> None:
        save_dewfile(dewfile, self.dewfile_path)

    def save_local_work(self, dewfile: DewFile) -> None:
        save_local_work(dewfile, self.local_work_path)
