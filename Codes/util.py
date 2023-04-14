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
    def open_and_load(cls, _file: pathlib.Path | str, ) -> dict[str, Any]:
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
        d: dict[str, Any] = {}
        with open(
            _file, mode='r', encoding=TextFileEncodingEstimator.do(_file),
        ) as fp:
            d = json5.load(fp, )  # type: ignore
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
        with open(_file, 'rb', ) as f_b:
            enc = str(chardet.detect(f_b.read(), )['encoding'])
        return enc
# ----------------------------------------------------------------------
# -----------------------------------------------------------------------------
