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
	
	
#	var translation: Vector3 = Vector3.FORWARD
	
	var translation := Vector3(
		Input.get_axis("move_right", "move_left"),
		Input.get_axis("move_forward", "move_back"),
		Input.get_axis("move_down", "move_up")
	)
	
	var rotation := Vector3(
		Input.get_axis("pitch_up", "pitch_down"),
		Input.get_axis("roll_right", "roll_left"),
		Input.get_axis("yaw_right", "yaw_left")
	)
	
	rotation *= 0.3
	rotation.z *= 1.2
	translation.y *= abs(pow(translation.y, 1.0))
	translation.x *= 1.5
	
	$InputLabel.text = "%s : %s" % [str(translation), str(rotation)]
	
	$"%TranslationXValue".text = str("%0.3f" % translation.x)
	$"%TranslationYValue".text = str("%0.3f" % translation.y)
	$"%TranslationZValue".text = str("%0.3f" % translation.z)
	
	$"%RotationXValue".text = str("%0.3f" % rotation.x)
	$"%RotationYValue".text = str("%0.3f" % rotation.y)
	$"%RotationZValue".text = str("%0.3f" % rotation.z)
	
	var servo_pwm = $ServoPWMSlider.value
	$ServoCurrentPWMLabel.text = str(servo_pwm)
	
	translation *= Vector3(1.0, 5.0, 3.0)
	$InputLabel.text = str(translation)
	
	if ready:
		var data = {
			"type": "control_input",
			"translate": Input.get_axis("move_left", "move_right"),
			"translation": [translation.x, translation.y * 5.0, translation.z * 3.0],
			"rotation": [rotation.x, rotation.y, rotation.z],
			"direct_motors": $DirectMotorsButton.pressed,
			"servo_pwm": int(servo_pwm),
		}
		_client.get_peer(1).put_packet(JSON.print(data).to_ascii())
