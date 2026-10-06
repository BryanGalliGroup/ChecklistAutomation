from datetime import datetime
from typing import Callable


class Logger:
    def __init__(self, callback: Callable[[str], None] | None = None):
        self.callback = callback

    def _log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        if self.callback:
            self.callback(formatted_message)

    def info(self, message: str) -> None:
        self._log(message)

    def success(self, message: str) -> None:
        self._log(f"✓ {message}")

    def warning(self, message: str) -> None:
        self._log(f"⚠ {message}")

    def error(self, message: str) -> None:
        self._log(f"✗ {message}")