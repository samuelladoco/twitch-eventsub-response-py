# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import asyncio
from typing import Any
#
from twitchio import PartialUser, User
from twitchio.channel import Channel
from twitchio.errors import HTTPException
from twitchio.ext import commands
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class TERBaseCog(commands.Cog):

    def __init__(self,
        bot: commands.Bot,
        _token: str,
        _pu: PartialUser,
        _cm_units: list[list[Any]],
    ) -> None:
        self.bot: commands.Bot = bot
        self.__token: str = _token
        self.__pu: PartialUser = _pu
        self.__cm_units: list[list[Any]] = _cm_units

    def get_replaced_cm_units(self,
        _replacements: dict[str, str],
    ) -> list[TERCommandMessageUnit]:
        return [
            TERCommandMessageUnit(cm_unit, _replacements, )
            for cm_unit in self.__cm_units
        ]

    async def execute_cms(self,
        _channel: Channel,
        cm_units: list[TERCommandMessageUnit],
    ) -> None:
        print(f'    Commands or messages')
        for index, cm_unit in enumerate(cm_units):
            cm_plus_args: list[str] = [cm_unit.cm_replaced]
            cm_plus_args.extend(cm_unit.args_replaced)
            print(
                f'      No. {index + 1} (after {cm_unit.sleep_sec:>2} s.) = '
                + f'{cm_plus_args} ... ',
                end=''
            )
            #
            await asyncio.sleep(cm_unit.sleep_sec)
            #
            # (コマンド) /shoutout メッセージ送信先チャンネルにレイドをしたユーザー
            if cm_unit.cm_replaced == '/shoutout':
                channel_broadcaster_user: User = await _channel.user()
                try:
                    await self.__pu._http.post_shoutout(
                        self.__token,
                        str(channel_broadcaster_user.id),
                        str(self.__pu.id),
                        cm_unit.args_replaced[0]
                    )
                except HTTPException as e:
                    # ToDo: ★ マルチスレッド化して1分後にリトライ
                    print(f'failed.')
                    print(f'        {e}')
                    continue
            #
            # ToDo: ★ (コマンド) 別のコマンドにも対応する場合は、ここに実装する
            # elif cm_unit.cm_replaced == '/???':
            #     pass
            #
            # (メッセージ)
            else:
                await _channel.send(cm_unit.cm_replaced)
            #
            print(f'done.')
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class TERCommandMessageUnit:

    def __init__(self,
        _cm_unit: list[Any],
        _replacements: dict[str, str],
    ) -> None:
        self.__sleep_sec: int = int(_cm_unit[0])
        #
        self.__cm_replaced: str = str(_cm_unit[1])
        for (rk, rv) in _replacements.items():
            self.__cm_replaced = self.__cm_replaced.replace(rk, rv)
        #
        self.__args_replaced: list[str] = [str(a) for a in _cm_unit[2:]]
        for (rk, rv) in _replacements.items():
            self.__args_replaced = [
                arg_temp.replace(rk, rv) for arg_temp in self.__args_replaced
            ]

    @property
    def sleep_sec(self) -> int:
        return self.__sleep_sec

    @property
    def cm_replaced(self) -> str:
        return self.__cm_replaced

    def extend_args_replaced(self, _args_to_add: list[str]) -> None:
        self.__args_replaced.extend(_args_to_add)

    @property
    def args_replaced(self) -> list[str]:
        return self.__args_replaced
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
