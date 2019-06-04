import fasteners, threading
from dew.impl import CommandData

class LockFile(fasteners.InterProcessLock):
    def __init__(self, path: str, data: CommandData):
        self.data = data
        super().__init__(path)

    def __enter__(self):
        gotten = super().acquire(blocking=False)
        if not gotten:
            self.data.view.info("Waiting for another dew to complete."
                                " Press Ctrl-C to abort.")
            gotten = super().acquire()
            if not gotten:
                # This shouldn't happen, but just incase...
                raise threading.ThreadError("Unable to acquire a file lock"
                                            " on `%s` (when used as a"
                                            " context manager)" % self.path)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().release()
