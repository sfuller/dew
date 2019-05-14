from typing import Iterable

from dew.builder import Builder
from dew.projectproperties import ProjectProperties
from dew.dewfile import Dependency
from dew.subprocesscaller import SubprocessCaller
from dew.view import View
from dew.storage import BuildType


class MakefileBuilder(Builder):
    def __init__(self, buildfile_dir: str, build_dir: str, install_dir: str, build_type: BuildType,
                 dependency: Dependency, options: ProjectProperties, caller: SubprocessCaller,
                 view: View, prefix_paths: Iterable[str]) -> None:
        self.buildfile_dir = buildfile_dir
        self.build_dir = build_dir
        self.install_dir = install_dir
        self.build_type = build_type
        self.dependency = dependency
        self.options = options
        self.caller = caller
        self.view = view
        self.prefix_paths = list(prefix_paths)

    def build(self) -> None:

        self.caller.call([
                'make',
                f'DESTDIR={self.install_dir}'
                'install'
            ],
            cwd=self.buildfile_dir
        )
