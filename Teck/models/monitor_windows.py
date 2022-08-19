import logging
import time

import psutil
from StreamDeck.Transport.Transport import TransportError
from win32gui import GetForegroundWindow, GetWindowText
from win32process import GetWindowThreadProcessId

from .teck import Teck

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Monitor(object):
    """Class to monitor window switch and trigger Teck instance page switching."""
    def __init__(self) -> None:
        self.teck = Teck()
        self.active_application = "system"

    def start(self) -> None:
        while True:
            time.sleep(3)
            self.teck.refresh_button_text_image()
            new_pid = GetWindowThreadProcessId(GetForegroundWindow())
            try:
                active_app_name = psutil.Process(new_pid[-1]).name()
                logger.debug("active_app_name: %s", active_app_name)
                new_page_name = (
                    active_app_name
                    if active_app_name in self.teck.config.pages
                    else list(self.teck.config.pages.keys())[0]
                )
            except (psutil.NoSuchProcess, ValueError):
                logger.warning("Can't get process, ignore")
                new_page_name = self.teck.active_page

            logger.debug(new_page_name)

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
