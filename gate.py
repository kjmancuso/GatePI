import atexit
import flask
import flask_bootstrap
import RPi.GPIO as GPIO

app = flask.Flask(__name__)
flask_bootstrap.Bootstrap(app)


def cleanup():
    GPIO.cleanup()


atexit.register(cleanup)

RELAY = {'FAR': 21,
         'MIDDLE': 20,
         'NEAR': 26}

GATE = RELAY['FAR']

GPIO.setmode(GPIO.BCM)

GPIO.setup(list(RELAY.values()), GPIO.OUT)

with open('password', 'r') as fp:
    password_read = fp.readline().rstrip()


@app.route('/', methods=['GET'])
def index():
    password = flask.request.args.get('password', '')
    if password != password_read:
        flask.abort(403)
    action = flask.request.args.get('action', 'CLOSE')
    if action == 'OPEN':
        GPIO.output(GATE, GPIO.HIGH)
    elif action == 'CLOSE':
        GPIO.output(GATE, GPIO.LOW)

    status = GPIO.input(GATE)

    if status:
        status_text = "OPEN"
    elif not status:
        status_text = "CLOSED"

    return flask.render_template('index.html', status_text=status_text,
                                 password=password_read)


if __name__ == '__main__':
    app.run('0.0.0.0', port=80)
