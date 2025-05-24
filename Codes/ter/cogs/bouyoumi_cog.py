# Import
from __future__ import annotations

import pathlib
import subprocess
from typing import Any

import aiohttp
from twitchio import Chatter, Message, PartialUser
from twitchio.ext import commands

from .base_cog import TERBaseCog


# Classes
class TERBouyomiCog(TERBaseCog):
    def __init__(
        self,
        _token: str,
        _pu: PartialUser,
        _settings_base: dict[str, Any],
        _response_cms_base: list[list[Any]],
        _prefix: str,
    ) -> None:
        super().__init__(_token, _pu, _settings_base, _response_cms_base)
        #
        #
        # セッション
        self.__session: aiohttp.ClientSession | None = _pu._http.session
        # 棒読みちゃん プロセス
        self.__p: subprocess.Popen | None = None
        #
        #
        # 設定値
        self.__settings_replaced: dict[str, Any] = self.get_settings_replaced(
            {}
        )
        #
        #
        # メッセージたちを受け渡すか否か
        self.__sends_messages = bool(self.__settings_replaced["sendsMessages"])
        if self.__sends_messages is False:
            return
        #
        #
        # 自動起動・停止とパス
        arkp: pathlib.Path = pathlib.Path(
            rf"{self.__settings_replaced['autoRunKillPath']}"
        )
        self.__auto_run_kill_path: pathlib.Path | None = (
            arkp if arkp.exists() is True and arkp.is_file() is True else None
        )
        # ポート番号
        self.__port_no: int = int(self.__settings_replaced["portNo"])
        #
        if self.__auto_run_kill_path is not None:
            try:
                print(
                    f'        Running "{str(self.__auto_run_kill_path)}" ... ',
                    end="",
                )
                self.__p = subprocess.Popen(self.__auto_run_kill_path)
                print("done.")
            except (OSError, subprocess.CalledProcessError) as e:
                print("failed")
                print(f"          {e}")
        #
        #
        # 受け渡すメッセージたちに対する制限
        #   送信ユーザーのユーザー名ないし表示名の、
        #   末尾の数字部分を省略するか否か
        self.__ignores_sender_name_suffix_num: bool = bool(
            self.__settings_replaced["limitsWhenPassing"][
                "ignoresSenderNameSuffixNum"
            ]
        )
        #   送信ユーザーのユーザー名ないし表示名の、先頭からの文字数の上限
        self.__num_sender_name_characters: int = int(
            self.__settings_replaced["limitsWhenPassing"][
                "numSenderNameCharacters"
            ]
        )
        #   先頭からのエモート(スタンプ)数の上限
        self.__num_emotes: int = int(
            self.__settings_replaced["limitsWhenPassing"]["numEmotes"]
        )
        #
        #
        # 受け渡さないメッセージたち
        #   送信したユーザーたち
        self.__sender_user_names_to_ignore: list[str] = [
            str(s).casefold().strip()
            for s in self.__settings_replaced["messagesToIgnore"][
                "senderUserNames"
            ]
            if str(s).casefold().strip() != ""
        ]
        #   ユーザーコマンドの接頭辞たち ( <ter>_ も含む)
        self.__user_command_prefixes_to_ignore: list[str] = [
            str(s).strip()
            for s in self.__settings_replaced["messagesToIgnore"][
                "userCommandPrefixes"
            ]
            if str(s).strip() != ""
        ]
        self.__user_command_prefixes_to_ignore.append(_prefix)
        #   メッセージ内の文字列たち
        self.__strings_in_message_to_ignore: list[str] = [
            str(s).strip()
            for s in self.__settings_replaced["messagesToIgnore"][
                "stringsInMessage"
            ]
            if str(s).strip() != ""
        ]
        #
        #
        # 翻訳先メッセージの構成
        self.__messages_format: str = str(
            self.__settings_replaced["messagesFormat"]
        ).strip()

    @commands.Cog.event(event="event_message")
    async def message_response(self, message: Message) -> None:
        # (受け渡さない 1/3)
        #   セッションがない
        if self.__session is None:
            return
        #   メッセージたちを受け渡さないように設定されている
        if self.__sends_messages is False:
            return
        #   メッセージがボットによる反応によるものである
        if bool(message.echo) is True:
            return
        #
        #
        # メッセージから文字列を除去
        #   左右空白
        text: str = (
            "" if message.content is None else str(message.content).strip()
        )
        #   /me 公式コマンド実行時に付随してくるもの
        text = text.removeprefix("\x01ACTION").removesuffix("\x01")
        #   エモート文字列たち
        if (
            message.tags is not None
            and "emotes" in message.tags.keys()
            and str(message.tags["emotes"]) != ""
        ):
            emote_names: list[str] = []
            #
            emote_id_positions_col: list[str] = str(
                message.tags["emotes"]
            ).split("/")
            for emote_id_positions in emote_id_positions_col:
                id_and_positions: list[str] = emote_id_positions.split(":")
                assert len(id_and_positions) == 2, (
                    f"Emote ID & positions are {id_and_positions}."
                )
                first_position: str = id_and_positions[1].split(",")[0]
                from_and_to: list[str] = first_position.split("-")
                assert len(from_and_to) == 2, (
                    f"1st position of {id_and_positions[0]} is {from_and_to}."
                )
                # (* メッセージ(各種削除前のもの)からエモート名を特定)
                if message.content is not None:
                    emote_names.append(
                        str(message.content)[
                            int(from_and_to[0]) : int(from_and_to[1]) + 1
                        ]
                    )
            #
            # エモートの削除
            words: list[str] = text.split()
            emote_order: int = 0
            for i, word in enumerate(words):
                if word in emote_names:
                    if emote_order >= self.__num_emotes:
                        words[i] = ""
                    emote_order += 1
            text = " ".join(words)
        #
        #   単語間を半角空白1つで統一
        text = " ".join(text.split())
        #
        # (受け渡さない 2/3) メッセージが空になった
        if text == "":
            return
        #
        #
        # 送信者のユーザー名(小文字化済み, 左右空白除去済み)
        sender_user_name: str = (
            ""
            if message.author.name is None
            else str(message.author.name).casefold().strip()
        )
        # 送信者の表示名(左右空白除去済み)
        sender_display_name: str = (
            ""
            if type(message.author) is not Chatter
            else (
                ""
                if message.author.display_name is None
                else str(message.author.display_name).strip()
            )
        )
        #
        #
        # (受け渡さない 3/3)
        #   メッセージ送信者が翻訳しないユーザー名たちの中に含まれている
        if sender_user_name in self.__sender_user_names_to_ignore:
            return
        #   メッセージの接頭辞が
        #   翻訳しないユーザーコマンドの接頭辞たちの中に含まれている
        for (
            user_command_prefix_to_ignore
        ) in self.__user_command_prefixes_to_ignore:
            if text.startswith(user_command_prefix_to_ignore):
                return
        #   メッセージに翻訳しない文字列たちのいずれかが含まれている
        for string_in_message_to_ignore in self.__strings_in_message_to_ignore:
            if string_in_message_to_ignore in text:
                return
        #
        #
        # 送信ユーザーのユーザー名ないし表示名に対する制限を適用
        if self.__ignores_sender_name_suffix_num is True:
            sender_user_name = sender_user_name.rstrip(
                "0123456789０１２３４５６７８９"
            )
            sender_display_name = sender_display_name.rstrip(
                "0123456789０１２３４５６７８９"
            )
        sender_user_name = sender_user_name[
            : self.__num_sender_name_characters
        ]
        sender_display_name = sender_display_name[
            : self.__num_sender_name_characters
        ]
        #
        #
        # 置換される文字列たちを定義
        replacements: dict[str, str] = {
            "{{senderUserName}}": sender_user_name,
            "{{senderDisplayName}}": sender_display_name,
            "{{senderMessage}}": text,
            #
            # ToDo: ★ (置換) 別の文字列置換にも対応する場合は、ここに実装する
            # '{{????}}': '????',
        }
        # 置換後の受け渡しメッセージ
        m: str = self.__messages_format
        for k, v in replacements.items():
            m = m.replace(k, v)
        # 空白類を %20 に置換
        m = "%20".join(m.split())
        #
        #
        try:
            async with self.__session.get(
                f"http://localhost:{self.__port_no}/talk?text={m}"
            ) as res:
                res.raise_for_status()
                if res.status != 200:
                    raise ValueError(f"{res.status=}, {await res.text()=}")
        except Exception as e:
            print(f'  Passing "{m}" to BouyomiChan failed.')
            print(f"    {e}")
            print("")

    def kill_process(self) -> None:
        if self.__p is not None and self.__p.poll() is None:
            print("  Killing BouyomiChan ... ", end="")
            self.__p.kill()
            print("done.")
