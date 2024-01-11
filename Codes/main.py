# Import
# -----------------------------------------------------------------------------
from __future__ import annotations

import asyncio
import os
import pathlib
import signal
import sys
import time
from typing import Any

import ter
import util
import window

# Constants
# -----------------------------------------------------------------------------
ver_no: str = ter.__version__.casefold().strip()
uses_tkinter_window: bool = True
return_code_for_restrt: int = 3
sleep_before_restart_s: int = 4


# Main
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
def main(
    _uses_tkinter_window: bool,
) -> int:
    if (
        _uses_tkinter_window is True
        and window.TkinterConsoleWindow.is_aleady_opened() is False
    ):
        window.TkinterConsoleWindow.lets_thread_close_window = False
        asyncio.new_event_loop().run_in_executor(
            None, window.TkinterConsoleWindow.open, ver_no
        )
        while window.TkinterConsoleWindow.is_aleady_opened() is False:
            time.sleep(1.0 / 64.0)
        sys.stdout = window.TkinterConsoleWindow  # type: ignore
        sys.stderr = window.TkinterConsoleWindow  # type: ignore
    #
    title: str = (
        f"-" * 20 + f" Twitch EventSub Response Bot (v{ver_no}) " + f"-" * 20
    )
    print(f"{title}")
    #
    print(f"[Preprocess]")
    base_dir: pathlib.Path = pathlib.Path(
        rf"{os.path.abspath(os.path.dirname(sys.argv[0]))}"
    )
    #
    cj_file: pathlib.Path = base_dir.joinpath("config.json5")
    print(f"  JSON5 file path = {cj_file}")
    print(
        f"    parsing this file ... ",
        end="",
    )
    cj_obj: dict[str, Any] = util.JSON5Reader.open_and_load(cj_file)
    cj_obj["verNo"] = ver_no
    cj_obj["returnCodeForRestrt"] = return_code_for_restrt
    print(f"done.")
    print(f"")
    #
    print(f"[Activation of Bot]")
    b: ter.TERBot = ter.TERBot(cj_obj)

    def __post_process(
        _b: ter.TERBot,
        _title: str,
    ) -> None:
        signal.signal(signal.SIGBREAK, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        #
        print(f"[Postprocess]")
        print(
            f"  Return code = {_b.return_code}",
            end="",
        )
        if _b.return_code == return_code_for_restrt:
            print(f" (Restart)")
        else:
            print(f"")
        _b.kill_bouyomi_process()
        print(f"")
        print(f"-" * len(_title))
        #
        if _b.return_code != return_code_for_restrt:
            window.TkinterConsoleWindow.lets_thread_close_window = True
        #
        signal.signal(signal.SIGBREAK, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)

    print(f"[Run of Bot]")
    signal.signal(
        signal.SIGBREAK,
        lambda *_: __post_process(
            b,
            title,
        ),
    )
    signal.signal(
        signal.SIGTERM,
        lambda *_: __post_process(
            b,
            title,
        ),
    )
    try:
        if _uses_tkinter_window is True:
            window.TkinterConsoleWindow.add_func_kill_bot(
                b.kill_self_without_print,
            )
        b.run()
    finally:
        __post_process(
            b,
            title,
        )
    return b.return_code


# ----------------------------------------------------------------------
if __name__ == "__main__":
    return_code_main: int = 0
    #
    while True:
        asyncio.set_event_loop(asyncio.new_event_loop())
        return_code_main = main(uses_tkinter_window)
        #
        if return_code_main == return_code_for_restrt:
            print(f"")
            print(f"Restart after {sleep_before_restart_s} s.")
            print(f"")
            time.sleep(float(sleep_before_restart_s))
        else:
            break
    #
    sys.exit(return_code_main)
