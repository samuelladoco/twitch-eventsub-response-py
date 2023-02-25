# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import Any
#
from twitchio import Chatter, PartialUser
from twitchio.channel import Channel
from twitchio.ext import commands
#
from .cogs import *
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class TERBot(commands.Bot):

    def __init__(self, _j: dict[str, Any], ) -> None:
        print(f'  Initializing bot ...')
        self.__j: dict[str, Any] = _j
        self.__token: str = str(self.__j['bot']['oAuthAccessToken'])
        self.__prefix = '<ter>_'
        self.__pu: PartialUser | None = None
        self.__return_code: int = -1
        #
        broadcaster_user_name: str = str(
            self.__j['messageChannel']['broadcasterUserName']
        )
        print(f"    Message channel user name = {broadcaster_user_name}")
        print(f'    Bot token length = {len(self.__token)}')
        super().__init__(  # type: ignore
            token=self.__token,
            prefix=self.__prefix,
            initial_channels=[
                broadcaster_user_name,
            ],
        )
        print(f'  done.')
        print(f'')

    @property
    def return_code(self) -> int:
        return self.__return_code

    async def event_channel_joined(self, channel: Channel):
        print(f'  Joining channel ...')
        print(f'    Channel name = {channel.name}')
        #
        name_color: str = str(self.__j['bot']['nameColor'])
        if name_color != 'DoNotChange':
            print(f'    Setting bot name color = {name_color} ... ', end='', )
            #
            await channel.send(f'/color {name_color}')
            print(f'done.')
        #
        await channel.send(
            f'/me {self.nick} bot for {self.__prefix} has joined.'
        )
        print(f'  done.')
        print(f'')

    async def event_ready(self) -> None:
        print(f'  Making bot ready ...')
        assert self.user_id is not None, f'Bot user ID is unknown.'
        assert self.nick is not None, f'Bot user ID is unknown.'
        self.__pu = self.create_user(self.user_id, self.nick)
        print(f'    Bot user ID = {self.__pu.id}')
        print(f'    Bot user name = {self.__pu.name}')
        print(f'    Bot commands')
        for c_name in self.commands.keys():
            print(f'      {self.__prefix}{str(c_name)}')
        #
        print(f'    Bot cogs')
        self.add_cog(
            TERRaidCog(
                self, self.__token, self.__pu, self.__j['responses']['/raid'],
            )
        )
        # ToDo: ★ 別のCogを開発した場合は、登録処理をここに実装する
        #
        for c in self.cogs.keys():
            print(f'      {c}')
        print(f'  done.')
        print(f'')

    @commands.command(name='test', )
    async def __test(self, ctx: commands.Context):
        print(f"  Testing bot (v{self.__j['ver_no']}) ...")
        print(f'    Channel name = {ctx.channel.name}')
        assert self.__pu is not None, f'Bot user is not created.'
        print(f'    Bot user ID = {self.__pu.id}')
        print(f'    Bot user name = {self.__pu.name}')
        print(f'    Bot commands')
        for c_name in self.commands.keys():
            print(f'      {self.__prefix}{str(c_name)}')
        #
        print(f'    Bot cogs')
        for c_name in self.cogs.keys():
            print(f'      {c_name}')
        #
        await ctx.send(f'/me {self.nick} bot for {self.__prefix} is alive.')
        print(f'  done.')
        print(f'')

    @commands.command(name='kill', )
    async def __kill(self, ctx: commands.Context):
        if self.__is_by_channel_broadcaster_or_myself(ctx) is True:
            print(f'  Killing bot ... ')
            self.loop.stop()
            #
            await ctx.send(
                f'/me {self.nick} bot for {self.__prefix} has stopped.'
            )
            #
            is_valid_return_code: bool = False
            return_code_str: str = str(
                ctx.message.content
            ).strip().removeprefix(f'{self.__prefix}kill').strip()
            if len(return_code_str) <= 3 and return_code_str.isdecimal() is True:
                return_code_int: int = int(return_code_str)
                if 0 <= return_code_int <= 255:
                    self.__return_code = int(return_code_int)
                    is_valid_return_code = True
                else:
                    self.__return_code = 0
                    is_valid_return_code = False
            else:
                self.__return_code = 0
                is_valid_return_code = (
                    True if len(return_code_str) == 0 else False
                )
            print(f'    Return code = {self.__return_code}')
            if is_valid_return_code is False:
                print(f'      * Invalid return code input')
            print(f'  done.')
            print(f'')

    def __is_by_channel_broadcaster_or_myself(self,
        ctx: commands.Context
    ) -> bool:
        if type(ctx.author) is Chatter:
            if ctx.author.is_broadcaster is True:
                return True
            elif ctx.author.id == str(self.user_id):
                return True
            else:
                return False
        else:
            return False
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
