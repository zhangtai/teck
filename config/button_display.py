from datetime import datetime


def time_display() -> str:
    return datetime.now().strftime("%H:%M")


def today_time_remains(hour_in_24, minute: int) -> str:
    today = datetime.today()
    start_time = datetime(today.year, today.month, today.day, hour_in_24, minute)
    remain_seconds = (start_time - datetime.now()).seconds

    if remain_seconds > 60 * 60:
        hours = str(int((start_time - datetime.now()).seconds / 60 / 60)).zfill(2)
        minutes = str(int((start_time - datetime.now()).seconds / 60 % 60)).zfill(2)
        display = f"{hours}:{minutes}"
    elif remain_seconds > 0:
        minutes = str(int((start_time - datetime.now()).seconds / 60 % 60)).zfill(2)
        display = f"00:{minutes}"
    else:
        display = "Started"

    return display
