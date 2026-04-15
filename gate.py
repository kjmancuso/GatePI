import atexit
import logging
import os
import sys
import time

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
        log.error(f"Password file '{password_file}' not found. Create it with your password.")
        sys.exit(1)
    except OSError as e:
        log.error(f"Cannot read password file '{password_file}': {e}")
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
            log.warning(f"Failed auth attempt from {flask.request.remote_addr}")
            flask.abort(403)

    if not flask.session.get('authenticated'):
        flask.abort(403)

    status = GPIO.input(GATE)
    status_text = "OPEN" if status else "CLOSED"

    response = flask.make_response(flask.render_template('index.html', status_text=status_text))
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/', methods=['POST'])
def action():
    if not flask.session.get('authenticated'):
        flask.abort(403)

    act = flask.request.form.get('action', '')
    if act == 'OPEN':
        GPIO.output(GATE, GPIO.HIGH)
        log.info(f"Gate OPENED from {flask.request.remote_addr}")
    elif act == 'CLOSE':
        GPIO.output(GATE, GPIO.LOW)
        log.info(f"Gate CLOSED from {flask.request.remote_addr}")
    else:
        flask.abort(400)

    return flask.redirect(flask.url_for('index'))


@app.route('/pulse', methods=['GET'])
def pulse():
    password = flask.request.args.get('password', '')
    if password:
        if password == password_read:
            flask.session['authenticated'] = True
        else:
            log.warning(f"Failed auth attempt from {flask.request.remote_addr}")
            flask.abort(403)

    if not flask.session.get('authenticated'):
        flask.abort(403)

    GPIO.output(GATE, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(GATE, GPIO.LOW)
    log.info(f"Gate PULSED from {flask.request.remote_addr}")

    return ('', 204)


if __name__ == '__main__':
    app.run('0.0.0.0', port=int(os.environ.get('PORT', 9130)))
