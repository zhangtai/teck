from typing import Callable

import win32com.client
from pythoncom import CoInitialize  # pylint: disable=no-name-in-module
from win32gui import GetWindowText, EnumWindows, ShowWindow, SetForegroundWindow  # pylint: disable=no-name-in-module

from config.logger import get_logger

logger = get_logger(__name__)


def windowEnumerationHandler(hwnd: int, top_windows: list[tuple[int, str]]):
    top_windows.append((hwnd, GetWindowText(hwnd)))


def bring_window_front(keyword: str, finder: Callable[[str, str], bool]) -> None:
    top_windows: list[tuple[int, str]] = []
    EnumWindows(windowEnumerationHandler, top_windows)
    for i in top_windows:
        if finder(keyword, i[1]):
            logger.info("Bringing %s to front", keyword)
            ShowWindow(i[0], 5)
            shell = win32com.client.Dispatch("WScript.Shell", CoInitialize())
            shell.SendKeys('%')
            SetForegroundWindow(i[0])
            break
