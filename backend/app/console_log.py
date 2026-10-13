"""Plain, human-readable step logging printed straight to the terminal
running `uvicorn`, so the pipeline's progress can be shown live in a console
window during a demo (as opposed to anything rendered in the website UI).
"""
from __future__ import annotations

import time
from datetime import datetime


def _ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def banner(text: str) -> None:
    line = "=" * 70
    print(f"\n{line}\n[{_ts()}] {text}\n{line}", flush=True)


def step(label: str, detail: str = "") -> None:
    msg = f"[{_ts()}]   {label}"
    if detail:
        msg += f" - {detail}"
    print(msg, flush=True)


def sub(text: str) -> None:
    print(f"[{_ts()}]        {text}", flush=True)


class Timer:
    """Use as `with Timer() as t: ...` then read `t.elapsed` in seconds."""

    def __enter__(self) -> "Timer":
        self._start = time.monotonic()
        return self

    def __exit__(self, *exc) -> None:
        self.elapsed = time.monotonic() - self._start
