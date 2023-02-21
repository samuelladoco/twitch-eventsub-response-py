# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import os
import pathlib
import sys
from typing import Any
#
from bot import TERBot
from util import JSON5Reader
# -----------------------------------------------------------------------------


# Main
# -----------------------------------------------------------------------------
print(f'--- Twitch EventSub Response Bot (v0.1) ---')
print(f'')
#
print(f'[Preprocess]')
j_file: pathlib.Path = (
    pathlib.Path(
        rf'{os.path.abspath(os.path.dirname(sys.argv[0]))}'
    ).joinpath('config.json5')
)
print(f'  JSON5 file path = {j_file}')
print(f'    parsing this file ... ', end='')
j_obj: dict[str, Any] = JSON5Reader.open_and_loads(j_file)
print(f'done.')
print(f'')
#
print(f'[Activation of Bot]')
b: TERBot = TERBot(j_obj)
#
print(f'[Running of Bot]')
b.run()
#
print(f'[Postprocess]')
print(f'')
print(f'-------------------------------------------')
# -----------------------------------------------------------------------------
