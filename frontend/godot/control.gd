extends Control
class_name Ctrl

@export var btn : Button
@export var bounding_box_angle : Control
@export var slider : HSlider
@export var indicator : TextureRect
@export var deglab : Label
@export var main : Node3D

var on_control : bool = false

func _process(delta: float) -> void:
	if (btn.get_rect().has_point(get_local_mouse_position()) || bounding_box_angle.get_rect().has_point(get_local_mouse_position())):
		on_control = true
	else:
		on_control = false
	
	size = get_viewport_rect().size

	indicator.rotation_degrees = -180 + slider.value
	deglab.text = str(slider.value) + "°"

	main.deg = slider.value
