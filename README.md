GatePI
======

A simple application to activate a relay on a Raspberry Pi to short out the hold-open circuit on a Liftmaster LA400 gate control board. Provides a minimal web UI optimized for use as an iOS home screen webclip.

Hardware
--------
* Raspberry Pi 4
* Electronics-Salon RPi Relay Hat
* Raspberry Pi Foundation PoE Hat
* Geekworm riser accessories
* Liftmaster LA400 gate control board

Pin config
----------
The pins used for the relay hat are as follows:

| Location               | Pin Number |
|------------------------|------------|
| Furthest from Ethernet | 21         |
| Middle Relay           | 20         |
| Closest to Ethernet    | 26         |

Setup
-----

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `password` file in the working directory:
   ```
   echo 'yourpassword' > /opt/gate/password
   chmod 600 /opt/gate/password
   ```

3. (Optional) Edit `gate.py` to change the `GATE` variable if using a different relay pin.

4. Install and start the systemd service:
   ```
   sudo cp gate.service /etc/systemd/system/
   sudo systemctl enable gate
   sudo systemctl start gate
   ```

Usage
-----

Point your iOS webclip at `http://<pi-ip>:9130/?password=yourpassword`.

The first visit authenticates and sets a session cookie. Subsequent visits (OPEN/CLOSE button taps) use the session without re-sending the password. Sessions persist until the server restarts.

For persistent sessions across restarts, set the `SECRET_KEY` environment variable in the service file:
```
Environment=SECRET_KEY=somethinglong
```

Authentication notes
--------------------

Uses a GET parameter for initial auth because iOS Safari does not cache `user:pass@host` formatting when adding a webclip. After the first visit, a session cookie handles authentication — the password is no longer sent with each request.

Environment variables
---------------------

| Variable        | Default    | Description                                      |
|-----------------|------------|--------------------------------------------------|
| `SECRET_KEY`    | (random)   | Flask session key. Set for persistence across restarts. |
| `PASSWORD_FILE` | `password` | Path to the password file.                       |
| `PORT`          | `9130`     | Port for the dev server (`__main__` only).       |
