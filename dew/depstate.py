import os

from typing import Set

from dew.storage import StorageController


class DependencyStateController(object):
    def __init__(self, storage: StorageController) -> None:
        self.storage = storage
        self.states: Set[str] = set()

    def get_state(self, label: str) -> bool:
        return label in self.states

    def load(self) -> None:
        if not os.path.isfile(self.get_state_file_path()):
            return

        with open(self.get_state_file_path()) as f:
            contents = f.read()

        lines = contents.split('\n')

        self.states.clear()

        for line in lines:
            if line:
                self.states.add(line)

    def save(self) -> None:
        contents = '\n'.join(self.states)

        with open(self.get_state_file_path(), 'w') as f:
            f.write(contents)

    def get_state_file_path(self) -> str:
        return self.storage.join_storage_dir_path('depstates')

    def clear(self) -> None:
        self.states.clear()

    def add(self, label: str):
        self.states.add(label)
