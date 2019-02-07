

class Remote(object):
    def pull(self) -> None:
        pass

    def get_latest_ref(self) -> str:
        pass

    def get_current_ref(self) -> str:
        pass

    def get_current_head(self) -> str:
        pass

    def has_pending_changes(self) -> bool:
        pass

    def get_source_dir(self) -> str:
        pass

