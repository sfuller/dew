import multiprocessing
import os, pathlib, posixpath
from typing import Iterable, ItemsView, Optional

from dew.exceptions import BuildError
from dew.subprocesscaller import SubprocessCaller
from dew.builder import Builder
from dew.projectproperties import ProjectProperties
from dew.view import View
from dew.storage import BuildType

CMAKE_BUILD_TYPES = {BuildType.Debug:'Debug', BuildType.Release:'RelWithDebInfo'}

class CMakeBuilder(Builder):
    def __init__(self,
                 buildfile_dir: str,
                 build_dir: str,
                 install_dir: Optional[str],
                 build_type: BuildType,
                 properties: ProjectProperties,
                 caller: SubprocessCaller,
                 view: View,
                 additional_prefix_paths: Iterable[str] = (),
                 additional_cmake_defines: Optional[ItemsView[str, str]] = None
                 ) -> None:
        self.buildfile_dir = pathlib.PurePath(os.path.abspath(buildfile_dir)).as_posix()
        self.build_dir = pathlib.PurePath(os.path.abspath(build_dir)).as_posix()
        if install_dir:
            self.install_dir = pathlib.PurePath(os.path.abspath(install_dir)).as_posix()
        else:
            self.install_dir = None
        self.build_type = build_type
        self.properties = properties
        self.caller = caller
        self.view = view
        self.additional_prefix_paths = list(additional_prefix_paths)
        self.additional_cmake_defines = additional_cmake_defines

    def get_cmake_executable(self) -> str:
        cmake_executable = self.properties.cmake_executable
        if not cmake_executable:
            cmake_executable = 'cmake'
        return cmake_executable

    def build(self) -> None:
        install_dir = self.install_dir
        os.makedirs(self.build_dir, exist_ok=True)

        cmake_executable = self.get_cmake_executable()

        prefix_paths = self.properties.prefixes.copy()
        prefix_paths.extend(self.additional_prefix_paths)
        prefix_paths = [pathlib.PurePath(prefix).as_posix() for prefix in prefix_paths]

        module_paths = [posixpath.join(prefix, 'share', 'cmake', 'Modules') for prefix in prefix_paths]

        generator = self.properties.cmake_generator
        if not generator:
            generator = guess_generator()
            if not generator:
                raise BuildError('Cannot guess CMake generator to use. ' 
                                 'Please specify a generator using the --cmake-generator flag.')

        args = [
            cmake_executable,
            '-G', generator,
            self.buildfile_dir,
            '-DCMAKE_PREFIX_PATH={0}'.format(';'.join(prefix_paths)),
            '-DCMAKE_MODULE_PATH={0}'.format(';'.join(module_paths)),
            '-DCMAKE_BUILD_TYPE={0}'.format(CMAKE_BUILD_TYPES[self.build_type]),

            # Lots of projects default to build shared libs instead of static. Let's add some consistency.
            # TODO: Need a system to choose the types of libraries desired.
            '-DBUILD_SHARED_LIBS=OFF'
        ]

        if install_dir:
            args.append('-DCMAKE_INSTALL_PREFIX={0}'.format(install_dir),)

        if self.additional_cmake_defines:
            args.extend([f'-D{k}={v}' for k, v in self.additional_cmake_defines.items()])

        # Setup environment
        env = {
            'CC': self.properties.c_compiler_path,
            'CXX': self.properties.cxx_compiler_path,
            'INVOKED_BY_DEW': 'true'  # Set this environment variable to alert the dew CMake modules to no-op.
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
        if install_dir:
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
