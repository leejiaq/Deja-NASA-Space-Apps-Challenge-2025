extends Control
class_name Ctrl

@export var btn : Button

var on_control : bool = false

func _process(delta: float) -> void:
	on_control = btn.get_rect().has_point(get_local_mouse_position())
	size = get_viewport_rect().size
