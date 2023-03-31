# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import aiohttp
import json
from typing import Any
#
from twitchio import Message, PartialUser
from twitchio.ext import commands
#
import deepl
import deepltranslate
import deepltranslate.settings
import googletrans
import googletrans.models
#
from .base_cog import TERBaseCog
from .__lang import TERLang, TERTransService
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class TERTransCog(TERBaseCog):

    def __init__(self,
        _token: str, _pu: PartialUser,
        _settings_base: dict[str, Any], _response_cms_base: list[list[Any]],
        _prefix: str,
    ) -> None:
        super().__init__(_token, _pu, _settings_base, _response_cms_base, )
        #
        #
        # 設定値
        #   置換される文字列たちを定義
        replacements: dict[str, str] = {
            #
            # ToDo: ★ (置換) 別の文字列置換にも対応する場合は、ここに実装する
            # '{{????}}': '????'
        }
        #   置換後の設定値たち
        self.__settings_replaced: dict[str, Any] = (
            self.get_settings_replaced(replacements, )
        )
        #
        #
        # 使用する翻訳サービスたち
        self.__services: list[TERTransService] = []
        #   対応言語たち
        self.__from_langs_all: dict[TERTransService, list[str]] = {}
        self.__to_langs_all: dict[TERTransService, list[str]] = {}
        #   翻訳サービスたち
        self.__translator_d_trans: deepl.Translator | None = None
        self.__translator_g_trans: googletrans.Translator | None = None
        self.__translator_g_session_url: tuple[aiohttp.ClientSession, str] | None = None
        for service_with_key_or_url in self.__settings_replaced['serviceWithKeyOrURLs']:
            if isinstance(service_with_key_or_url, list) is False:
                continue
            tts: TERTransService | None = TERTransService.get(
                str(service_with_key_or_url[0])
            )
            if tts is None or len(service_with_key_or_url) <= 1:
                continue
            key_or_url: str = str(service_with_key_or_url[1]).strip()
            # DeepL Python Library
            if tts is TERTransService.DEEPLKEY:
                try:
                    self.__translator_d_trans = deepl.Translator(key_or_url)
                    # 対応言語文字列たちは小文字で持つことにする(以下、同様)
                    self.__from_langs_all[tts] = [
                        (l.code).casefold().strip()
                        for l
                        in self.__translator_d_trans.get_source_languages()
                    ]
                    self.__to_langs_all[tts] = [
                        (l.code).casefold().strip()
                        for l
                        in self.__translator_d_trans.get_target_languages()
                    ]
                except deepl.exceptions.AuthorizationException as e:
                    print(
                        f'      Getting translatable languages lists ' +
                        f'for {tts.name} failed.'
                    )
                    print(f'        {e}')
                    print(f'')
                    continue
            # DeepL Translate
            elif tts is TERTransService.DEEPLTRANSLATE:
                self.__from_langs_all[tts] = [
                    d['code'].casefold().strip()
                    for d in deepltranslate.settings.SUPPORTED_LANGUAGES
                ]
                self.__to_langs_all[tts] = [
                    d['code'].casefold().strip()
                    for d in deepltranslate.settings.SUPPORTED_LANGUAGES
                ]
            # Googletrans
            elif tts is TERTransService.GOOGLETRANS:
                try:
                    self.__translator_g_trans = googletrans.Translator(
                        service_urls = [key_or_url, ],
                        raise_exception=True,
                    )
                    self.__from_langs_all[tts] = [
                        k.casefold().strip()
                        for k in googletrans.LANGUAGES.keys()
                    ]
                    self.__to_langs_all[tts] = [
                        k.casefold().strip()
                        for k in googletrans.LANGUAGES.keys()
                    ]
                except Exception as e:
                    print(
                        f'      Getting translatable languages lists ' +
                        f'for {tts.name} failed.'
                    )
                    print(f'        {e}')
                    print(f'')
                    continue
            # Google Apps Script (GAS)
            elif tts is TERTransService.GOOGLEGAS:
                if _pu._http.session is None:
                    continue
                self.__translator_g_session_url = (
                    _pu._http.session, key_or_url
                )
                self.__from_langs_all[tts] = [
                    k.casefold().strip() for k in googletrans.LANGUAGES.keys()
                ]
                self.__to_langs_all[tts] = [
                    k.casefold().strip() for k in googletrans.LANGUAGES.keys()
                ]
            else:
                assert False, f'Translation service is {tts}.'
            #
            self.__services.append(tts)
        #
        # 翻訳元言語の推定に使うための googleTrans
        self.__translator_g_detection: googletrans.Translator | None = None
        try:
                self.__translator_g_detection = googletrans.Translator(
                    service_urls = [
                        self.__settings_replaced['fromLanguageDetection'],
                    ],
                    raise_exception=True,
                )
        except Exception as e:
            print(f'      Getting language detection function failed.')
            print(f'        {e}')
            print(f'')
        #
        #
        # 翻訳しないメッセージ
        #   送信したユーザーたち
        self.__sender_user_names_to_ignore: list[str] = [
            str(s).casefold().strip()
            for s in self.__settings_replaced['messagesToIgnore']['senderUserName']
            if str(s).casefold().strip() != ''
        ]
        #   翻訳元言語たち
        self.__from_langs_to_ignore: list[str] = [
            str(s).casefold().strip()
            for s in self.__settings_replaced['messagesToIgnore']['fromLanguages']
            for tts in self.__from_langs_all.keys()
            if str(s).casefold().strip() in self.__from_langs_all[tts]
        ]
        #   ユーザーコマンドの接頭辞たち ( <ter>_ も含む)
        self.__user_command_prefixes_to_ignore: list[str] = [
            str(s).strip()
            for s in self.__settings_replaced['messagesToIgnore']['userCommandPrefixes']
            if str(s).strip() != ''
        ]
        self.__user_command_prefixes_to_ignore.append(_prefix)
        #   メッセージ内の文字列たち
        self.__strings_in_message_to_ignore: list[str] = [
            str(s).strip()
            for s in self.__settings_replaced['messagesToIgnore']['stringsInMessage']
            if str(s).strip() != ''
        ]
        #
        #
        # 翻訳先言語
        #   既定
        self.__to_langs_default: list[str] = [
            str(s).casefold().strip()
            for s in self.__settings_replaced['toLanguages']['defaults']
            for tts in self.__to_langs_all.keys()
            if str(s).casefold().strip() in self.__to_langs_all[tts]
        ]
        if len(self.__to_langs_default) == 0:
            self.__services = []
            return
        #   翻訳元言語が既定の翻訳先言語であった場合
        self.__to_langs_if_from_lang_is_in_defaults: list[str] = [
            str(s).casefold().strip()
            for s in self.__settings_replaced['toLanguages']['onesIfFromLanguageIsInDefaults']
            for tts in self.__to_langs_all.keys()
            if str(s).casefold().strip() in self.__to_langs_all[tts]
        ]
        #
        #
        # 翻訳先メッセージへの文字列追加
        #   翻訳元メッセージを送信したユーザー名
        self.__adds_sender_user_name: bool = (
            self.__settings_replaced['supplementsToTranslatedMessage']['senderUserName']
        )
        #   翻訳元と翻訳先の言語
        self.__adds_from_to_lang: bool = (
            self.__settings_replaced['supplementsToTranslatedMessage']['fromToLanguages']
        )

    @commands.Cog.event(event='event_message')  # type: ignore
    async def message_response(self, message: Message) -> None:
        # (翻訳しない 1/6)
        #   翻訳サービスが全く設定されていない
        if len(self.__services) == 0:
            return
        #   メッセージがボットによる反応によるものである
        if bool(message.echo) is True:
            return
        #
        #
        # メッセージから文字列を除去
        #   左右空白
        text_from_w_langs: str = (
            '' if message.content is None else str(message.content).strip()
        )
        #   エモート文字列たち
        if (
            message.tags is not None
            and 'emotes' in message.tags.keys()
            and str(message.tags['emotes']) != ''
        ):
            emote_names: list[str] = []
            #
            emote_id_positions_col: list[str] = (
                str(message.tags['emotes']).split('/')
            )
            for emote_id_positions in emote_id_positions_col:
                id_and_positions: list[str] = emote_id_positions.split(':')
                assert len(id_and_positions) == 2, (
                    f'Emote ID & positions are {id_and_positions}.'
                )
                first_position: str = id_and_positions[1].split(',')[0]
                from_and_to: list[str] = first_position.split('-')
                assert len(from_and_to) == 2, (
                    f'1st position of {id_and_positions[0]} is {from_and_to}.'
                )
                # (* メッセージ(各種削除前のもの)からエモート名を特定)
                if message.content is not None:
                    emote_names.append(
                        str(message.content)[
                            int(from_and_to[0]):int(from_and_to[1]) + 1
                        ]
                    )
            #
            for emote_name in emote_names:
                text_from_w_langs = text_from_w_langs.replace(emote_name, '')
        #   単語間を半角空白1つで統一
        text_from_w_langs = ' '.join(text_from_w_langs.split())
        #
        # (翻訳しない 2/6) メッセージが空になった
        if text_from_w_langs == '':
            return
        #
        # 送信者のユーザー名(小文字化済み, 左右空白除去済み)
        sender_user_name: str = (
            '' if message.author.name is None
            else str(message.author.name).casefold().strip()
        )
        #
        #
        # (翻訳しない 3/6)
        #   メッセージ送信者が翻訳しないユーザー名たちの中に含まれている
        if sender_user_name in self.__sender_user_names_to_ignore:
            return
        #   メッセージの接頭辞が翻訳しないユーザーコマンドの接頭辞たちの中に含まれている
        for user_command_prefix_to_ignore in self.__user_command_prefixes_to_ignore:
            if text_from_w_langs.startswith(user_command_prefix_to_ignore):
                return
        #   メッセージに翻訳しない文字列たちのいずれかが含まれている
        for string_in_message_to_ignore in self.__strings_in_message_to_ignore:
            if string_in_message_to_ignore in text_from_w_langs:
                return
        #
        #
        # 翻訳処理
        text_to: str = ''
        lang_from: str | None = None
        lang_to: str | None = None
        index_service: int = 0
        services_to_be_removed: list[TERTransService] = []
        while index_service < len(self.__services):
            # 翻訳元言語
            lang_from = None
            text_from_wo_langs: str = text_from_w_langs
            #   メッセージ内に指定があれば従う
            lang_from_and_text_froms: list[str] = text_from_wo_langs.split(' > ')
            if len(lang_from_and_text_froms) >= 2:
                # 対応言語を、現在のサービス～最後のサービスから探す
                for i in range(index_service, len(self.__services)):
                    if (
                        lang_from_and_text_froms[0].casefold().strip()
                        in self.__from_langs_all[self.__services[i]]
                    ):
                        lang_from = lang_from_and_text_froms[0].casefold().strip()
                        text_from_wo_langs = ' > '.join(
                            lang_from_and_text_froms[1:]
                        )
                        index_service = i
                        break
                # ない場合は、現在のサービスを維持する
            #   独自で日本語, 中国語(簡体字), 中国語(繁体字)であるかそれ以外かを推定
            if lang_from is None:
                lang_from = TERLang.detect_cj(
                    text_from_wo_langs, self.__services[index_service],
                )
            #   googleTrans を利用して推定
            if lang_from is None and self.__translator_g_detection is not None:
                try:
                    lang_from_g_detection: str = str(
                        self.__translator_g_detection.detect(
                            text_from_wo_langs
                        ).lang
                    ).casefold().strip()
                    # 対応言語を、現在のサービス～最後のサービスから探す
                    for i in range(index_service, len(self.__services)):
                        # googleTrans と現在のサービスとで言語名が違う場合は変換
                        lang_from_converted: str = TERLang.convert_from(
                            lang_from_g_detection, self.__services[i],
                        )
                        if (
                            lang_from_converted
                            in self.__from_langs_all[self.__services[i]]
                        ):
                            lang_from = lang_from_converted
                            index_service = i
                            break
                    # ない場合は、現在のサービスを維持する
                except Exception as e:
                    print(
                        f'  Language detection of "{text_from_w_langs}" failed.'
                    )
                    print(f'    {e}')
                    print(f'')
            #
            # (翻訳しない 4/6) メッセージが翻訳しない言語たちのいずれかである
            if lang_from in self.__from_langs_to_ignore:
                return
            #
            # 翻訳先言語
            lang_to = None
            #   メッセージ内に指定があれば従う
            text_from_and_lang_tos: list[str] = text_from_wo_langs.split(' > ')
            if len(text_from_and_lang_tos) >= 2:
                # 対応言語を、現在のサービス～最後のサービスから探す
                for i in range(index_service, len(self.__services)):
                    if (
                        text_from_and_lang_tos[-1].casefold().strip()
                        in self.__to_langs_all[self.__services[i]]
                    ):
                        lang_to = text_from_and_lang_tos[-1].casefold().strip()
                        text_from_wo_langs = ' > '.join(
                            text_from_and_lang_tos[0:-1]
                        )
                        index_service = i
                        break
                # ない場合は、現在のサービスを維持する
            #   既定
            if lang_to is None:
                is_service_found: bool = False
                # 対応言語を、現在のサービス～最後のサービスから探す
                for i in range(index_service, len(self.__services)):
                    for to_lang_default in self.__to_langs_default:
                        if to_lang_default in (
                            self.__to_langs_all[self.__services[i]]
                        ):
                            lang_to = to_lang_default
                            index_service = i
                            is_service_found = True
                            break
                    if is_service_found is True:
                        break
                # ない場合は、現在のサービスを維持する
                #   ( lang_to is None なので、以下で return )
            #   推定した翻訳元と翻訳先が同じであった場合
            if lang_to is not None and lang_from == lang_to:
                lang_to = None
                is_service_found: bool = False
                # 対応言語を、現在のサービス～最後のサービスから探す
                for i in range(index_service, len(self.__services)):
                    for to_lang_if in self.__to_langs_if_from_lang_is_in_defaults:
                        if to_lang_if in (
                            self.__to_langs_all[self.__services[i]]
                        ):
                            lang_to = to_lang_if
                            index_service = i
                            is_service_found = True
                            break
                    if is_service_found is True:
                        break
                # ない場合は、現在のサービスを維持する
                #   ( lang_to is None なので、以下で return )
            #
            # (翻訳しない 5/6) 翻訳先の言語が決まっていない
            if lang_to is None:
                return
            #
            # 現在のサービスで非対応の言語ならば次のサービスへ
            is_translatable: bool = True
            if (
                lang_from
                not in self.__from_langs_all[self.__services[index_service]]
            ):
                # DeepL Translate は lang_from が None の場合に非対応
                if (
                    self.__services[index_service] is TERTransService.DEEPLTRANSLATE
                    or lang_from is not None
                ):
                    is_translatable = False
            if (
                lang_to
                not in self.__to_langs_all[self.__services[index_service]]
            ):
                is_translatable = False
            if is_translatable is False:
                print(
                    f'  {self.__services[index_service]} cannot translate ' +
                    f'"{text_from_w_langs}" from {lang_from} to {lang_to}.'
                )
                print(f'')
                index_service += 1
                continue
            #
            # 翻訳処理
            try:
                # DeepL Python Library
                if self.__services[index_service] is TERTransService.DEEPLKEY:
                    assert self.__translator_d_trans is not None, (
                        f'{self.__services[index_service]} is not available.'
                    )
                    if lang_from is not None:
                        lang_from = lang_from.upper()
                    lang_to = lang_to.upper()
                    #
                    r_or_rs: deepl.TextResult | list[deepl.TextResult] = (
                        self.__translator_d_trans.translate_text(
                            text_from_wo_langs,
                            source_lang=lang_from, target_lang=lang_to,
                            split_sentences=deepl.SplitSentences.NO_NEWLINES,
                            outline_detection=False,
                        )
                    )
                    if type(r_or_rs) is deepl.TextResult:
                        text_to = r_or_rs.text
                        lang_from = (
                            r_or_rs.detected_source_lang.upper().strip()
                        )
                    elif type(r_or_rs) is list and r_or_rs[0] is deepl.TextResult:
                        text_to = ' '.join([r.text for r in r_or_rs])
                        lang_from = (
                            str(r_or_rs[0].detected_source_lang).upper().strip()
                        )
                    else:
                        assert False, f'{r_or_rs}([0]) is not deepl.TextResult.'
                    break
                # DeepL Translate
                elif self.__services[index_service] is TERTransService.DEEPLTRANSLATE:
                    assert lang_from is not None, (
                        f'{self.__services[index_service]} is not available.'
                    )
                    lang_from = lang_from.upper()
                    lang_to = lang_to.upper()
                    text_to = str(
                        deepltranslate.translate(
                            lang_from, lang_to, text_from_wo_langs
                        )
                    )
                    break
                # Googletrans
                elif self.__services[index_service] is TERTransService.GOOGLETRANS:
                    assert self.__translator_g_trans is not None, (
                        f'{self.__services[index_service]} is not available.'
                    )
                    r: googletrans.models.Translated = (
                        self.__translator_g_trans.translate(
                            text_from_wo_langs,
                            dest=lang_to,
                            src=lang_from if lang_from is not None else 'auto'
                        )
                    )
                    text_to = str(r.text)
                    lang_from = str(r.src).casefold().strip()
                    break
                # Google Apps Script (GAS)
                elif self.__services[index_service] is TERTransService.GOOGLEGAS:
                    assert self.__translator_g_session_url is not None, (
                        f'{self.__services[index_service]} is not available.'
                    )
                    p: str = f'text={text_from_wo_langs}'
                    if lang_from is not None:
                        p += f'&source={lang_from}'
                    p += f'&target={lang_to}'
                    #
                    async with self.__translator_g_session_url[0].get(
                        f'{self.__translator_g_session_url[1]}?{p}'
                    ) as res:
                        res.raise_for_status()
                        d: dict[str, Any] = json.loads(await res.text())
                        if int(d['code']) == 200:
                            text_to = str(d['text'])
                            if lang_from is None:
                                lang_from = '??'
                        else:
                            raise ValueError(
                                f'{res.status=}, {await res.text()=}'
                            )
                    break
                else:
                    assert False, (
                        f'Translation service is {self.__services[index_service]}.'
                    )
            except Exception as e:
                services_to_be_removed.append(self.__services[index_service])
                print(
                    f'  Translation of "{text_from_w_langs}" ' +
                    f'by {self.__services[index_service]} failed.'
                )
                print(f'    {e}')
                print(f'')
            #
            index_service += 1
        #
        for service_to_be_removed in services_to_be_removed:
            self.__services.remove(service_to_be_removed)
        #
        #
        # (翻訳しない 6/6) 翻訳できなかった
        if text_to == '':
            return
        #
        #
        # 翻訳先メッセージへの文字列追加
        #   翻訳元メッセージを送信したユーザー名
        if self.__adds_sender_user_name is True:
            text_to = f'{sender_user_name}: {text_to}'
        #   翻訳元と翻訳先の言語
        if self.__adds_from_to_lang is True:
            text_to = f'{text_to} ({lang_from} > {lang_to})'
        #
        #
        await message.channel.send(f'/me {text_to}')
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
