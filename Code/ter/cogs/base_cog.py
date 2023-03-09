# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import asyncio
import queue
from typing import Any
#
from twitchio import Channel, HTTPException, PartialUser, User
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
        _cm_bases: list[list[Any]],
    ) -> None:
        self.bot: commands.Bot = bot
        self.__token: str = _token
        self.__pu: PartialUser = _pu
        self.__cm_bases: list[list[Any]] = _cm_bases

    def get_replaced_cm_units(self,
        _replacements: dict[str, str],
    ) -> list[TERCommandMessageUnit]:
        return [
            TERCommandMessageUnit(cm_base, _replacements, )
            for cm_base in self.__cm_bases
        ]

    async def execute_cms(self,
        _channel: Channel,
        _cm_units: list[TERCommandMessageUnit],
    ) -> None:
        index: int = 0
        q: queue.Queue[TERCommandMessageUnit] = queue.Queue()
        for cm_unit in [_cm_unit for _cm_unit in _cm_units]:
            q.put(cm_unit)
        #
        print(f'    Commands or messages')
        while q.empty() is False:
            index += 1
            cm_unit: TERCommandMessageUnit = q.get()
            print(
                f'      {index} (after {cm_unit.sleep_sec:>3} s.) = '
                + f'{[cm_unit.cm_replaced] + cm_unit.args_replaced} ... ',
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
                    print(f'failed.')
                    print(f'        {e}')
                    cm_base: list[Any] = [
                        125, cm_unit.cm_replaced, cm_unit.args_replaced[0],
                        '(Retry)',
                    ]
                    q.put(TERCommandMessageUnit(cm_base, {}, ))
                    continue
            #
            # ToDo: ★ (コマンド) 別のコマンドにも対応する場合は、ここに実装する
            # elif cm_unit.cm_replaced == '/????':
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
        _cm_base: list[Any],
        _replacements: dict[str, str],
    ) -> None:
        self.__sleep_sec: int = int(_cm_base[0])
        #
        self.__cm_replaced: str = str(_cm_base[1])
        for (rk, rv) in _replacements.items():
            self.__cm_replaced = self.__cm_replaced.replace(rk, rv)
        #
        self.__args_replaced: list[str] = [str(a) for a in _cm_base[2:]]
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
