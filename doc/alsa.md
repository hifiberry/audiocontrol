# Controlling volume via ALSA

Most sound cards provide mixer controls via the ALSA API. You can use tools like alsamixer to control the volume, 
but you can also use audiocontrol for this.

ALSA mixer configuration is very simple:

```
[alsavolume]
alsacontrol=DSPVolume
```

The only option is the name of the ALSA mixer control name. The easiest way to find this, is the amixer command. Just run amixer 
without any options and it will display the known mixer controls:

```
# amixer
Simple mixer control 'DSPVolume',0
  Capabilities: volume
  Playback channels: Front Left - Front Right
  Capture channels: Front Left - Front Right
  Limits: 0 - 255
  Front Left: 89 [35%]
  Front Right: 89 [35%]
Simple mixer control 'Softvol',0
  Capabilities: volume
  Playback channels: Front Left - Front Right
  Capture channels: Front Left - Front Right
  Limits: 0 - 255
  Front Left: 255 [100%]
  Front Right: 255 [100%]
```

In this case, we're using the first control named DSPVolume. Often the master volume control is named like "Master", 
"Playback" or similar. 
