import signal
import sys
from types import FrameType

import notch

import license_plate_bingo.app

notch.configure()


def handle_sigterm(_signal: int, _frame: FrameType | None) -> None:
    sys.exit()


signal.signal(signal.SIGTERM, handle_sigterm)
license_plate_bingo.app.main()
