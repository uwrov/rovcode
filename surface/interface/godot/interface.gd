extends Control

export var websocket_url = "ws://localhost:8002"

# help option popup (not implemented)
onready var popup = $MoreInfo/InfoPopUp
onready var popup_label = $MoreInfo/InfoPopUp/VBoxContainer/SeeMore

# popup to change manipulator
onready var change_popup = $ChangeManipulator/popup 
onready var option_label = $ChangeManipulator/popup/VBoxContainer/mOptions

var option_index = 0
var options_list = ["Manipulator 1", "Manipulator 2", "Manipulator 3"] #increase for total available options
var total_options = options_list.size()
var awaiting_confirmation = false #must be true to actually change the manipulator

var _client = WebSocketClient.new()

var ready = false

var rov_orientation: Basis
var target_orientation: Basis
#var last_time = 0.0
#var time = 0.0
var power_scale := 1.8 setget set_power_scale
var power_adjust_hold_time := 0.0
var power_repeat_delay := 0.2  # Seconds between repeated steps
var manipulator_repeat_delay := 0.5
var manipulator_index = 1
var totalManipulators = 5

var mode_names = {
	1: "Dual Axis Manipulator Mode",
	2: "Single Toggle Manipulator Mode Top",
	3: "Single Toggle Manipulator Mode Bottom",
	4: "Thermistor Manipulator Mode",
	5: "Syringe Manipulator Mode"
}

var x_button = {
	1: "close bottom manipulator",
	2: "spin medium",
	3: "spin medium",
	4: "bottom close",
	5: "top open"
}

var y_button = {
	1: "open bottom manipulator",
	2: "spin fast",
	3: "spin fast",
	4: "bottom open",
	5: "top close"
}

var b_button = {
	1: "dont know - impact both top/bottom",
	2: "spin slow",
	3: "spin slow",
	4: "top close",
	5: "N/A"
}

var a_button = {
	1: "opposite of B (?)",
	2: "top manipulator power change",
	3: "bottom manipulator power change",
	4: "top open",
	5: "N/A"
}

var light_on = false

func _ready():
	_client.connect("connection_closed", self, "_closed")
	_client.connect("connection_error", self, "_closed")
	_client.connect("connection_established", self, "_connected")
	_client.connect("data_received", self, "_on_data")
	
	var err = _client.connect_to_url(websocket_url)
	if err != OK:
		print("Unable to connect")
		set_process(false)
		
	popup.hide()
	change_popup.hide()

func _closed(was_clean = false):
	print("Closed, clean: ", was_clean)
	set_process(false)

func _connected(proto = ""):
	print("Connected with protocol: ", proto)
	ready = true
	

var suspicous_gyro_values = 0

#var gravity_calibration_rotation = Vector3.ZERO

func basis_xform(operator: Basis, input: Basis):
	return Basis(
		operator.xform(input.x),
		operator.xform(input.y),
		operator.xform(input.z)
	)

var derivative = Vector3.ZERO
var imu_last_time = -1.0

func set_power_scale(value: float) -> void:
	power_scale = clamp(value, 0.05, 3.5)
	$PowerBoost.text = "Power scale: %.3f" % power_scale

func _on_data():
	var data = _client.get_peer(1).get_packet().get_string_from_utf8()
	print("Got data from server: ", data)
	var parsed = JSON.parse(data).result
#	$Label.text = data
#	$Label.text = str(parsed)
# warning-ignore:unused_variable
	var acc  = parsed["accelerometer"]
	var gyro = parsed["quaternion"]
#	$Label.text = str(acc)
	# IMU: x left, y forward, z up
	# ROV: x left, y backward, z up
	# Godot: x left, y up, z forward
	if gyro[0] == null:
		$Label.text = str(gyro)
		#$LabelDebug.text = str(gyro)
		return
	# var gyrotext = "%.5f %.5f %.5f\n%.5f %.5f %.5f %.5f" % [acc[0], acc[1], acc[2], gyro[0], gyro[1], gyro[2], gyro[3]]
	# $Label.text = gyrotext
	
		# if not acc[0]:
		# 	$LabelDebug.text = gyrotext

	var prev_rov_orientation = rov_orientation
	
	# convert quaternion from IMU to basis
	rov_orientation = Basis(Quat(gyro[0], gyro[2], gyro[1], gyro[3]))

	# swap yaw and pitch
	var old_x = rov_orientation.x
	var old_y = rov_orientation.y
	rov_orientation.x = -old_y
	rov_orientation.y = -old_x
	
	# rotate to correct "up" direction
	rov_orientation = rov_orientation.rotated(Vector3(0.0, 0.0, -1.0), PI / 2)
	
	# https://stackoverflow.com/a/55718733
	# mat3x3 ros_to_unity = /* construct this by hand by mapping input axes to output axes */;
	# mat3x3 unity_to_ros = ros_to_unity.inverse();
	# quat q_ros = ...;
	# mat3x3 m_unity = ros_to_unity * mat3x3(q_ros) * unity_to_ros;
	# quat q_unity = mat_to_quat(m_unity);
	
	# x left, y forward, z up
	
#	var godot_to_gyro: Basis = Basis(Vector3(1.0, 0.0, 0.0), Vector3(0.0, 0.0, 1.0), Vector3(0.0, 1.0, 0.0))
#	var gyro_to_godot: Basis = godot_to_gyro.inverse()
#	var gyro_basis: Basis = Basis(Quat(gyro[0], gyro[1], gyro[2], gyro[3]))
##	var godot_basis = basis_xform(godot_to_gyro, basis_xform(gyro_basis, gyro_to_godot))
##	var godot_basis = basis_xform(godot_to_gyro, basis_xform(gyro_basis, gyro_to_godot))
#	var godot_basis = basis_xform(gyro_to_godot, gyro_basis)
#	rov_orientation = godot_basis
	
	
	# rov_orientation is now in y-up space
	
	
	var diff = (
		abs(prev_rov_orientation.x.angle_to(rov_orientation.x)) +
		abs(prev_rov_orientation.y.angle_to(rov_orientation.y)) + 
		abs(prev_rov_orientation.z.angle_to(rov_orientation.z))
	)
	
	var axis = (
		prev_rov_orientation.x.cross(rov_orientation.x) +
		prev_rov_orientation.y.cross(rov_orientation.y) + 
		prev_rov_orientation.z.cross(rov_orientation.z)
	).normalized()
	
	var imu_current_time = OS.get_system_time_msecs() / 1000.0
	var imu_delta = imu_current_time - imu_last_time
	imu_last_time = imu_current_time
	
	derivative = axis * diff / imu_delta
	
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
	
#	if gravity_calibration_rotation:
#		rov_orientation = rov_orientation.rotated(gravity_calibration_rotation, gravity_calibration_rotation.length())
	
	var euler = rov_orientation.get_euler()

	$Label4.text = "Euler X: " + str(euler.x) + "\nEuler Y: " + str(euler.y) + "\nEuler Z: " + str(euler.z)
	$"%ROVProxy".transform.basis = rov_orientation


var rotation_boost_i = Vector3.ZERO

var error_integral = Vector3.ZERO

var spinPWM = 1500
func _process(delta):
	
#	time += delta
	_client.poll()
	
	var holding_increase := Input.is_action_pressed("power_increase")
	var holding_decrease := Input.is_action_pressed("power_decrease")
	var next_manipulator := Input.is_action_pressed("manipulator_next")
	var prev_manipulator := Input.is_action_pressed("manipulator_previous")

	if holding_increase or holding_decrease:
		power_adjust_hold_time -= delta
		if power_adjust_hold_time <= 0.0:
			if holding_increase:
				set_power_scale(power_scale * 1.1)
			elif holding_decrease:
				set_power_scale(power_scale / 1.1)
			power_adjust_hold_time = power_repeat_delay
	elif next_manipulator or prev_manipulator:
		power_adjust_hold_time -= delta
		if power_adjust_hold_time <= 0.0:
			manipulator_index += 1 if next_manipulator else -1
				
			if manipulator_index > totalManipulators:
				manipulator_index = 1
			elif manipulator_index < 1:
				manipulator_index = totalManipulators
				
			power_adjust_hold_time = manipulator_repeat_delay
			
		$LabelDebug.text = "Manipulator Mode: %s (Index: %d)" % [
			mode_names.get(manipulator_index, "Unknown"), 
			manipulator_index
		]
		$LabelXButton.text = "x - %s manipulator" % [
			x_button.get(manipulator_index, "Unknown"),
		]
		$LabelYButton.text = "y - %s manipulator" % [
			y_button.get(manipulator_index, "Unknown"),
		]
		$LabelBButton.text = "b - %s manipulator" % [
			b_button.get(manipulator_index, "Unknown"),
		]
		$LabelAButton.text = "a - %s manipulator" % [
			a_button.get(manipulator_index, "Unknown"),
		]
	else:
		power_adjust_hold_time = 0  # Reset when not held

	
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
		$LabelSASState.text = "SAS state: saving"
#		pass
		target_orientation = rov_orientation
	
	if Input.is_action_pressed("hold_orientation"):
		$LabelSASState.text = "SAS state: holding - "
#		var y_ctrl = -rov_orientation.get_euler().y
#		y_ctrl *= 0.4
#		y_ctrl = clamp(y_ctrl, -0.2, 0.2)
#		rotation_boost += Vector3(0.0, 0.0, y_ctrl)
#		$LabelSASState.text += str(y_ctrl)
#		pass
		print("foo")
		
		
		rotation_boost = Vector3.ZERO

		var x_displacement = rov_orientation.x.cross(target_orientation.x)
		var y_displacement = rov_orientation.y.cross(target_orientation.y)
		var z_displacement = rov_orientation.z.cross(target_orientation.z)

		$LabelSASState.text += "\nX ctrl: " + str(x_displacement)
		$LabelSASState.text += "\nY ctrl: " + str(y_displacement)
		$LabelSASState.text += "\nZ ctrl: " + str(z_displacement)
		
#		var temp = x_displacement
#		x_displacement = z_displacement
#		z_displacement = temp

#		x_displacement *= -1
#		y_displacement *= -1
#		z_displacement *= -1

		var error: Vector3 = x_displacement + y_displacement + z_displacement
		
		
		
		var diff = (
			abs(rov_orientation.x.angle_to(target_orientation.x)) +
			abs(rov_orientation.y.angle_to(target_orientation.y)) + 
			abs(rov_orientation.z.angle_to(target_orientation.z))
		)
		
		error = error.normalized() * diff
		error_integral += error * delta * 0.5
		error_integral.x = clamp(error_integral.x, -0.1, 0.1)
		error_integral.y = clamp(error_integral.y, -0.1, 0.1)
		error_integral.z = clamp(error_integral.z, -0.1, 0.1)
		
		
		var proportional = error * 0.1
#		var derivative = (error - last_error) * -0.1

		var integral = error_integral * 0.1 * 0.0
		
		var d = -derivative * 0.1 * 0.1
		
		var ctrl = proportional + integral + d
		
		ctrl.x *= 0.9
		ctrl.y *= 1.5
		ctrl.z *= 0.9
	

#		rotation_boost += error * 1.0
#		rotation_boost = Vector3(error.x, -error.z, error.y) * .2
#		rotation_boost = Vector3(-error.x, error.z, error.y) * .1
		rotation_boost = Vector3(-ctrl.x, ctrl.z, ctrl.y)
		rotation_boost.x = clamp(rotation_boost.x, -0.3, 0.3)
		rotation_boost.y = clamp(rotation_boost.y, -0.3, 0.3)
		rotation_boost.z = clamp(rotation_boost.z, -0.3, 0.3)
		
		$LabelSASState.text += "\nPitch boost: " + str(rotation_boost.x)
		$LabelSASState.text += "\nRoll boost: " + str(rotation_boost.y)
		$LabelSASState.text += "\nYaw boost: " + str(rotation_boost.z)
		$LabelSASState.text += "\nErr int: " + str(error_integral)
		$LabelSASState.text += "\nDerivative: " + str(derivative)

		$Label3.text = "%.5f %.5f %.5f" % [rotation_boost.x, rotation_boost.y, rotation_boost.z]

#		rotation += rotation_boost
	
	var bottom_manipulator_pwm = 1500
	var top_manipulator_pwm = 1500

	var OPEN_PWM = 75
	var PWM_COEFFICIENT = 1
	
	if Input.is_action_pressed("get_help"):
		if popup.visible:
				popup.hide()
		else:
			popup.show()
			
	if Input.is_action_pressed("change_manip"):
		if change_popup.visible:
			awaiting_confirmation = false
			change_popup.hide()
		else:
			change_popup.show()
	
	if change_popup.visible:
		# abort manipulator change
		if Input.is_action_pressed("manipulator_right") and Input.is_action_pressed("manipulator_close"): #x & b
			if awaiting_confirmation:
				awaiting_confirmation = false
				option_label.text = "Selection Cancelled. Pick again."
				print("Confirmation Aborted")
		
		if not awaiting_confirmation:
			if Input.is_action_just_pressed("manipulator_right"): # X
				option_index = (option_index + 1) % options_list.size()
				option_label.text = "Selected: " + options_list[option_index]   
				
			if Input.is_action_just_pressed("manipulator_close"): # B
				option_index -= 1
				if option_index < 0:
					option_index = options_list.size() - 1
				option_label.text = "Selected: " + options_list[option_index]
				
			if Input.is_action_just_pressed("manipulator_left"): #y
				awaiting_confirmation = true
				option_label.text = "CONFIRMING: " + options_list[option_index] + "\n(Press 'Change' to Apply)"
		
		# actually change the manipulator
		if awaiting_confirmation and Input.is_action_just_pressed("change_manip"):
			# manipulator_index = option_index + 1 
			# would change manipulator mode to match selected option? (not sure if thats a desired feature tho)
			print("Manipulator Hardware Swapped to: ", manipulator_index)
			
			# actually code the switch here :| (potentially w/ delay), 
			# the manipulator change thing should only disappear when the switch has been complete
			
			change_popup.hide()
			awaiting_confirmation = false
			
	else: #so manipulators wont move but robot can? (will need to test later)
		if manipulator_index == 1:
			if Input.is_action_pressed("manipulator_close"):
				bottom_manipulator_pwm -= OPEN_PWM * PWM_COEFFICIENT * 1.7
			if Input.is_action_pressed("manipulator_open"):
				bottom_manipulator_pwm += OPEN_PWM * PWM_COEFFICIENT * 1.7
			
			if Input.is_action_pressed("manipulator_left"):
				bottom_manipulator_pwm -= 100 * PWM_COEFFICIENT #90 is ok
				top_manipulator_pwm -= 115 * PWM_COEFFICIENT
			if Input.is_action_pressed("manipulator_right"):
				bottom_manipulator_pwm += 115 * PWM_COEFFICIENT #95 is ok
				top_manipulator_pwm += 100 * PWM_COEFFICIENT
			#bottom_manipulator_pwm += (bottom_manipulator_pwm - 1500) * 0.5
			#top_manipulator_pwm += (top_manipulator_pwm - 1500) * 0.5
		elif manipulator_index == 2 or manipulator_index == 3:
			if Input.is_action_pressed("manipulator_close"):
				spinPWM = 1500
			if Input.is_action_pressed("manipulator_open"):
				spinPWM = 1600
			if Input.is_action_pressed("manipulator_left"):
				spinPWM = 1400

			if manipulator_index == 2:
				top_manipulator_pwm = spinPWM
			else:
				bottom_manipulator_pwm = spinPWM
		elif manipulator_index == 4:
			if Input.is_action_pressed("manipulator_close"):
				bottom_manipulator_pwm -= OPEN_PWM * PWM_COEFFICIENT * 1.7
			if Input.is_action_pressed("manipulator_open"):
				bottom_manipulator_pwm += OPEN_PWM * PWM_COEFFICIENT * 1.7
			if Input.is_action_pressed("manipulator_left"):
				top_manipulator_pwm -= 100 * PWM_COEFFICIENT
			if Input.is_action_pressed("manipulator_right"):
				top_manipulator_pwm += 100 * PWM_COEFFICIENT
		elif manipulator_index == 5:
			if Input.is_action_pressed("manipulator_close"):
				top_manipulator_pwm += OPEN_PWM * PWM_COEFFICIENT * 1.7
			if Input.is_action_pressed("manipulator_open"):
				top_manipulator_pwm -= OPEN_PWM * PWM_COEFFICIENT * 1.7
				
	
	if Input.is_action_pressed("light_on"):
		light_on = true
	else:
		light_on = false
	
	
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
	
	$ServoCurrentPWMLabel.text = str(bottom_manipulator_pwm)
	
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
			"bottom_manip_pwm": int(bottom_manipulator_pwm),
			"top_manip_pwm": int(top_manipulator_pwm),
			"power_scale" : power_scale,
			"light_on": light_on}
		_client.get_peer(1).put_packet(JSON.print(data).to_ascii())

