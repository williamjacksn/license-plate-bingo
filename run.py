import notch
import signal
import sys
import license_plate_bingo.app

log = notch.make_log('license-plate-bingo-entrypoint')

def handle_sigterm(_signale, _frame):
    sys.exit()


signal.signal(signal.SIGTERM, handle_sigterm)
license_plate_bingo.app.main()
