

class DewError(Exception):
    pass


class PullError(DewError):
    pass


class BuildError(DewError):
    pass


class DewfileError(DewError):
    def __init__(self, file_path: str, inner_tb) -> None:
        self.file_path = file_path
        self.inner_tb = inner_tb
        super().__init__()
