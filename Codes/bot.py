# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import Any
#
from twitchio import PartialUser
from twitchio.client import Channel
from twitchio.ext import commands
#
from cogs import TERBaseCog, TERRaidCog
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class TERBot(commands.Bot):

    def __init__(self, _j: dict[str, Any], ) -> None:
        print(f'  Initializing bot ...')
        #
        self.__j: dict[str, Any] = _j
        self.__token: str = str(self.__j['bot']['oAuthAccessToken'])
        self.__prefix = '<ter>_'
        print(
            f"    Bot token length = {len(self.__token)}"
        )
        print(
            f"    Test command = {self.__prefix}test"
        )
        print(
            f"    Message channel = " +
            f"{str(self.__j['messageChannel']['userName'])}"
        )
        super().__init__(
            token=self.__token,
            prefix=self.__prefix,
            initial_channels=[str(self.__j['messageChannel']['userName'])],
        )
        #
        self.__pu: PartialUser | None = None
        self.__cogs: list[TERBaseCog] = []
        #
        print(f'  done.')
        print(f'')

    async def event_channel_joined(self, channel: Channel):
        print(f'  Joining channel ...')
        print(f'    Channel name = {channel.name}')
        #
        name_color: str = str(self.__j['bot']['nameColor'])
        if name_color != 'DoNotChange':
            print(f'    Bot name color = {name_color}')
            #
            await channel.send(f"/color {name_color}")
        #
        await channel.send(
            f'/me {self.nick} bot for {self.__prefix} has joined.'
        )
        print(f'  done.')
        print(f'')

    async def event_ready(self) -> None:
        print(f'  Making bot ready ...')
        self.__pu = self.create_user(self.user_id, self.nick)
        print(f'    Bot user ID = {self.__pu.id}')
        print(f'    Bot user name = {self.__pu.name}')
        print(f'  done.')
        print(f'')
        #
        print(f'  Registering Cogs ...')
        self.__cogs.extend([
            TERRaidCog(
                self.__token,
                list(self.__j['responses']['raid']['commands']),
                list(self.__j['responses']['raid']['messages']),
                self.__pu,
            ),
            # ToDo: ★ 別のCogにも対応する場合は、ここに実装する
        ])
        for cog in self.__cogs:
            self.add_cog(cog)
        print(f"    Cogs = [{', '.join([cog.name for cog in self.__cogs])}]")
        print(f'  done.')
        print(f'')

    @commands.command()
    async def test(self, ctx: commands.Context):
        print(f'  Testing bot ...')
        print(f'    Channel name = {ctx.channel.name}')
        print(f'    Bot user ID = {self.user_id}')
        print(f'    Bot user name = {self.nick}')
        print(f"    Cogs = [{', '.join([cog.name for cog in self.__cogs])}]")
        #
        await ctx.send(f'/me {self.nick} bot for {self.__prefix} is alive.')
        print(f'  done.')
        print(f'')
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
