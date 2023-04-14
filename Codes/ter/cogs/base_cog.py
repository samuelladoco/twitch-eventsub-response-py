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
        _token: str, _pu: PartialUser,
        _settings_base: dict[str, Any],_response_cms_base: list[list[Any]],
    ) -> None:
        print(f'      {self.name}')
        self.__token: str = _token
        self.__pu: PartialUser = _pu
        self.__settings_base: dict[str, Any] = _settings_base
        self.__response_cms_base: list[list[Any]] = _response_cms_base

    def get_settings_replaced(self,
        _replacements: dict[str, str],
    ) -> dict[str, Any]:
        return _replace_recursively_d(self.__settings_base, _replacements)

    def get_cm_units_replaced(self,
        _replacements: dict[str, str],
    ) -> list[TERCommandMessageUnit]:
        return [
            TERCommandMessageUnit(cm_base, _replacements, )
            for cm_base in self.__response_cms_base
        ]

    async def execute_cms(self,
        _channel: Channel, _cm_units: list[TERCommandMessageUnit],
    ) -> None:
        index: int = 0
        q: queue.Queue[TERCommandMessageUnit] = queue.Queue()
        for cm_unit in [_cm_unit for _cm_unit in _cm_units]:
            q.put(cm_unit)
        #
        #
        print(f'    Commands or messages')
        while q.empty() is False:
            # 送信前の待機(秒)
            index += 1
            cm_unit: TERCommandMessageUnit = q.get()
            print(
                f'      {index} (after {cm_unit.sleep_sec:>3} s.) = '
                + f'{cm_unit.cm_replaced} (+ {cm_unit.args_replaced}) ... ',
                end='', flush=True,
            )
            #
            await asyncio.sleep(cm_unit.sleep_sec)
            #
            #
            # (コマンド) /shoutout メッセージ送信先チャンネルにレイドをしたユーザー
            if cm_unit.cm_replaced == '/shoutout':
                channel_broadcaster_user: User = await _channel.user()
                try:
                    await self.__pu._http.post_shoutout(
                        self.__token,
                        str(channel_broadcaster_user.id),
                        str(self.__pu.id),
                        str(cm_unit.args_replaced[0])
                    )
                except HTTPException as e:
                    print(f'failed.')
                    print(f'        {e}')
                    num_retrials: int = (
                        1 if len(cm_unit.args_replaced) < 3
                        else int(cm_unit.args_replaced[2]) + 1
                    )
                    cm_base: list[Any] = [
                        125, cm_unit.cm_replaced, cm_unit.args_replaced[0],
                        f'(Retrial)', num_retrials,
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
        _cm_base: list[Any], _replacements: dict[str, str],
    ) -> None:
        self.__sleep_sec: int = int(_cm_base[0])
        #
        self.__cm_replaced: str = str(_cm_base[1])
        for (rk, rv) in _replacements.items():
            self.__cm_replaced = self.__cm_replaced.replace(rk, rv)
        #
        self.__args_replaced: list[Any] = _replace_recursively_l(
            [a for a in _cm_base[2:]], _replacements,
        )

    @property
    def sleep_sec(self) -> int:
        return self.__sleep_sec

    @property
    def cm_replaced(self) -> str:
        return self.__cm_replaced

    def extend_args_replaced(self, _args_to_add: list[Any]) -> None:
        self.__args_replaced.extend(_args_to_add)

    @property
    def args_replaced(self) -> list[Any]:
        return self.__args_replaced
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------


# Functions
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
def _replace_recursively_d(
    d_base: dict[str, Any], _replacements: dict[str, str],
) -> dict[str, Any]:
    d_replaced: dict[str, Any] = {}
    for k_vase, v_base in d_base.items():
        v_replaced: Any
        if isinstance(v_base, str) is True:
            v_replaced = v_base
            for (rk, rv) in _replacements.items():
                v_replaced = v_replaced.replace(rk, rv)
        elif isinstance(v_base, list) is True:
            v_replaced = _replace_recursively_l(v_base, _replacements, )
        elif isinstance(v_base, dict) is True:
            v_replaced = _replace_recursively_d(v_base, _replacements, )
        else:
            v_replaced = v_base
        d_replaced[k_vase.strip()] = v_replaced
    return d_replaced
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
def _replace_recursively_l(
    l_base: list[Any], _replacements: dict[str, str],
) -> list[Any]:
    l_replaced: list[Any] = []
    for e_base in l_base:
        e_replaced: Any
        if isinstance(e_base, str):
            e_replaced = e_base
            for (rk, rv) in _replacements.items():
                e_replaced = e_replaced.replace(rk, rv)
        elif isinstance(e_base, list) is True:
            e_replaced = _replace_recursively_l(e_base, _replacements, )
        elif isinstance(e_base, dict) is True:
            e_replaced = _replace_recursively_d(e_base, _replacements, )
        else:
            e_replaced = e_base
        l_replaced.append(e_replaced)
    return l_replaced
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
