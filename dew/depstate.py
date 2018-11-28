import copy
import json

from typing import Dict, Any

from dew.storage import StorageController


class DependencyStateInfo(object):
    def __init__(self) -> None:
        self.remote_type = ''
        self.version = ''


class DependencyStateController(object):
    def __init__(self, storage: StorageController) -> None:
        self.storage = storage
        self.states: Dict[str, DependencyStateInfo] = {}

    def get_state(self, name: str) -> DependencyStateInfo:
        info = self.states.get(name)
        if info is None:
            info = DependencyStateInfo()
        else:
            info = copy.copy(info)
        return info

    def load(self) -> None:
        with open(self.get_state_file_path()) as f:
            data = json.load(f)

        self.states.clear()

        for key, value in data:
            info = self.parse_state_info(value)
            self.states[key] = info

    def parse_state_info(self, data: Dict[str, Any]) -> DependencyStateInfo:
        info = DependencyStateInfo()
        info.remote_type = str(data.get('remote_type', ''))
        info.version = str(data.get('version', ''))
        return info

    def serialize_state_info(self, info: DependencyStateInfo) -> Dict[str, Any]:
        data = []
        data['remote_type'] = info.remote_type
        data['version'] = info.version
        return data

    def get_state_file_path(self) -> str:
        return self.storage.join_storage_dir_path('depstate.json')

    def save(self) -> None:
        data = []

        for key, value in self.states:
            data[key] = self.serialize_state_info(value)

        with open(self.get_state_file_path(), 'w') as f:
            json.dump(data, f)
