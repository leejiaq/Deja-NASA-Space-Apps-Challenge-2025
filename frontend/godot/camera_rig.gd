extends Node3D

var prev_mouse_pos : Vector2 = Vector2.ZERO
var mouse_pos : Vector2

@export var speed : float = 100
@export var dampening : float = 2.0
@export var camera : Camera3D

var vel : Vector2 = Vector2.ZERO

var scroll_vel : float = 0

func _process(delta: float) -> void:
	vel = vel.lerp(Vector2.ZERO, delta * dampening)
	scroll_vel = lerpf(scroll_vel, 0, delta * 10)

	rotation_degrees.x -= vel.y * get_process_delta_time() * speed * (camera.position.z / 6.0)
	rotation_degrees.y -= vel.x * get_process_delta_time()  * speed * (camera.position.z / 6.0)

	camera.position.z += scroll_vel
	camera.position.z = max(1.75, camera.position.z)

func _input(event: InputEvent) -> void:
	if !(event is InputEventMouse):
		return

	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_WHEEL_UP:
		scroll_vel = -0.05
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
		scroll_vel = 0.05

	if event.button_mask != MOUSE_BUTTON_MASK_LEFT:
		prev_mouse_pos = event.position

		return

	vel = Vector2.ZERO

	mouse_pos = event.position

	var delta_x = mouse_pos.x - prev_mouse_pos.x
	var delta_y = mouse_pos.y - prev_mouse_pos.y

	vel = Vector2(delta_x, delta_y)

	prev_mouse_pos = mouse_pos
