import multiprocessing
import os
from typing import Iterable

from dew.subprocesscaller import SubprocessCaller
from dew.builder import Builder
from dew.buildoptions import BuildOptions
from dew.dewfile import Dependency
from dew.view import View


class CMakeBuilder(Builder):
    def __init__(self, buildfile_dir: str, build_dir: str, install_dir: str, dependency: Dependency,
                 options: BuildOptions, caller: SubprocessCaller, view: View, prefix_paths: Iterable[str]) -> None:
        self.buildfile_dir = os.path.abspath(buildfile_dir)
        self.build_dir = os.path.abspath(build_dir)
        self.install_dir = os.path.abspath(install_dir)
        self.dependency = dependency
        self.options = options
        self.caller = caller
        self.view = view
        self.prefix_paths = list(prefix_paths)

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
            '-DCMAKE_PREFIX_PATH={0}'.format(';'.join(self.prefix_paths)),
            '-DCMAKE_BUILD_TYPE=Debug',  # TODO: Support building dependencies in release mode.
            '-DDEW_CMAKE_INTEGRATION_ENABLED=OFF'
        ]
        args.extend(self.dependency.build_arguments)

        # Configure
        self.caller.call(args, cwd=self.build_dir)

        build_args = [cmake_executable, '--build', '.']
        generator = self.options.cmake_generator
        if generator in ('Unix Makefiles', 'MinGW Makefiles'):
            build_args.extend(('--', '-j', str(multiprocessing.cpu_count())))

        # Build
        self.caller.call(
            build_args,
            cwd=self.build_dir,
        )

        # Install
        self.caller.call(
            [cmake_executable, '--build', '.', '--target', 'install'],
            cwd=self.build_dir
        )
