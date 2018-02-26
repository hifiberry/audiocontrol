# AudioController

## Purpose
AudioController enabled multiple audio applications to coexist on the 
same server and provides a central control to all of them.

## Single source playback
When having multiple audio sources like Airplay, Bluetooth and Spotify, 
they all run in independently. If you're playing a song from your iPhone
via Airplay and you start Spotify, the Airplay playback will still be
active. Listening to two different audio sources usually isn't what you
want to to. 
That's where AudioController helps you. It can detect the playback 
status of different sources and stop playback of active sources if a new
source becomes active. This means it will automatically stop Airplay when
you start Spotify playback.

## Backends
AudioController needs to understand the specifics of an audio source. 
To support different sources, AudioController uses so-called "backends" 
that represent a specific music service running on the system. The 
simplest backend does only provide a service to stop playback for this
audio source. 

### Airplay

Airplay is usually implemented using shairport-sync. This backend allows 
to control shairport-sync. However, as there is functionality to stop
playback of an audio source, we use a quite aggressive way to stop 
playback - by killing the shairport-sync process. 
This means you have to configure systemd to automatically restart 
shairport-sync once it has been killed.

A configuration could look like this:

```
[Unit]
Description=Shairport Sync - AirPlay Audio Receiver
After=sound.target
Requires=avahi-daemon.service
After=avahi-daemon.service
Wants=network-online.target
After=network.target network-online.target

[Service]
ExecStart=/usr/local/bin/shairport-sync -c /etc/shairport-sync.conf
User=shairport-sync
Group=shairport-sync
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### Spotify

To control Spotify, the spotify backend needs to be connected to the 
backend servcie first. To do this, go to
[http://spotify-registration.local:14281/]

When the application has been connected it receives a Spotify 
authorisation code that is used to control Spotify playback. This is 
only stored locally. No Spotify data are send somewhere else.


### MPD

MPD - the music player daemon is very popular for users with a collection
of music files stored locally. mpd comes with the control tool mpc that 
will be used by audiocontrol. 


## Notification interface
AudioController creates a named pipe /tmp/audiostatus.
Services can report their playback status into this pipe

Right now only "START" and "STOP" messages are implemented

### Notification script
As the communication is handled via fifos, writes can block if the 
AudioController isn't running. Therefore it is recommended to set a 
timeout and abort the write if it isn't finished after the timeout.
This can be done simply in a shell script:

```
#!/bin/bash
/bin/echo $*  > /tmp/audiostatus &
sleep 2
kill $!
```

### Shairport

Shairport can call an external script when playback starts on stops.
This can be used to post the START/STOP messages to the named pipe. You
need to add this to the sessioncontrol section of your shairport-sync.conf 
file:

```
sessioncontrol =
{
  run_this_before_play_begins = "/opt/hifiberry/bin/write-status START AIRPLAY";
  run_this_after_play_ends = "/opt/hifiberry/bin/write-status STOP AIRLAY"; 
  wait_for_completion = "no";
  allow_session_interruption = "yes";
  session_timeout = 20;
};
```

### Spotifyd

Similar to shairport, spotifyd can also call external programs on 
play/pause. Put the following lines in the "[global] section of the 
Spotify configuration file 

```
[global]
onstart = /opt/hifiberry/bin/write-status START SPOTIFY
onstop = /opt/hifiberry/bin/write-status STOP SPOTIFY
```

## Controllers

While the main functionality of a backend is the playback of music, a
controller is used to send and recieve control messages. A controller 
can actively send command (e.g. based on a keypress, rotary controller,
infrared remote or many more). A controller can also just listen to 
events (e.g. meta data of the song currently playing or the volume 
level). If can also combine both

### Nuimo

The Senic Nuimo is a rotary controller with additional touch 
functionality that can send command via Bluetooth LE.
The Nuimo module allows to use the rotary control for volume control
and the touch panel to seek forward and backward

### Keyboard

The Keyboard can map key pressed to control actions. Ideally you will 
use multimedia keys or function keys for this. Many RF remote controls 
that use an USB dongle also act as a keyboard and can be integrated 
using this controller

### ALSAVolume

ALSAVolume provides a bi-directional control to an ALSA mixer device. 
It can directly control the volume, but also report changes that were
made by other programs.


## Running Audio control

As AudioControl has to control different processed that might run under 
their own user id, the easiest way is to run it as root. 
