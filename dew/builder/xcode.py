import os

from dew.builder import Builder
from dew.projectproperties import ProjectProperties
from dew.dewfile import Dependency
from dew.exceptions import BuildError
from dew.subprocesscaller import SubprocessCaller
from dew.view import View
from dew.storage import BuildType

XCODE_BUILD_TYPES = {BuildType.Debug:'Debug', BuildType.Release:'Release'}

class XcodeBuilder(Builder):
    def __init__(self, buildfile_dir: str, build_dir: str, install_dir: str, build_type: BuildType,
                 dependency: Dependency, options: ProjectProperties, caller: SubprocessCaller, view: View) -> None:
        self.buildfile_dir = buildfile_dir
        self.build_dir = build_dir
        self.install_dir = install_dir
        self.build_type = build_type
        self.dependency = dependency
        self.options = options
        self.caller = caller
        self.view = view

    def build(self) -> None:
        build_dir = self.build_dir
        os.makedirs(build_dir, exist_ok=True)

        # Figure out which xcodeproj path we are using
        xcodeproj_path = ''
        for path in os.listdir(os.path.join(self.buildfile_dir)):
            if path.endswith('.xcodeproj'):
                xcodeproj_path = os.path.join(self.buildfile_dir, path)
                break

        if not xcodeproj_path:
            self.view.error('Cannot determine the xcodeproj to build with.')
            raise BuildError()

        self.caller.call(
            [
                'xcodebuild', '-project', xcodeproj_path,
                '-configuration', XCODE_BUILD_TYPES[self.build_type],
                'OBJROOT=' + os.path.join(build_dir, 'Intermediates'),
                'BUILD_DIR=' + os.path.join(build_dir, 'Products'),
                'SYMROOT=' + os.path.join(build_dir, 'Products'),
                'build'
            ],
            cwd=self.build_dir
        )
