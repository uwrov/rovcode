Make sure to add Godot to your path (or whatever the equivalent is on your operating system)

On macOS, to ensure you can run Godot stuff from command line:

```ln -s /Applications/Godot.app/Contents/MacOS/Godot /usr/local/bin/godot```


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
