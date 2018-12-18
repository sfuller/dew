import os.path
from enum import Enum
from typing import Optional, Iterable

import dew
from dew.builder import Builder
from dew.builder.cmake import CMakeBuilder
from dew.builder.makefile import MakefileBuilder
from dew.builder.xcode import XcodeBuilder
from dew.buildoptions import BuildOptions
from dew.dewfile import Dependency, DewFile
from dew.exceptions import BuildError, PullError
from dew.remote import Remote
from dew.remote.git import GitRemote
from dew.remote.local import LocalRemote
from dew.storage import StorageController
from dew.subprocesscaller import SubprocessCaller
from dew.view import View


class BuildSystem(Enum):
    UNKNOWN = 0
    CMAKE = 1
    MAKEFILE = 2
    XCODE = 3


class DependencyProcessor(object):
    def __init__(self, storage: StorageController, view: View, dependency: Dependency, dewfile: DewFile,
                 options: BuildOptions):
        self.label = ''
        self.storage = storage
        self.dependency = dependency
        self.dewfile = dewfile
        self.options = options
        self.view = view
        self._remote = None

    def set_label(self, label: str):
        self.label = label

    def pull(self):
        self.get_remote().pull(self.get_source_dir())

    def build(self, install_dir: str, input_prefixes: Iterable[str]):
        self.get_builder(install_dir, input_prefixes).build()

    def get_remote(self) -> Optional[Remote]:
        if self._remote:
            return self._remote

        type = self.dependency.type
        factory = None

        if type == 'git':
            factory = GitRemote
        elif type == 'local':
            factory = LocalRemote

        if not factory:
            self.view.error('Unknown dependency type {0}'.format(type))
            raise PullError()

        self._remote = factory(dependency=self.dependency)
        return self._remote

    def get_builder(self, install_dir: str, input_prefixes: Iterable[str]) -> Optional[Builder]:
        buildsystem = self.get_buildsystem()
        factory = None

        if buildsystem is BuildSystem.MAKEFILE:
            factory = MakefileBuilder
        elif buildsystem is BuildSystem.CMAKE:
            factory = CMakeBuilder
        elif buildsystem is BuildSystem.XCODE:
            factory = XcodeBuilder

        if not factory:
            self.view.error('Unknown build system')
            raise BuildError()

        caller = SubprocessCaller(self.view)

        return factory(
            buildfile_dir=self.get_buildfile_dir(),
            build_dir=self.get_build_dir(),
            install_dir=install_dir,
            prefix_paths=input_prefixes,
            dependency=self.dependency,
            options=self.options,
            caller=caller,
            view=self.view
        )

    def has_dewfile(self) -> bool:
        dewfile_path = os.path.join(self.get_source_dir(), 'dewfile.json')
        return os.path.isfile(dewfile_path)

    def get_dewfile(self) -> DewFile or None:
        dewfile_path = os.path.join(self.get_source_dir(), 'dewfile.json')
        if os.path.isfile(dewfile_path):
            return dew.dewfile.parse_dewfile_with_local_overlay(dewfile_path)
        else:
            return None

    def get_source_dir(self):
        return os.path.join(self.storage.get_sources_dir(), self.label)

    def get_buildfile_dir(self):
        buildfile_dir = self.dependency.buildfile_dir
        src_dir = self.get_source_dir()
        if buildfile_dir:
            return os.path.join(src_dir, buildfile_dir)
        return self.get_source_dir()

    def get_build_dir(self):
        return os.path.join(self.storage.get_builds_dir(), self.label)

    def get_buildsystem(self):
        """ Guesses the build system """
        src_path = self.get_buildfile_dir()
        if os.path.isfile(os.path.join(src_path, 'CMakeLists.txt')):
            return BuildSystem.CMAKE
        if os.path.isfile(os.path.join(src_path, 'Makefile')):
            return BuildSystem.MAKEFILE

        for path in os.listdir(src_path):
            if path.endswith('.xcodeproj'):
                return BuildSystem.XCODE

        return BuildSystem.UNKNOWN

    def install_fake_cmake_config(self):
        with open('', 'w') as f:
            f.write(
                'set(PACKAGE_FIND_NAME "{0}")'
                'set(PACKAGE_FIND_VERSION)'
            )

    def get_version(self) -> str:
        remote = self.get_remote()
        return f'{self.dependency.type}_{remote.get_version()}'
