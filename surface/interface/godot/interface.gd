extends Control

export var websocket_url = "ws://localhost:8002"

var _client = WebSocketClient.new()

var ready = false

var rov_orientation: Basis
var target_orientation: Basis
#var last_time = 0.0
#var time = 0.0

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
	

var suspicous_gyro_values = 0

var gravity_calibration_rotation = Vector3.ZERO

func _on_data():
	var data = _client.get_peer(1).get_packet().get_string_from_utf8()
	print("Got data from server: ", data)
	var parsed = JSON.parse(data).result
#	$Label.text = data
#	$Label.text = str(parsed)
	var acc  = parsed["accelerometer"]
	var gyro = parsed["gyroscope"]
#	$Label.text = str(acc)
	# IMU: x left, y forward, z up
	# ROV: 
	$Label.text = str(gyro)
	if gyro[0] == null:
		$LabelDebug.text = str(gyro)
		return
	var gyrotext = "%.5f %.5f %.5f\n%.5f %.5f %.5f %.5f" % [acc[0], acc[1], acc[2], gyro[0], gyro[1], gyro[2], gyro[3]]
	$Label.text = gyrotext
	
	if not acc[0]:
		$LabelDebug.text = gyrotext
	
	var prev_rov_orientation = rov_orientation
	
	# convert quaternion from IMU to basis
	rov_orientation = Basis(Quat(gyro[0], gyro[2], gyro[1], gyro[3]))
	
	# swap yaw and pitch
	var old_x = rov_orientation.x
	var old_y = rov_orientation.y
	rov_orientation.x = old_y
	rov_orientation.y = old_x
	
	# rotate to correct "up" direction
	rov_orientation = rov_orientation.rotated(Vector3(0.0, 0.0, -1.0), PI / 2)
	
	# rov_orientation is now in y-up space
	
	
	var diff = (
		abs(prev_rov_orientation.x.angle_to(rov_orientation.x)) +
		abs(prev_rov_orientation.y.angle_to(rov_orientation.y)) + 
		abs(prev_rov_orientation.z.angle_to(rov_orientation.z))
	)
	
	$LabelDiff.text = str(diff)
	
	# TODO: for the future: what if we get a bad value on the 10th loop?
	if diff > 1.0 and suspicous_gyro_values < 10:
		rov_orientation = prev_rov_orientation
		suspicous_gyro_values += 1
		$LabelDebug2.text = "Last suspicious count: " + str(suspicous_gyro_values)
		$LabelDiff.modulate = Color.red
	else:
		suspicous_gyro_values = 0
		$LabelDiff.modulate = Color.white
	
#	if Input.is_action_pressed("calibrate_gravity"):
#		var imu_gravity = Vector3(acc[0], acc[1], acc[2])
	
	if gravity_calibration_rotation:
		rov_orientation = rov_orientation.rotated(gravity_calibration_rotation, gravity_calibration_rotation.length())
	
	
	var euler = rov_orientation.get_euler()

	$Label4.text = "Euler X: " + str(euler.x) + "\nEuler Y: " + str(euler.y) + "\nEuler Z: " + str(euler.z)
	$"%ROVProxy".transform.basis = rov_orientation
	

func _process(delta):
	
#	time += delta
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
	
	$LabelSASState.text = "SAS state: inactive"
	
	var rotation_boost = Vector3.ZERO
	
	# TODO: should this be "just pressed" ?
	if Input.is_action_pressed("save_orientation"):
#		$LabelSASState.text = "SAS state: saving"
#		pass
		target_orientation = rov_orientation
	
	if Input.is_action_pressed("hold_orientation"):
#		$LabelSASState.text = "SAS state: holding - "
#		var y_ctrl = -rov_orientation.get_euler().y
#		y_ctrl *= 0.4
#		y_ctrl = clamp(y_ctrl, -0.2, 0.2)
#		rotation_boost += Vector3(0.0, 0.0, y_ctrl)
#		$LabelSASState.text += str(y_ctrl)
#		pass
		
		
		rotation_boost = Vector3.ZERO

		var x_displacement = rov_orientation.x.cross(target_orientation.x)
		var y_displacement = rov_orientation.y.cross(target_orientation.y)
		var z_displacement = rov_orientation.z.cross(target_orientation.z)

#		var temp = x_displacement
#		x_displacement = z_displacement
#		z_displacement = temp

#		x_displacement *= -1
#		y_displacement *= -1
#		z_displacement *= -1

		# TODO: fix proportional magintued if difference is more than 180 degrees

		var proportional: Vector3 = x_displacement + y_displacement + z_displacement
		
		
		
		var diff = (
			abs(rov_orientation.x.angle_to(target_orientation.x)) +
			abs(rov_orientation.y.angle_to(target_orientation.y)) + 
			abs(rov_orientation.z.angle_to(target_orientation.z))
		)
		
		proportional = proportional.normalized() * diff
	

#		rotation_boost += proportional * 1.0
		rotation_boost = Vector3(proportional.x, -proportional.z, proportional.y) * .2
		rotation_boost.x = clamp(rotation_boost.x, -0.2, 0.2)
		rotation_boost.y = clamp(rotation_boost.y, -0.2, 0.2)
		rotation_boost.z = clamp(rotation_boost.z, -0.2, 0.2)

		$Label3.text = "%.5f %.5f %.5f" % [rotation_boost.x, rotation_boost.y, rotation_boost.z]

#		rotation += rotation_boost
	
	var manipulator_pwm = 1500
	if Input.is_action_pressed("manipulator_close"):
		manipulator_pwm -= 50
	if Input.is_action_pressed("manipulator_open"):
		manipulator_pwm += 100
	
	
#	rotation.y *= 0.3
	rotation.x *= pow(abs(rotation.x), 1.0)
	rotation.y *= pow(abs(rotation.y), 1.0)
	rotation.z *= pow(abs(rotation.z), 1.0)
	
	rotation *= 0.7
	rotation.y *= 0.4
	
	rotation += rotation_boost
	
#	rotation.z *= 1.2
	translation.y *= abs(pow(translation.y, 1.0))
	#translation.x *= 0
	
#	translation *= 0.4

	translation.x *= -1.0
	
	$InputLabel.text = "%s : %s" % [str(translation), str(rotation)]
	
	$"%TranslationXValue".text = str("%0.3f" % translation.x)
	$"%TranslationYValue".text = str("%0.3f" % translation.y)
	$"%TranslationZValue".text = str("%0.3f" % translation.z)
	
	$"%RotationXValue".text = str("%0.3f" % rotation.x)
	$"%RotationYValue".text = str("%0.3f" % rotation.y)
	$"%RotationZValue".text = str("%0.3f" % rotation.z)
	
#	var servo_pwm = $ServoPWMSlider.value
	var servo_pwm = manipulator_pwm
	$ServoCurrentPWMLabel.text = str(servo_pwm)
	
	translation *= Vector3(1.0, 2.5, 2.5)
#	translation *= Vector3(1.0, 5.0, 3.0)
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
