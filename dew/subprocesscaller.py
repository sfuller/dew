import subprocess
from typing import List, Type, Optional, Dict

from dew.view import View


class SubprocessCallError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class SubprocessCaller(object):
    def __init__(self, view: View) -> None:
        self.view = view

    def call(self, args: List[str], cwd: str, error_exception: Type[Exception],
             env: Optional[Dict[str, str]] = None) -> None:
        self.view.verbose('Calling subprocess: "{0}", cwd: {1}'.format(repr(args), repr(cwd)))
        proc = subprocess.run(
            args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
            universal_newlines=True
        )

        self.view.verbose('Process output:\n{0}'.format(proc.stdout))
        if len(proc.stderr) > 0:
            self.view.error(proc.stderr)

        if proc.returncode is not 0:
            raise error_exception()
