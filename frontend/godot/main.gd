extends Node3D

@export var animator : AnimationPlayer
@export var rig : Node3D

var pos : Vector2 # lat long

var _callback_ref = JavaScriptBridge.create_callback(_param_callback)

var id
var date
var close_approach_date
var estimated_maximum_diameter
var relative_velocity
var distance_from_earth

func _ready() -> void:
	var search = JavaScriptBridge.get_interface("location").search
	var params = JavaScriptBridge.create_object("URLSearchParams", search)
	id = params.get("id")
	date = params.get("date")
	close_approach_date = params.get("close_approach_date")
	estimated_maximum_diameter = params.get("estimated_maximum_diameter")
	relative_velocity = params.get("relative_velocity")
	distance_from_earth = params.get("distance_from_earth")

func _on_button_pressed() -> void:
	rig.rotation = Vector3(-pos.x, pos.y+PI, 0)
	animator.play("rock")


func redirect() -> void:
	var location = JavaScriptBridge.get_interface("location")
	location.href = "%s/impact.html?id=%s&date=%s&close_approach_date=%s&estimated_maximum_diameter=%s&relative_velocity=%s&distance_from_earth=%s&lat=%s&lon=%s" % \
			[location.origin, id, date, close_approach_date, estimated_maximum_diameter, relative_velocity, distance_from_earth, str(pos.x / PI * 180), str(pos.y / PI * 180)]

func _param_callback(args):
	pass
