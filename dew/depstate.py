import os

from typing import Set

from dew.storage import StorageController, BuildType, BUILD_TYPE_NAMES


class DependencyStateController(object):
    def __init__(self, storage: StorageController) -> None:
        self.storage = storage
        self.states: Dict[BuildType, Set[str]] = {tp:set() for tp in BUILD_TYPE_NAMES}

    def get_state(self, type: BuildType, label: str) -> bool:
        return label in self.states[type]

    def get_any_state(self, label: str) -> bool:
        for (k,v) in self.states.items():
            if label in v:
                return True
        return False

    def load(self) -> None:
        for tp in BUILD_TYPE_NAMES:
            path = self.get_state_file_path(tp)
            if not os.path.isfile(path):
                continue

            with open(path) as f:
                contents = f.read()

            lines = contents.split('\n')

            self.states[tp].clear()

            for line in lines:
                if line:
                    self.states[tp].add(line)

    def save(self) -> None:
        for tp in BUILD_TYPE_NAMES:
            contents = '\n'.join(self.states[tp])

            with open(self.get_state_file_path(tp), 'w') as f:
                f.write(contents)

    def get_state_file_path(self, type: BuildType) -> str:
        return self.storage.join_storage_dir_path(f'depstates-{BUILD_TYPE_NAMES[type]}')

    def clear(self) -> None:
        for (k,v) in self.states.items():
            v.clear()

    def add(self, type: BuildType, label: str):
        self.states[type].add(label)
