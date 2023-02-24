# Import
# -----------------------------------------------------------------------------
from __future__ import annotations
import chardet
import json5
import pathlib
from typing import Any
# -----------------------------------------------------------------------------


# Classes
# -----------------------------------------------------------------------------
# ----------------------------------------------------------------------
class JSON5Reader:
    """JSON5ファイルを読み込むクラス(クラスメソッドのみ)"""

    @classmethod
    def open_and_loads(cls, _file: pathlib.Path | str, ) -> dict[str, Any]:
        """ファイルをパースして内容を辞書形式で返す

        Parameters
        ----------
        _file : pathlib.Path | str
            ファイルのパス

        Returns
        -------
        dict[str, Any]
            ファイルの内容を辞書形式にしたもの
        """
        s_file: str = ''
        with open(
            file=_file, mode='r', encoding=TextFileEncodingEstimator.do(_file),
        ) as f_t:
            s_file = f_t.read()
        d: dict[str, Any] = json5.loads(s=s_file, )  # type: ignore
        return d
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
class TextFileEncodingEstimator:
    """テキストファイルのエンコーディングを推定するクラス(クラスメソッドのみ)"""

    @classmethod
    def do(cls, _file: pathlib.Path | str, ) -> str:
        """テキストファイルのエンコーディングを推定する

        Parameters
        ----------
        _file : pathlib.Path | str
            ファイルのパス

        Returns
        -------
        str
            推定したエンコーディングの名称
        """
        enc: str = ''
        with open(file=_file, mode='rb', ) as f_b:
            enc = str(chardet.detect(byte_str=f_b.read(), )['encoding'])
        return enc
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
