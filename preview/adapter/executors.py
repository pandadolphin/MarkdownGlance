import sys
from concurrent.futures import ThreadPoolExecutor


class OwnedExecutors:
    def __init__(self) -> None:
        self.render = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="mdglance-render"
        )
        self.network = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="mdglance-net"
        )

    def shutdown(self) -> None:
        kwargs = {"wait": False}
        if sys.version_info >= (3, 9):
            kwargs["cancel_futures"] = True
        self.render.shutdown(**kwargs)
        self.network.shutdown(**kwargs)
