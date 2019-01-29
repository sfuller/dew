import multiprocessing
import os
from typing import Iterable, Optional

from dew.exceptions import BuildError
from dew.subprocesscaller import SubprocessCaller
from dew.builder import Builder
from dew.projectproperties import ProjectProperties
from dew.dewfile import Dependency
from dew.view import View


class CMakeBuilder(Builder):
    def __init__(self, buildfile_dir: str, build_dir: str, install_dir: str, dependency: Dependency,
                 properties: ProjectProperties, caller: SubprocessCaller, view: View, prefix_paths: Iterable[str]) -> None:
        self.buildfile_dir = os.path.abspath(buildfile_dir)
        self.build_dir = os.path.abspath(build_dir)
        self.install_dir = os.path.abspath(install_dir)
        self.dependency = dependency
        self.properties = properties
        self.caller = caller
        self.view = view
        self.prefix_paths = list(prefix_paths)

    def get_cmake_executable(self) -> str:
        cmake_executable = self.properties.cmake_executable
        if not cmake_executable:
            cmake_executable = 'cmake'
        return cmake_executable

    def build(self) -> None:
        install_dir = self.install_dir
        os.makedirs(self.build_dir, exist_ok=True)

        cmake_executable = self.get_cmake_executable()

        module_paths = [os.path.join(prefix, 'share', 'cmake', 'Modules') for prefix in self.prefix_paths]

        generator = self.properties.cmake_generator
        if not generator:
            generator = guess_generator()
            if not generator:
                raise BuildError('Cannot guess CMake generator to use. ' 
                                 'Please specify a generator using the --guess-generator flag.')

        args = [
            cmake_executable,
            '-G', generator,
            self.buildfile_dir,
            '-DCMAKE_INSTALL_PREFIX={0}'.format(install_dir),
            '-DCMAKE_PREFIX_PATH={0}'.format(';'.join(self.prefix_paths)),
            '-DCMAKE_MODULE_PATH={0}'.format(';'.join(module_paths)),
            '-DCMAKE_BUILD_TYPE=Debug',  # TODO: Support building dependencies in release mode.
            '-DDEW_CMAKE_INTEGRATION_ENABLED=OFF'
        ]
        args.extend(self.dependency.build_arguments)

        # Lots of projects default to build shared libs instead of static. Let's add some consistency.
        args.append('-DBUILD_SHARED_LIBS=OFF')

        # Setup environment
        env = {
            'PATH': os.environ.get('PATH'),
            'CC': self.properties.c_compiler_path,
            'CXX': self.properties.cxx_compiler_path
        }

        # Configure
        self.caller.call(args, cwd=self.build_dir, error_exception=BuildError, env=env)

        build_args = [cmake_executable, '--build', '.']
        if generator in ('Unix Makefiles', 'MinGW Makefiles'):
            build_args.extend(('--', '-j', str(multiprocessing.cpu_count())))

        # Build
        self.caller.call(
            build_args,
            cwd=self.build_dir,
            error_exception=BuildError
        )

        # Install
        self.caller.call(
            [cmake_executable, '--build', '.', '--target', 'install'],
            cwd=self.build_dir,
            error_exception=BuildError
        )


GUESSED_GENERATOR: Optional[str] = None


def guess_generator() -> Optional[str]:
    global GUESSED_GENERATOR
    if GUESSED_GENERATOR:
        return GUESSED_GENERATOR

    guess = None

    paths = os.environ.get('PATH', '').split(os.pathsep)
    if os.name == 'nt':
        extensions = os.environ.get('PATHEXT').split(';')
    else:
        extensions = ['']

    def locate(name: str) -> bool:
        for path in paths:
            for entry in os.listdir(path):
                filename, ext = os.path.splitext(entry)
                if filename != name:
                    continue
                if ext not in extensions:
                    continue
                return True

    if locate('make'):
        guess = 'Unix Makefiles'
    elif locate('mingw32-make'):
        guess = 'MinGW Makefiles'

    GUESSED_GENERATOR = guess
    return guess
