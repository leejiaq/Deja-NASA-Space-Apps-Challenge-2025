extends Node3D

@export var animator : AnimationPlayer
@export var rig : Node3D

var pos : Vector2

var _callback_ref = JavaScriptBridge.create_callback(_param_callback)

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	var search = JavaScriptBridge.get_interface("location").search
	print(search)
	var params = JavaScriptBridge.create_object("URLSearchParams", search)
	var bob = params.get("bob")
	print(bob)

func _on_button_pressed() -> void:
	rig.rotation = Vector3(-pos.x, PI/2-pos.y, 0)
	animator.play("rock")

func _param_callback(args):
	pass
