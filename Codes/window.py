# Import
from __future__ import annotations

import sys
import tkinter as tk
import tkinter.scrolledtext as tks
from typing import AnyStr, Callable, ClassVar, Union


# Classes
class TkinterConsoleWindow:
    __root: ClassVar[Union[tk.Tk, None]] = None
    __text: ClassVar[Union[tks.ScrolledText, None]] = None
    #
    lets_thread_close_window: ClassVar[bool] = False
    __thread_close_window_intervale_ms: ClassVar[int] = 4000
    #
    __func_kill_bot: Callable[[], None] | None = None
    #
    __window_width: ClassVar[int] = 48 * 16 - 13
    __window_height: ClassVar[int] = 48 * 9 - 15
    __text_padding: ClassVar[int] = 8
    __color_background: ClassVar[str] = "#0c0c0c"
    __color_foreground: ClassVar[str] = "#e5e5e5"
    __color_selectbackground: ClassVar[str] = "#858585"
    __font: ClassVar[tuple[str, int]] = ("Cascadia Mono", 12)

    @classmethod
    def open(cls, _ver_no: str) -> None:
        root: tk.Tk = tk.Tk()
        root.title(f"Twitch EventSub Response Bot (v{_ver_no})")
        root.geometry(f"{cls.__window_width}x{cls.__window_height}")
        #
        text: tks.ScrolledText = tks.ScrolledText(
            root,
            width=(cls.__window_width - cls.__text_padding * 2),
            padx=cls.__text_padding,
            pady=cls.__text_padding,
            background=cls.__color_background,
            foreground=cls.__color_foreground,
            insertbackground=cls.__color_foreground,
            selectbackground=cls.__color_selectbackground,
            font=cls.__font,
        )
        #
        menu_right_click: tk.Menu = tk.Menu(
            root,
            tearoff=0,
        )
        menu_right_click.add_command(
            label="Copy                      Ctrl+C",
            command=lambda: [
                text.clipboard_clear(),
                text.clipboard_append(text.get(tk.SEL_FIRST, tk.SEL_LAST)),
            ]
            if text.tag_ranges(tk.SEL) != ()
            else [],
        )
        menu_right_click.add_separator()
        menu_right_click.add_command(
            label="Select all                Ctrl+A",
            command=lambda: [
                text.tag_add(tk.SEL, "1.0", tk.END),
            ],
        )
        text.bind(
            "<Button-3>", lambda e: menu_right_click.post(e.x_root, e.y_root)
        )
        #
        text.configure(state=tk.DISABLED)
        text.pack()
        cls.__text = text
        #
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", cls.__close_delete_window)
        root.after(
            cls.__thread_close_window_intervale_ms, cls.__close_or_not_after
        )
        cls.__root = root
        cls.__root.mainloop()
        #
        del menu_right_click
        del cls.__text
        del text
        del cls.__root
        del root

    @classmethod
    def is_aleady_opened(cls) -> bool:
        return cls.__root is not None and cls.__text is not None

    @classmethod
    def add_func_kill_bot(cls, f: Callable[[], None]) -> None:
        cls.__func_kill_bot = f

    @classmethod
    def write(cls, s: AnyStr) -> int:
        if cls.__text is not None:
            cls.__text.see(tk.END)
            cls.__text.configure(state=tk.NORMAL)
            cls.__text.insert(tk.END, str(s))
            cls.__text.configure(state=tk.DISABLED)
            cls.__text.see(tk.END)
            return len(s)
        return 0

    @classmethod
    def flush(cls) -> None:
        pass

    @classmethod
    def __close_delete_window(cls) -> None:
        if cls.__root is not None:
            sys.stdout = None
            sys.stderr = None
            cls.__root.destroy()
            if cls.__func_kill_bot is not None:
                cls.__func_kill_bot()

    @classmethod
    def __close_or_not_after(cls) -> None:
        if cls.__root is not None:
            if cls.lets_thread_close_window is True:
                cls.__root.destroy()
            else:
                cls.__root.after(
                    cls.__thread_close_window_intervale_ms,
                    cls.__close_or_not_after,
                )
