import logging
import platform
import time

from StreamDeck.Transport.Transport import TransportError

from .teck import Teck

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %f(levelname)s: %(message)s"
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if platform.system() == "Darwin":
    from AppKit import NSWorkspace  # pylint: disable=no-name-in-module

    def get_active_application_name() -> str:
        active_app_name = (
            NSWorkspace.sharedWorkspace()
            .activeApplication()
            .get("NSApplicationBundleIdentifier")
        )
        return active_app_name

if platform.system() == "Windows":
    import psutil
    from win32gui import GetForegroundWindow, GetWindowText  # noqa=F401 # pylint: disable=import-error,unused-import
    from win32process import GetWindowThreadProcessId  # noqa=F401 # pylint: disable=import-error,unused-import

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
        self.active_application = "system"

    def start(self) -> None:
        while True:
            time.sleep(3)
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
