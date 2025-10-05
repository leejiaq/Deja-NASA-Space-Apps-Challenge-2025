extends Camera3D 

@export var marker : Node3D
@export var control : Control
@export var main : Node3D

func _input(event: InputEvent) -> void:
	if control.on_control:
		return

	if event is InputEventMouseButton && event.button_index == MOUSE_BUTTON_LEFT && event.pressed:
		var mouse_pos = event.position

		var from = project_ray_origin(mouse_pos)
		var to = from + project_ray_normal(mouse_pos) * 1000.0
	
		var space_state = get_world_3d().direct_space_state
		var query = PhysicsRayQueryParameters3D.create(from, to)
		var result = space_state.intersect_ray(query)
	
		if result:
			var hit_pos = result.position

			marker.visible = true
			marker.global_position = hit_pos

			var pos_loc = result.collider.to_local(hit_pos)
	
			var radius = result.collider.scale.x / 2
			var dir = pos_loc.normalized()
	
			var lat = asin(dir.y)
			var lon = atan2(dir.z, dir.x)

			main.pos = Vector2(lat, lon)

			print(lat / PI * 180, " ", lon / PI * 180)
			
			marker.look_at(hit_pos + dir, Vector3.UP)
