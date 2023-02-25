# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import os
import pathlib
import sys
from typing import Any
#
import ter
import util
# -----------------------------------------------------------------------------


# Version No.
# -----------------------------------------------------------------------------
ver_no: str = '0.4'
# -----------------------------------------------------------------------------


# Main
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
def main() -> int:
    n: str = f'--- Twitch EventSub Response Bot (v{ver_no}) ---'
    print(f'{n}')
    #
    print(f'[Preprocess]')
    j_file: pathlib.Path = (
        pathlib.Path(
            rf'{os.path.abspath(os.path.dirname(sys.argv[0]))}'
        ).joinpath('config.json5')
    )
    print(f'  JSON5 file path = {j_file}')
    print(f'    parsing this file ... ', end='', )
    j_obj: dict[str, Any] = util.JSON5Reader.open_and_loads(j_file)
    j_obj['ver_no'] = ver_no
    print(f'done.')
    print(f'')
    #
    print(f'[Activation of Bot]')
    b: ter.TERBot = ter.TERBot(j_obj)
    #
    print(f'[Run of Bot]')
    b.run()
    #
    print(f'[Postprocess] (nothing)')
    print(f'')
    print(f'-' * len(n))
    return b.return_code
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
if __name__ == '__main__':
    return_code: int = main()
    sys.exit(return_code)
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
