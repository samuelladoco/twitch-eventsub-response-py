# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import os
import pathlib
import signal
import sys
from typing import Any
#
import ter
import util
# -----------------------------------------------------------------------------


# Version No.
# -----------------------------------------------------------------------------
ver_no: str = ter.__version__.casefold().strip()
# -----------------------------------------------------------------------------


# Main
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
def main() -> None:
    n: str = f'--- Twitch EventSub Response Bot (v{ver_no}) ---'
    print(f'{n}')
    #
    print(f'[Preprocess]')
    base_dir: pathlib.Path = pathlib.Path(
        rf'{os.path.abspath(os.path.dirname(sys.argv[0]))}'
    )
    rt_file: pathlib.Path = base_dir.joinpath('restart-flag.txt')
    rt_file.unlink(missing_ok=True)
    #
    cj_file: pathlib.Path = base_dir.joinpath('config.json5')
    print(f'  JSON5 file path = {cj_file}')
    print(f'    parsing this file ... ', end='', )
    cj_obj: dict[str, Any] = util.JSON5Reader.open_and_load(cj_file)
    cj_obj['verNo'] = ver_no
    print(f'done.')
    print(f'')
    #
    print(f'[Activation of Bot]')
    b: ter.TERBot = ter.TERBot(cj_obj)
    #
    def __post_process() -> None:
        signal.signal(signal.SIGBREAK, signal.SIG_IGN)
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        #
        print(f'[Postprocess]')
        print(f'  Return code = {b.return_code}')
        b.kill_bouyomi_process()
        if b.return_code == 3:
            rt_file.touch()
        print(f'')
        print(f'-' * len(n))
        #
        signal.signal(signal.SIGBREAK, signal.SIG_DFL)
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        sys.exit(b.return_code)
    #
    print(f'[Run of Bot]')
    signal.signal(signal.SIGBREAK, lambda *_: __post_process())
    signal.signal(signal.SIGTERM, lambda *_: __post_process())
    try:
        b.run()
    finally:
        __post_process()
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
if __name__ == '__main__':
    main()
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
