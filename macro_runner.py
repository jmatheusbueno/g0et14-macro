import threading
import time
from collections.abc import Callable

from macro_models import MacroItem


class MacroRunner:
    def __init__(self, action_resolver: Callable[[MacroItem], Callable[[], None]]) -> None:
        self._action_resolver = action_resolver
        self._worker_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    @property
    def is_running(self) -> bool:
        return bool(self._worker_thread and self._worker_thread.is_alive())

    def start(self, macros: list[MacroItem], global_delay: float) -> None:
        if self.is_running:
            return

        global_start_at = time.monotonic() + global_delay
        schedule = [
            {
                "action": self._action_resolver(item),
                "interval": item.interval,
                "next_run": global_start_at + item.start_delay,
            }
            for item in macros
        ]

        self._stop_event.clear()
        self._worker_thread = threading.Thread(
            target=self._run_loop,
            args=(schedule,),
            daemon=True,
        )
        self._worker_thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _run_loop(self, schedule: list[dict]) -> None:
        while not self._stop_event.is_set():
            now = time.monotonic()
            next_due = None

            for slot in schedule:
                if now >= slot["next_run"]:
                    slot["action"]()
                    slot["next_run"] = now + slot["interval"]

                if next_due is None or slot["next_run"] < next_due:
                    next_due = slot["next_run"]

            if next_due is None:
                if self._stop_event.wait(0.2):
                    break
                continue

            wait_time = max(0.05, next_due - time.monotonic())
            if self._stop_event.wait(wait_time):
                break
