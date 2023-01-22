extends Control

export var websocket_url = "ws://localhost:8002"

var _client = WebSocketClient.new()

var ready = false

func _ready():
	_client.connect("connection_closed", self, "_closed")
	_client.connect("connection_error", self, "_closed")
	_client.connect("connection_established", self, "_connected")
	_client.connect("data_received", self, "_on_data")
	
	var err = _client.connect_to_url(websocket_url)
	if err != OK:
		print("Unable to connect")
		set_process(false)

func _closed(was_clean = false):
	print("Closed, clean: ", was_clean)
	set_process(false)

func _connected(proto = ""):
	print("Connected with protocol: ", proto)
	ready = true
	

func _on_data():
	var data = _client.get_peer(1).get_packet().get_string_from_utf8()
	print("Got data from server: ", data)
	$Label.text = data

func _process(delta):
	_client.poll()
	if ready:
		var data = {
			"type": "control_input",
			"translate": Input.get_axis("move_left", "move_right")
		}
		_client.get_peer(1).put_packet(JSON.print(data).to_ascii())
