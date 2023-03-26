# ROV Code
## Setup
Install Godot, and make sure to add Godot to your path (or whatever the equivalent is on your operating system). 

If you are getting a 'file not found' error around subprocesses, recheck that Godot is in your path. Otherwise contact Alnis with other errors. 

On macOS, to ensure you can run Godot stuff from command line (this pretends to add Godot to path):

```ln -s /Applications/Godot.app/Contents/MacOS/Godot /usr/local/bin/godot```

On Windows, look for your 'Environment Variables' setting menu, click on the Path variable, and add a line with the directory path to your Godot executable. (Your executable needs to be named godot.exe - rename if necessary.)

On Linux... good luck, but you probably know what you're doing. (Please add documentation if you figure it out.)

Test websocket connection locally:

```python3 -m websockets ws://localhost:8001/```

install numpy (pip3 install numpy)
install websockets (pip3 install websockets)

To get Logitech F310 controller working with macOS, check this out:
https://gist.github.com/jackblk/8138827afd986f30cf9d26647e8448e1

Notes:
- need python3 in your path in order to launch properly
- physical.py contains stubs
- onboard.py should do heavy lifting for onboard code
- TODO: need to state what packages are needed

## Running the System
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