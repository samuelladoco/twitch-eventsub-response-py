# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import Any
#
from twitchio.client import Channel
from twitchio.ext import commands
#
from .base import TERBaseCog, TERResponseCM
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class TERRaidCog(TERBaseCog):

    @commands.Cog.event(event='event_raw_usernotice')
    async def raid_response(self,
        channel: Channel, tags: dict[Any, Any],
    ) -> None:
        msg_id: str = tags.get('msg-id', '')
        if msg_id != 'raid':
            return
        #
        print(f'  Responding to raid ...')
        raid_broadcaster_user_name: str = tags.get('msg-param-login', '')
        print(f'    Raid broadcaster user name = {raid_broadcaster_user_name}')
        #
        # 置換される文字列たちを定義
        replacements: dict[str, str] = {
            '{{raidBroadcasterUserName}}': raid_broadcaster_user_name,
            # ToDo: ★ 別の文字列にも対応する場合は、ここに実装する
            # '{{}}': '',
        }
        #
        cms: tuple[list[TERResponseCM], list[TERResponseCM]] = (
            self.replace_double_curly_brackets(replacements)
        )
        for cs in cms[0]:
            # shoutout の場合
            if cs.command[0] == 'shoutout':
                # レイド元のユーザー(チャンネル)IDを取得して利用
                shoutout_broadcaster_user_id = str(tags.get('user-id', 0))
                print(
                    f'    Shoutout broadcaster user ID = ' +
                    f'{shoutout_broadcaster_user_id}'
                )
                if shoutout_broadcaster_user_id == '0':
                    print(f'      * Cannot shoutout.')
                cs.command.append(shoutout_broadcaster_user_id)
            #
            # ToDo: ★ 別のコマンドにも対応する場合は、追加の引数取得をここに実装する
            # elif cm.command[0] == '???':
            #     pass
            else:
                pass
        #
        await self.execute_commands_and_send_messages(channel, cms[0], cms[1])
        print(f'  done.')
        print(f'')
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
