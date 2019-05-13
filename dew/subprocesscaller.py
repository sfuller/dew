import subprocess, os
from typing import List, Type, Optional, Dict

from dew.view import View


class SubprocessCallError(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class SubprocessCaller(object):
    def __init__(self, view: View, *, redirect_output=True) -> None:
        self.view = view
        self.redirect_output = redirect_output

    def call(self,
             args: List[str],
             cwd: str,
             error_exception: Type[Exception],
             env: Optional[Dict[str, str]] = None
             ) -> None:
        if env is not None:
            merged_env = dict(os.environ)
            merged_env.update(env)
        else:
            merged_env = os.environ
        self.view.verbose('Calling subprocess: "{0}", cwd: {1}'.format(repr(args), repr(cwd)))

        output_file = subprocess.PIPE
        if not self.redirect_output:
            output_file = None

        proc = subprocess.run(
            args, cwd=cwd, stdout=output_file, stderr=output_file, env=merged_env,
            universal_newlines=True
        )

        self.view.verbose(f'Process output:\n{proc.stdout}')
        self.view.verbose(f'Process stderr:\n{proc.stderr}')

        if proc.returncode is not 0:
            if len(proc.stderr) > 0:
                self.view.error(proc.stderr)
            raise error_exception()
