import json
import os.path
import stat
import subprocess
import shutil
from enum import Enum

from dew.buildoptions import BuildOptions
from dew.dewfile import Dependency, DewFile, DewFileParser, Fix
from dew.exceptions import BuildError, PullError
from dew.storage import StorageController
from dew import git
from dew.view import View


class BuildSystem(Enum):
    UNKNOWN = 0
    CMAKE = 1
    MAKEFILE = 2
    XCODE = 3


class DependencyProcessor(object):
    def __init__(self, storage: StorageController, view: View, skip_download: bool):
        self.storage = storage
        self.dependency = None
        self.dewfile = None
        self.options = None
        self.view = view
        self.skip_download = skip_download

    def set_data(self, dependency: Dependency, dewfile: DewFile, options: BuildOptions):
        self.dependency = dependency
        self.dewfile = dewfile
        self.options = options

    def process(self):
        self.pull()
        self.build()

    def pull(self):
        type = self.dependency.type
        if type == 'git':
            self.pull_git()
        elif type == 'local':
            self.pull_local()
        else:
            self.view.error('Cannot pull, unknown dependency type {0}'.format(type))
            raise PullError()

        if self.dependency.execute_after_fetch:
            self.call([self.dependency.execute_after_fetch], cwd=self.get_src_dir())

    def build(self):
        buildsystem = self.get_buildsystem()
        if buildsystem is BuildSystem.MAKEFILE:
            self.build_makefile()
        elif buildsystem is BuildSystem.CMAKE:
            self.build_cmake()
        elif buildsystem is BuildSystem.XCODE:
            self.build_xcode()
        else:
            self.view.error('Cannot build, unkown build system')
            raise BuildError()

        self.apply_fixes()

    def has_dewfile(self) -> bool:
        dewfile_path = os.path.join(self.get_src_dir(), 'dewfile.json')
        return os.path.isfile(dewfile_path)

    def get_dewfile(self) -> DewFile or None:
        dewfile_path = os.path.join(self.get_src_dir(), 'dewfile.json')
        if os.path.isfile(dewfile_path):
            parser = DewFileParser()
            with open(dewfile_path) as f:
                data = json.load(f)
            parser.set_data(data)
            return parser.parse()
        else:
            return None

    def pull_git(self):
        if self.skip_download:
            return
        dest_dir = self.get_src_dir()
        git.update_repo(self.dependency.url, dest_dir, self.dependency.ref)

    def pull_local(self):
        dest_dir = self.get_src_dir()
        if os.path.exists(dest_dir):
            if os.path.isdir(dest_dir):
                def remove_readonly(func, path, excinfo):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                shutil.rmtree(dest_dir, onerror=remove_readonly)
            else:
                os.remove(dest_dir)
        shutil.copytree(self.dependency.url, dest_dir)

    def get_src_dir(self):
        return os.path.join(self.storage.get_sources_dir(), self.dependency.name)

    def get_buildfile_dir(self):
        buildfile_dir = self.dependency.buildfile_dir
        src_dir = self.get_src_dir()
        if buildfile_dir:
            return os.path.join(src_dir, buildfile_dir)
        return self.get_src_dir()

    def get_build_dir(self):
        return os.path.join(self.storage.get_builds_dir(), self.dependency.name)

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

    def build_cmake(self) -> None:
        buildfile_dir = self.get_buildfile_dir()
        build_dir = self.get_build_dir()
        install_dir = self.storage.get_install_dir()
        os.makedirs(build_dir, exist_ok=True)

        cmake_executable = self.options.cmake_executable
        if not cmake_executable:
            cmake_executable = 'cmake'

        args = [
            cmake_executable,
            '-G', self.options.cmake_generator,
            buildfile_dir,
            '-DCMAKE_INSTALL_PREFIX={0}'.format(install_dir),
            '-DCMAKE_PREFIX_PATH={0}'.format(install_dir),
            '-DCMAKE_BUILD_TYPE=Debug'
        ]
        args.extend(self.dependency.build_arguments)

        # Configure
        self.call(args, cwd=build_dir)

        # Build
        self.call(
            [cmake_executable, '--build', '.'],
            cwd=build_dir,
        )

        # Install
        self.call(
            [cmake_executable, '--build', '.', '--target', 'install'],
            cwd=build_dir
        )

    def build_makefile(self) -> None:
        self.view.error('Building makefile is not supported yet')
        raise BuildError()

    def build_xcode(self) -> None:
        build_dir = self.get_build_dir()
        os.makedirs(build_dir, exist_ok=True)

        # Figure out which xcodeproj path we are using
        xcodeproj_path = ''
        for path in os.listdir(os.path.join(self.get_buildfile_dir())):
            if path.endswith('.xcodeproj'):
                xcodeproj_path = os.path.join(self.get_buildfile_dir(), path)
                break

        if not xcodeproj_path:
            self.view.error('Cannot determine the xcodeproj to build with.')
            raise BuildError()

        self.call(
            [
                'xcodebuild', '-project', xcodeproj_path,
                'OBJROOT=' + os.path.join(build_dir, 'Intermediates'),
                'BUILD_DIR=' + os.path.join(build_dir, 'Products'),
                'SYMROOT=' + os.path.join(build_dir, 'Products'),
                'build'
            ],
            cwd=self.get_build_dir()
        )

    def call(self, args, cwd):
        self.view.verbose('Calling subprocess: "{0}", cwd: {1}'.format(repr(args), repr(cwd)))
        proc = subprocess.run(
            args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            universal_newlines=True
        )

        self.view.verbose('Process output:\n{0}'.format(proc.stdout))
        if len(proc.stderr) > 0:
            self.view.error(proc.stderr)

        if proc.returncode is not 0:
            raise BuildError()

    def install_fake_cmake_config(self):
        with open('', 'w') as f:
            f.write(
                'set(PACKAGE_FIND_NAME "{0}")'
                'set(PACKAGE_FIND_VERSION)'
            )

    def apply_fixes(self):
        for fix in self.dependency.fixes:
            self.apply_fix(fix)

    def apply_fix(self, fix: Fix):
        if fix.type == 'includeconfig':
            self.apply_includeconfig_fix(fix)

    def apply_includeconfig_fix(self, fix: Fix):
        include_path = fix.params['include_path']
        package_name = fix.params['package_name']
        config_file_path = os.path.join(
            self.storage.get_install_dir(), 'lib', 'cmake', package_name, '{0}Config.cmake'.format(package_name)
        )
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        with open(config_file_path, 'w') as f:
            f.writelines([
                'include(${{CMAKE_CURRENT_LIST_DIR}}/{0})'.format(include_path)
            ])
