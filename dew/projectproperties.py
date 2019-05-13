import copy
import json
import os.path
from typing import Dict, Union, Any, List, Tuple

from dew.storage import StorageController, BuildType

BUILD_TYPE_TUPLES = {'debug':(BuildType.Debug,),
                     'release':(BuildType.Release,),
                     'both':(BuildType.Debug, BuildType.Release)}

class ProjectProperties(object):
    def __init__(self):
        self.cmake_generator = ''
        self.cmake_executable = ''
        self.c_compiler_path = ''
        self.cxx_compiler_path = ''
        self.prefixes: List[str] = []
        self.options: Dict[str, Union[str, bool]] = {}
        self.build_type = 'both'

    def active_build_types(self) -> Tuple[BuildType]:
        return BUILD_TYPE_TUPLES[self.build_type]

class ProjectPropertiesController(object):
    def __init__(self, storage: StorageController):
        self.storage = storage
        self.properties_dict: Dict[str, Any] = {}
        self.dirty = False

    def load(self) -> None:
        cache_path = self.get_cache_file_path()
        if os.path.isfile(cache_path):
            with open(cache_path) as f:
                properties = self.from_dict(json.load(f))
        else:
            properties = ProjectProperties()
        self.properties_dict = self.to_dict(properties)
        self.dirty = False

    def save(self) -> None:
        cache_path = self.get_cache_file_path()
        with open(cache_path, 'w') as f:
            json.dump(self.properties_dict, f, indent=4)
        self.dirty = False

    def get(self) -> ProjectProperties:
        return self.from_dict(self.properties_dict)

    def set(self, properties: ProjectProperties) -> None:
        new_dict = self.to_dict(properties)
        if self.are_dicts_different(self.properties_dict, new_dict):
            self.dirty = True
        self.properties_dict = new_dict

    def from_dict(self, data: Dict[str, Any]) -> ProjectProperties:
        properties = ProjectProperties()
        properties.cmake_generator = data.get('cmake_generator', '')
        properties.cmake_executable = data.get('cmake_executable', '')
        properties.c_compiler_path = data.get('c_compiler_path', '')
        properties.cxx_compiler_path = data.get('cxx_compiler_path', '')
        properties.prefixes = list(data.get('prefixes', []))
        properties.options = dict(data.get('options', {}))
        properties.build_type = data.get('build_type', 'both')
        if properties.build_type not in ('debug', 'release', 'both'):
            properties.build_type = 'both'
        return properties

    def to_dict(self, properties: ProjectProperties) -> Dict[str, str]:
        data = dict()
        data['cmake_generator'] = properties.cmake_generator
        data['cmake_executable'] = properties.cmake_executable
        data['c_compiler_path'] = properties.c_compiler_path
        data['cxx_compiler_path'] = properties.cxx_compiler_path
        data['prefixes'] = properties.prefixes.copy()
        data['options'] = copy.deepcopy(properties.options)
        data['build_type'] = properties.build_type
        return data

    def get_cache_file_path(self) -> str:
        return os.path.join(self.storage.get_storage_dir(), 'cache.json')

    def are_objects_different(self, object_a: Any, object_b: Any) -> bool:
        if type(object_a) != type(object_b):
            return True

        if isinstance(object_a, dict):
            return self.are_dicts_different(object_a, object_b)
        if isinstance(object_a, list):
            return self.are_lists_different(object_a, object_b)

        return object_a != object_b

    def are_lists_different(self, list_a: List[Any], list_b: List[Any]) -> bool:
        if len(list_a) != len(list_b):
            return True

        for i in range(len(list_a)):
            value_a = list_a[i]
            value_b = list_b[i]
            if self.are_objects_different(value_a, value_b):
                return True

        return False

    def are_dicts_different(self, dict_a: Dict[str, Any], dict_b: Dict[str, Any]) -> bool:
        for name, value in dict_a.items():
            other_value = dict_b.get(name)

            if self.are_objects_different(value, other_value):
                return True

        return False
