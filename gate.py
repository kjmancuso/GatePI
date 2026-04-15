import atexit
import logging
import os
import sys

import flask
import RPi.GPIO as GPIO

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)
log = logging.getLogger(__name__)

app = flask.Flask(__name__)
# Set SECRET_KEY env var for persistent sessions across restarts.
# Without it, sessions reset on every restart (acceptable for home use).
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))

RELAY = {'FAR': 21, 'MIDDLE': 20, 'NEAR': 26}
GATE = RELAY['FAR']

GPIO.setmode(GPIO.BCM)
GPIO.setup(list(RELAY.values()), GPIO.OUT)


def cleanup():
    GPIO.cleanup()


atexit.register(cleanup)


def load_password():
    password_file = os.environ.get('PASSWORD_FILE', 'password')
    try:
        with open(password_file) as fp:
            return fp.readline().rstrip()
    except FileNotFoundError:
        log.error("Password file '%s' not found. Create it with your password.", password_file)
        sys.exit(1)
    except OSError as e:
        log.error("Cannot read password file '%s': %s", password_file, e)
        sys.exit(1)


password_read = load_password()


@app.route('/', methods=['GET'])
def index():
    # Accept password via query param to establish a session.
    # iOS webclip URLs can include ?password=xxx to auto-authenticate.
    password = flask.request.args.get('password', '')
    if password:
        if password == password_read:
            flask.session['authenticated'] = True
        else:
            log.warning("Failed auth attempt from %s", flask.request.remote_addr)
            flask.abort(403)

    if not flask.session.get('authenticated'):
        flask.abort(403)

    action = flask.request.args.get('action', 'STATUS')
    if action == 'OPEN':
        GPIO.output(GATE, GPIO.HIGH)
        log.info("Gate OPENED from %s", flask.request.remote_addr)
    elif action == 'CLOSE':
        GPIO.output(GATE, GPIO.LOW)
        log.info("Gate CLOSED from %s", flask.request.remote_addr)
    elif action != 'STATUS':
        flask.abort(400)

    status = GPIO.input(GATE)
    status_text = "OPEN" if status else "CLOSED"

    return flask.render_template('index.html', status_text=status_text)


if __name__ == '__main__':
    app.run('0.0.0.0', port=int(os.environ.get('PORT', 9130)))
