import json
import os.path
import subprocess
import shutil
from enum import Enum, auto

from dew.buildoptions import BuildOptions
from dew.dewfile import Dependency, DewFile, DewFileParser
from dew.exceptions import BuildError, PullError
from dew.storage import StorageController
from dew import git
from dew.view import View


class BuildSystem(Enum):
    UNKNOWN = auto()
    CMAKE = auto()
    MAKEFILE = auto()


class DependencyProcessor(object):
    def __init__(self, storage: StorageController, view: View):
        self.storage = storage
        self.dependency = None
        self.dewfile = None
        self.options = None
        self.view = view

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

    def build(self):
        buildsystem = self.get_buildsystem()
        if buildsystem == BuildSystem.MAKEFILE:
            self.build_makefile()
        elif buildsystem == BuildSystem.CMAKE:
            self.build_cmake()
        else:
            self.view.error('Cannot build, unkown build system')
            raise BuildError()

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
        dest_dir = self.get_src_dir()
        git.clone_repo(self.dependency.url, dest_dir, self.dependency.ref)

    def pull_local(self):
        dest_dir = self.get_src_dir()
        if os.path.exists(dest_dir):
            if os.path.isdir(dest_dir):
                shutil.rmtree(dest_dir)
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
        return BuildSystem.UNKNOWN

    def build_cmake(self):
        buildfile_dir = self.get_buildfile_dir()
        build_dir = self.get_build_dir()
        install_dir = self.storage.get_install_dir()
        os.makedirs(build_dir, exist_ok=True)

        args = [
            'cmake',
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
            ['cmake', '--build', '.'],
            cwd=build_dir,
        )

        # Install
        self.call(
            ['cmake', '--build', '.', '--target', 'install'],
            cwd=build_dir
        )

    def build_makefile(self):
        self.view.error('Building makefile is not supported yet')
        raise BuildError()

    def call(self, args, cwd):
        self.view.verbose('Calling subprocess: "{0}", cwd: {1}'.format(repr(args), repr(cwd)))
        proc = subprocess.run(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              encoding='utf8')

        self.view.verbose('Process output:{0}{1}'.format(os.linesep, str(proc.stdout)))
        if len(proc.stderr) > 0:
            self.view.error(str(proc.stderr))

        if proc.returncode is not 0:
            raise BuildError()


    def install_fake_cmake_config(self):
        with open('', 'w') as f:
            f.write(
                'set(PACKAGE_FIND_NAME "{0}")'
                'set(PACKAGE_FIND_VERSION)'
            )