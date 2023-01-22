On macOS, to ensure you can run Godot stuff from command line:

```ln -s /Applications/Godot.app/Contents/MacOS/Godot /usr/local/bin/godot```


Test websocket connection locally:

```python3 -m websockets ws://localhost:8001/```


Notes:
- need python3 in your path in order to launch properly
- physical.py contains stubs
- onboard.py should do heavy lifting for onboard code
- TODO: need to state what packages are needed
