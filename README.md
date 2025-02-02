# ROV Code
## Setup

**Warning: if you are connected via ethernet to a router without internet connection (i.e., have the computer as a part of the surface station), you may run into weird errors, even if you have a network connection via a separate wifi connection. Therefore, make sure you are connected to the internet, and not connected to any networks without internet, to avoid issues during setup.**

### Godot Installation

Install Godot, and make sure to add Godot to your path (or whatever the equivalent is on your operating system).

This project is currently made with Godot 3.5.1, standard version (Mono/C# not needed): https://github.com/godotengine/godot/releases/tag/3.5.1-stable

If you are getting a 'file not found' error around subprocesses, recheck that Godot is in your path. Otherwise contact Alnis with other errors. 

On macOS, to ensure you can run Godot stuff from command line (this pretends to add Godot to path):

```ln -s /Applications/Godot.app/Contents/MacOS/Godot /usr/local/bin/godot```

On Windows, look for your 'Environment Variables' setting menu, click on the Path variable, and add a line with the directory path to your Godot executable. (Your executable needs to be named godot.exe - rename if necessary.)

On Linux:

```
wget https://downloads.tuxfamily.org/godotengine/3.5.1/Godot_v3.5.1-stable_x11.64.zip
unzip Godot_v3.5.1-stable_x11.64.zip
cp Godot_v3.5.1-stable_x11.64 ~/.local/bin/godot
```
This will download Godot and add it to `PATH` (eg. you can call `godot` to launch it).

### Python Installation

Make sure Python is installed & added to path.

Also, make sure Visual Studio Code's Python package is installed.

macOS: TODO

Windows:
* Get installer (3.12.2) from here: https://www.python.org/downloads/release/python-3122/
* Make sure "Add python.exe to path" is checked
* Default installation is OK
* Alternatively... you can type `python` into a terminal and it will launch the Microsoft Store, where you can try pressing "Get" for python. Maybe that will work (it sometimes throws an error).

Linux: Use deadsnakes PPA (also installs pip)
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-pip
```
This will work for Ubuntu and other Debian-based distros. On Fedora, use `dnf` instead of `apt`, on Arch, use `pacman` instead, etc.

Also make sure you have the following packages:

* numpy: `pip3 install numpy`
* websockets `pip3 install websockets`

Test websocket connection locally:

```python3 -m websockets ws://localhost:8001/```

### Other Notes

To get Logitech F310 controller working with macOS, check this out:
https://gist.github.com/jackblk/8138827afd986f30cf9d26647e8448e1

Notes:
- need python3 in your path in order to launch properly
- physical.py contains stubs
- onboard.py should do heavy lifting for onboard code
- TODO: need to state what packages are needed

## Running the System

Connecting to the physical ROV:
`ssh pi`
Password: `raspberry` (yes this is the default)

Note on cameras:
```sh
pi@main:~/raspivid_mjpeg_server $ v4l2-ctl -d 4 -c exposure_auto=1,exposure_absolute=300,brightness=0,gain=100
pi@main:~/raspivid_mjpeg_server $ v4l2-ctl -d 4 -v width=1024,height=768,pixelformat='MJPG' --stream-mmap --stream-to - | raspivid_mjpeg_server -p 8554
pi@main:~/raspivid_mjpeg_server $ v4l2-ctl -d 0 -v width=1024,height=768,pixelformat='MJPG' --stream-mmap --stream-to - | raspivid_mjpeg_server -p 8555
```

You can run all of this with:
```sh
./start_cameras.sh > /dev/null 2>&1 &
```

(Bookmarked on surface station Chrome)
Front cam: http://172.25.250.1:8554/
Down cam: http://172.25.250.1:8555/

Better balance of low light performance (~20 fps):
```sh
pi@main:~/raspivid_mjpeg_server $ v4l2-ctl -d 4 -c exposure_auto=1,exposure_absolute=500,brightness=32,contrast=32,gamma=100,gain=100,saturation=128
pi@main:~/raspivid_mjpeg_server $ v4l2-ctl -d 4 -v width=1024,height=768,pixelformat='MJPG' --stream-mmap --stream-to - | raspivid_mjpeg_server
```


### Physical ROV
On the ROV, use the terminal to run launch_onboard_physical.py. The command is `python3 launch_onboard_physical.py`. (Run this command from the directory of the file.)
On the surface, open the repository in VSCode and open launch_surface.py. Press the Play button to run the file. 

### Simulated ROV
On the surface (or any computer), open the repository in VSCode and open launch_full_simulation.py. Press the Play button to run the file. 

### Testing Networking
If you would like to test networking without actually running the physical ROV, run launch_surface.py on one computer, and run launch_onboard_simulation.py on another computer.

## Documentation
See in-line comments for implementation-related documentation.

The main loop for the surface is `surface.py`, and the main loop for onboard is `onboard.py`. Everything is called from there. 

### Overview of `surface.py`
This file initializes the core, interface, and task code. It then starts the appropriate servers and links handlers for websocket communication. 

### Overview of `onboard.py`
This file initializes onboard communication. This also parses commands and forwards them to the ROV. The code here is shared for physical and simulated ROVs. 





Input in z-up space, output in Godot visual
Control stick yaw left (+z rotation) -> model visually moves in -x rotation
Control stick roll left (+y rotation) -> model visually moves in -z rotation



Onshape space:
+x rotation -> -z
+z rotation -> -x result
