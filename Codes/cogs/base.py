# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import asyncio
from typing import Any, NamedTuple
#
from twitchio import PartialUser
from twitchio.client import Channel
from twitchio.ext import commands
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class TERBaseCog(commands.Cog):

    def __init__(self,
        _token: str,
        _commands: list[Any],
        _messages: list[Any],
        _pu: PartialUser,
    ) -> None:
        self.__token: str = _token
        self.__cs_pre_replacing: list[TERResponseCM] = [
            TERResponseCM(c[0], c[1], c[2:], True) for c in _commands
        ]
        self.__ms_pre_replacing: list[TERResponseCM] = [
            TERResponseCM(m[0], m[1], [m[2]], False) for m in _messages
        ]
        self.__pu: PartialUser = _pu

    def replace_double_curly_brackets(self,
        _replacements: dict[str, str],
    ) -> tuple[list[TERResponseCM], list[TERResponseCM]]:
        cs_post_replacing: list[TERResponseCM] = []
        for c_pre_replacing in self.__cs_pre_replacing:
            command: list[str] = []
            for c_arg_pre_replacing in c_pre_replacing.command:
                c_arg: str = c_arg_pre_replacing
                for (rk, rv) in _replacements.items():
                    c_arg = c_arg.replace(rk, rv)
                command.append(c_arg)
            cs_post_replacing.append(
                TERResponseCM(
                    c_pre_replacing.order,
                    c_pre_replacing.sleep_sec,
                    command,
                    True,
                )
            )
        print(f"    Number of commands = {len(cs_post_replacing)}")
        #
        ms_post_replacing: list[TERResponseCM] = []
        for m_pre_replacing in self.__ms_pre_replacing:
            message: str = m_pre_replacing.message
            for (rk, rv) in _replacements.items():
                message = message.replace(rk, rv)
            ms_post_replacing.append(
                TERResponseCM(
                    m_pre_replacing.order,
                    m_pre_replacing.sleep_sec,
                    [message],
                    False,
                )
            )
        print(f"    Number of messages = {len(ms_post_replacing)}")
        return (cs_post_replacing, ms_post_replacing)

    async def execute_commands_and_send_messages(self,
        _channel: Channel,
        _cs_post_replacing: list[TERResponseCM],
        _ms_post_replacing: list[TERResponseCM],
    ) -> None:
        cms: list[TERResponseCM] = []
        cms.extend(_cs_post_replacing)
        cms.extend(_ms_post_replacing)
        cms.sort(key=lambda x: x.order)
        #
        print(f'    Commands or messages')
        for index, cm in enumerate(cms):
            print(
                f'      No. {index + 1} (after {cm.sleep_sec:>2} s.) = ',
                end=''
            )
            #
            await asyncio.sleep(cm.sleep_sec)
            #
            # コマンドまたはメッセージ
            #   コマンド
            if cm.is_command:
                print(f'{cm.command} ... ', end='')
                #
                # /shoutout メッセージ送信先チャンネルにレイドをしたユーザー
                if cm.command[0] == 'shoutout':
                    await self.__pu.shoutout(
                        self.__token, int(cm.command[1]), self.__pu.id
                    )
                #
                # ToDo: ★ 別のコマンドにも対応する場合は、ここに実装する
                # elif cm.command[0] == '???':
                #     pass
                else:
                    print(f'ignored.')
                    continue
            #   メッセージ
            else:
                print(f'{cm.message} ... ', end='')
                #
                await _channel.send(cm.message)
            print(f'done.')
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class TERResponseCM(NamedTuple):
    order: int
    sleep_sec: int
    command_or_message: list[str]
    is_command: bool

    @property
    def command(self) -> list[str]:
        assert self.is_command is True, f'{self} はメッセージです'
        return self.command_or_message

    @property
    def message(self) -> str:
        assert self.is_command is False, f'{self} はコマンドです'
        return self.command_or_message[0]
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
