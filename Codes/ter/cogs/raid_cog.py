# Import
from __future__ import annotations

from typing import Any

from twitchio import Channel
from twitchio.ext import commands

from .base_cog import TERBaseCog, TERCommandMessageUnit


# Classes
class TERRaidCog(TERBaseCog):
    @commands.Cog.event(event="event_raw_usernotice")
    async def raid_response(
        self, channel: Channel, tags: dict[Any, Any]
    ) -> None:
        msg_id: str = tags.get("msg-id", "")
        if msg_id != "raid":
            return
        #
        #
        print("  Responding to raid ...")
        raid_broadcaster_user_name: str = tags.get("msg-param-login", "")
        print(f"    Raid broadcaster user name = {raid_broadcaster_user_name}")
        #
        #
        # コマンドやメッセージたち
        #   置換される文字列たちを定義
        replacements: dict[str, str] = {
            "{{raidBroadcasterUserName}}": raid_broadcaster_user_name,
            #
            # ToDo: ★ (置換) 別の文字列置換にも対応する場合は、ここに実装する
            # '{{????}}': '????',
        }
        #   置換後のコマンドやメッセージたち
        cm_units_replaced: list[TERCommandMessageUnit] = (
            self.get_cm_units_replaced(replacements)
        )
        #
        #
        cm_units_valid: list[TERCommandMessageUnit] = []
        for cm_unit in cm_units_replaced:
            # (コマンド) /shoutout の場合
            if cm_unit.cm_replaced == "/shoutout":
                # レイド元のユーザー(チャンネル)IDを取得して利用
                shoutout_broadcaster_user_id: str = str(
                    tags.get("user-id", -1)
                )
                print(
                    "    Shoutout broadcaster user ID = "
                    + f"{shoutout_broadcaster_user_id}"
                )
                if shoutout_broadcaster_user_id == "-1":
                    print("      * Invalid ID")
                    continue
                else:
                    cm_unit.extend_args_replaced(
                        [shoutout_broadcaster_user_id]
                    )
            #
            # ToDo: ★ (コマンド)
            #   別のコマンドにも対応する場合は、追加の引数取得をここに実装する
            # elif cm_unit.cm_replaced == '/????':
            #     pass
            else:
                pass
            cm_units_valid.append(cm_unit)
        #
        await self.execute_cms(channel, cm_units_valid)
        print("  done.")
        print("")
