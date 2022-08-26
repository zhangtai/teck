import platform
import time
from datetime import datetime

from StreamDeck.Transport.Transport import TransportError

from config.logger import get_logger
from Teck.utils.applications import bring_window_front

from .teck import Teck

logger = get_logger(__file__)


if platform.system() == "Darwin":
    from AppKit import (
        NSWorkspace,  # pyright: ignore # pylint: disable=no-name-in-module,import-error
    )

    def get_active_application_name() -> str:
        active_app_name = (
            NSWorkspace.sharedWorkspace()
            .activeApplication()
            .get("NSApplicationBundleIdentifier")
        )
        return active_app_name

if platform.system() == "Windows":
    import psutil
    from win32gui import (  # noqa=F401 # pylint: disable=import-error,unused-import,no-name-in-module
        GetForegroundWindow,
        GetWindowText,
    )
    from win32process import (  # noqa=F401 # pylint: disable=import-error,unused-import,no-name-in-module
        GetWindowThreadProcessId,
    )

    def get_active_application_name() -> str:  # noqa=F811 # pylint: disable=function-redefined
        new_pid = GetWindowThreadProcessId(GetForegroundWindow())
        try:
            active_app_name = psutil.Process(new_pid[-1]).name()
        except (psutil.NoSuchProcess, ValueError):
            logger.warning("Can't get process, ignore")
            active_app_name = "explorer.exe"
        return active_app_name


class Monitor():
    """Class to monitor window switch and trigger Teck instance page switching."""
    def __init__(self) -> None:
        self.teck = Teck()

    def start(self) -> None:
        logger.info("Monitor started")
        while True:
            self.teck.refresh_button_text_image()
            if not self.teck.page_freezed:
                active_app_name = get_active_application_name()
                new_page_name = (
                    active_app_name
                    if active_app_name in self.teck.config.pages
                    else list(self.teck.config.pages.keys())[0]
                )
                if new_page_name != self.teck.active_page:
                    self.teck.blank_page()
                    logger.info("Switching to new page: %s", new_page_name)
                    self.teck.active_page = new_page_name
                    try:
                        self.teck.refresh_page()
                    except TransportError:
                        logger.warning(
                            "No HID device, sleep %s seconds and retry",
                            self.teck.config.retry_interval,
                        )
                        time.sleep(self.teck.config.retry_interval)
                        self.teck.refresh_page()
            if datetime.now().minute % 29 == 0 and datetime.now().second < 1.5:
                logger.info("Current second is %d", datetime.now().second)
                bring_window_front("- Outlook", lambda k, t: t.endswith(k))
            time.sleep(1)

    def stop(self) -> None:
        logger.info("Shutting down monitor")
