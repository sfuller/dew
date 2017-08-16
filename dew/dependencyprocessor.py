import os.path
import subprocess
from enum import Enum, auto

from dew.dewfile import Dependency, DewFile
from dew.storage import StorageController
from dew import git


class BuildSystem(Enum):
    UNKNOWN = auto()
    CMAKE = auto()
    MAKEFILE = auto()


class DependencyProcessor(object):
    def __init__(self, storage: StorageController):
        self.storage = storage
        self.dependency = None
        self.dewfile = None

    def set_data(self, dependency: Dependency, dewfile: DewFile):
        self.dependency = dependency
        self.dewfile = dewfile

    def process(self):
        if self.dependency.type == 'git':
            self.process_git()
        else:
            print('Unknown dependency type')

        self.build()

    def process_git(self):
        dest_dir = self.get_src_dir()
        git.clone_repo(self.dependency.url, dest_dir, self.dependency.ref)

    def build(self):
        buildsystem = self.get_buildsystem()
        if buildsystem == BuildSystem.MAKEFILE:
            self.build_makefile()
        elif buildsystem == BuildSystem.CMAKE:
            self.build_cmake()
        else:
            print('Unknown build system')

    def get_src_dir(self):
        return os.path.join(self.storage.get_sources_dir(), self.dependency.name)

    def get_build_dir(self):
        return os.path.join(self.storage.get_builds_dir(), self.dependency.name)

    def get_buildsystem(self):
        """ Guesses the build system """
        src_path = self.get_src_dir()
        if os.path.isfile(os.path.join(src_path, 'CMakeLists.txt')):
            return BuildSystem.CMAKE
        if os.path.isfile(os.path.join(src_path, 'Makefile')):
            return BuildSystem.MAKEFILE
        return BuildSystem.UNKNOWN

    def build_cmake(self):
        src_dir = self.get_src_dir()
        build_dir = self.get_build_dir()
        install_dir = self.storage.get_install_dir()
        os.makedirs(build_dir, exist_ok=True)

        # Configure
        self.call(
            [
                'cmake',
                '-G', self.dewfile.cmake_generator,
                src_dir,
                '-DCMAKE_INSTALL_PREFIX={0}'.format(install_dir),
                '-DCMAKE_PREFIX_PATH={0}'.format(install_dir)
            ],
            cwd=build_dir
        )

        # Build
        self.call(
            ['cmake', '--build', '.'],
            cwd=build_dir,
        )

        # Install
        self.call(
            ['cmake', '-DCMAKE_INSTALL_CONFIG_NAME=Debug', '-P', 'cmake_install.cmake'],
            cwd=build_dir
        )

    def build_makefile(self):
        print('building makefile is not supported yet')


    def call(self, args, cwd):
        print('Calling subprocess: "{0}", cwd: {1}'.format(' '.join(args), cwd))
        subprocess.check_call(args, cwd=cwd)
