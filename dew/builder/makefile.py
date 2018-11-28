from dew.builder import Builder
from dew.buildoptions import BuildOptions
from dew.dewfile import Dependency
from dew.exceptions import BuildError
from dew.subprocesscaller import SubprocessCaller
from dew.view import View


class MakefileBuilder(Builder):
    def __init__(self, buildfile_dir: str, build_dir: str, install_dir: str, dependency: Dependency,
                 options: BuildOptions, caller: SubprocessCaller, view: View) -> None:
        self.buildfile_dir = buildfile_dir
        self.build_dir = build_dir
        self.install_dir = install_dir
        self.dependency = dependency
        self.options = options
        self.caller = caller
        self.view = view

    def build(self) -> None:
        self.view.error('Building makefiles is not supported yet')
        raise BuildError()
