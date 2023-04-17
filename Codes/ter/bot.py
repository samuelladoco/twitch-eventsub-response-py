# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import Any
#
from twitchio import Channel, Chatter, PartialUser
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
        self.__token: str = str(self.__j['bot']['oAuthAccessToken']).strip()
        self.__prefix: str = '<ter>_'
        self.__return_code: int = 1
        #
        broadcaster_user_name: str = str(
            self.__j['messageChannel']['broadcasterUserName']
        ).casefold().strip()
        print(f'    Message channel user name = {broadcaster_user_name}')
        print(f'    Bot token length = {len(self.__token)}')
        super().__init__(  # type: ignore
            self.__token,
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
        print(f'  done.')
        print(f'')
        #
        await channel.send(f'/me bot for {self.__prefix} has joined.')

    async def event_ready(self) -> None:
        print(f'  Making bot ready ...')
        assert self.user_id is not None, f'Bot user ID is unknown.'
        print(f'    Bot user ID = {self.user_id}')
        assert self.nick is not None, f'Bot user name is unknown.'
        print(f'    Bot user name = {self.nick}')
        #
        print(f'    Bot commands')
        for c_name in self.commands.keys():
            print(f'      {self.__prefix}{c_name}')
        #
        print(f'    Bot cogs')
        pu: PartialUser = self.create_user(self.user_id, self.nick)
        self.add_cog(
            TERRaidCog(
                self.__token, pu, {}, self.__j['responses']['/raid'],
            )
        )
        self.add_cog(
            TERBouyomiCog(
                self.__token, pu, self.__j['bouyomiChan'], [], self.__prefix,
            )
        )
        self.add_cog(
            TERTransCog(
                self.__token, pu, self.__j['translation'], [], self.__prefix,
            )
        )
        #
        # ToDo: ★ (Cog) 別のCogを開発した場合は、登録処理をここに実装する
        # self.add_cog(
        #     TER????Cog(self.__token, pu, {}, [], )
        # )
        #
        name_color: str = str(self.__j['bot']['nameColor']).casefold().strip()
        if name_color != 'doNotChange'.casefold().strip():
            print(f'    Setting bot name color = {name_color} ... ', end='', )
            #
            await self.update_chatter_color(
                self.__token, self.user_id, name_color
            )
            print(f'done.')
        print(f'  done.')
        print(f'')

    async def event_command_error(self,
        context: commands.Context, error: Exception
    ) -> None:
        return

    @commands.command(name='test', )
    async def __test(self, ctx: commands.Context):
        print(f"  Testing bot (v{str(self.__j['verNo']).casefold().strip()}) ...")
        print(f'    Channel name = {ctx.channel.name}')
        print(f'    Bot user ID = {self.user_id}')
        print(f'    Bot user name = {self.nick}')
        print(f'    Bot commands')
        for c_name in self.commands.keys():
            print(f'      {self.__prefix}{c_name}')
        print(f'    Bot cogs')
        for c_name in self.cogs.keys():
            print(f'      {c_name}')
        #
        await ctx.send(f'/me bot for {self.__prefix} is alive.')
        print(f'  done.')
        print(f'')

    @commands.command(name='restart', )
    async def __restart(self, ctx: commands.Context):
        ctx.message.content = (
            f"{self.__prefix}kill {str(self.__j['returnCodeForRestrt'])}"
        )
        #
        await self.__kill(ctx)

    @commands.command(name='kill', )
    async def __kill(self, ctx: commands.Context):
        if self.__is_by_channel_broadcaster_or_myself(ctx) is True:
            print(f'  Killing bot ... ')
            self.loop.stop()
            #
            await ctx.send(f'/me bot for {self.__prefix} has stopped.')
            #
            is_valid_return_code: bool = False
            return_code_str: str = str(
                ctx.message.content
            ).strip().removeprefix(f'{self.__prefix}kill').strip()
            if len(return_code_str) <= 3 and return_code_str.isdecimal() is True:
                return_code_int: int = int(return_code_str)
                if 0 <= return_code_int <= 255:
                    self.__return_code = return_code_int
                    is_valid_return_code = True
                else:
                    self.__return_code = 0
                    is_valid_return_code = False
            else:
                self.__return_code = 0
                is_valid_return_code = (
                    True if len(return_code_str) == 0 else False
                )
            print(f'    Return code = {self.__return_code}', end='', )
            if self.__return_code == int(self.__j['returnCodeForRestrt']):
                print(f' (Restart)')
            else:
                print(f'')
            if is_valid_return_code is False:
                print(f'      * Invalid return code input')
            print(f'  done.')
            print(f'')

    def __is_by_channel_broadcaster_or_myself(self,
        ctx: commands.Context,
    ) -> bool:
        if type(ctx.author) is Chatter:
            if ctx.author.is_broadcaster is True:
                return True
            elif str(ctx.author.id) == str(self.user_id):
                return True
            else:
                return False
        else:
            return False

    def kill_self_without_print(self) -> None:
        self.__return_code = 0
        self.loop.stop()

    def kill_bouyomi_process(self) -> None:
        c: commands.Cog | None = self.get_cog('TERBouyomiCog')
        if type(c) is TERBouyomiCog:
            print(f'  Killing BouyomiChan ... ', end='', )
            c.kill_process()
            print(f'done.')
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
