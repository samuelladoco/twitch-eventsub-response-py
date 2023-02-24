# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import Any
#
from twitchio import PartialUser
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
        print(
            f"    Message channel user name = "
            + f"{str(self.__j['messageChannel']['userName'])}"
        )
        print(f'    Bot token length = {len(self.__token)}')
        super().__init__(  # type: ignore
            token=self.__token,
            prefix=self.__prefix,
            initial_channels=[str(self.__j['messageChannel']['userName'])],
        )
        print(f'  done.')
        print(f'')

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
            TERRaidCog(self, self.__token, self.__pu, self.__j['responses']['/raid'])
        )
        # ToDo: ★
        #
        for c in self.cogs.keys():
            print(f'      {c}')
        print(f'  done.')
        print(f'')

    @commands.command(name='test', )
    async def show_alive(self, ctx: commands.Context):
        print(f"  Testing bot (v{self.__j['ver_no']}) ...")
        print(f'    Channel name = {ctx.channel.name}')
        assert self.__pu is not None, f'Bot user is not created.'
        print(f'    Bot user ID = {self.__pu.id}')
        print(f'    Bot user name = {self.__pu.name}')
        print(f'    Bot cogs')
        for c_name in self.cogs.keys():
            print(f'      {c_name}')
        #
        print(f'    Bot commands')
        for c_name in self.commands.keys():
            print(f'      {self.__prefix}{str(c_name)}')
        #
        await ctx.send(f'/me {self.nick} bot for {self.__prefix} is alive.')
        print(f'  done.')
        print(f'')
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
