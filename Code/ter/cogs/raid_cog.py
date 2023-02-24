# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
from typing import Any
#
from twitchio.channel import Channel
from twitchio.ext import commands
#
from .base_cog import TERBaseCog, TERCommandMessageUnit
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class TERRaidCog(TERBaseCog):

    @commands.Cog.event(event='event_raw_usernotice')  # type: ignore
    async def raid_response(self,
        channel: Channel, tags: dict[Any, Any]
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
        }
        #
        cm_units: list[TERCommandMessageUnit] = self.get_replaced_cm_units(
            replacements
        )
        for cm_unit in cm_units:
            # (コマンド) /shoutout の場合
            if cm_unit.cm_replaced == '/shoutout':
                # レイド元のユーザー(チャンネル)IDを取得して利用
                shoutout_broadcaster_user_id = str(tags.get('user-id', 0))
                print(
                    f'    Shoutout broadcaster user ID = ' +
                    f'{shoutout_broadcaster_user_id}'
                )
                if shoutout_broadcaster_user_id == '0':
                    print(f'      * Cannot shoutout.')
                cm_unit.extend_args_replaced([shoutout_broadcaster_user_id])
            #
            # ToDo: ★ (コマンド) 別のコマンドにも対応する場合は、追加の引数取得をここに実装する
            # elif cm_unit.cm_replaced == '/???':
            #     pass
            else:
                pass
        #
        await self.execute_cms(channel, cm_units, )
        print(f'  done.')
        print(f'')
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
