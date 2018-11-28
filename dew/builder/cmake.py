import os

from dew.subprocesscaller import SubprocessCaller
from dew.builder import Builder
from dew.buildoptions import BuildOptions
from dew.dewfile import Dependency
from dew.view import View


class CMakeBuilder(Builder):
    def __init__(self, buildfile_dir: str, build_dir: str, install_dir: str, dependency: Dependency,
                 options: BuildOptions, caller: SubprocessCaller, view: View) -> None:
        self.buildfile_dir = buildfile_dir
        self.build_dir = build_dir
        self.install_dir = install_dir
        self.dependency = dependency
        self.options = options
        self.caller = caller
        self.view = view

    def get_cmake_executable(self) -> str:
        cmake_executable = self.options.cmake_executable
        if not cmake_executable:
            cmake_executable = 'cmake'
        return cmake_executable

    def build(self) -> None:
        install_dir = self.install_dir
        os.makedirs(self.build_dir, exist_ok=True)

        cmake_executable = self.get_cmake_executable()

        args = [
            cmake_executable,
            '-G', self.options.cmake_generator,
            self.buildfile_dir,
            '-DCMAKE_INSTALL_PREFIX={0}'.format(install_dir),
            '-DCMAKE_PREFIX_PATH={0}'.format(install_dir),
            '-DCMAKE_BUILD_TYPE=Debug'
        ]
        args.extend(self.dependency.build_arguments)

        # Configure
        self.caller.call(args, cwd=self.build_dir)

        # Build
        self.caller.call(
            [cmake_executable, '--build', '.'],
            cwd=self.build_dir,
        )

        # Install
        self.caller.call(
            [cmake_executable, '--build', '.', '--target', 'install'],
            cwd=self.build_dir
        )
