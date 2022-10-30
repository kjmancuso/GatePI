GatePI
======

This is a simple application to activate a relay on a raspberry pi to short out the hold open circuit on a gate control board.

Hardware
--------
The hardware I used for this is as follows:
* Raspberry Pi 4
* Electronics-Salon RPi Relay Hat
* Raspberry Pi Foundation PoE Hat
* Geekworm riser accessories
* Liftmaster LA400 gate control board

Pin config
----------
The pins used for the relay hat are as follows:

|Location|Pin Number|
|---|---|
|Furthest from Ethernet|21|
|Middle Relay|20|
|Closest to Ethernet|26|

Usage
-----

1. Create a file in the script directory called `password` with the password you want to use
2. Change the script to set the correct pin for usage in the `GATE` variable
3. Run the business

Authentication notes
--------------------

Uses `GET` parameter to use auth as IOS Safari does not cache user:pass@host formatting when adding a webclip.

Autostart
---------
The systemd unit file I used is as follows:
```systemd
[Unit]
Description=Gate

[Service]
WorkingDirectory=/opt/gate/
TimeoutStartSec=0
Restart=always
ExecStart=/usr/local/bin/waitress-serve --host 0.0.0.0 --port 9130 gate:app

[Install]
WantedBy=multi-user.target
```