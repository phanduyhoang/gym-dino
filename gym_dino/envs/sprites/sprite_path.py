import os

def sprite_path(file):
	base_path = '/content/gym-dino/gym_dino/envs/sprites'
	full_path = os.path.join(base_path, file)
	if not os.path.exists(full_path):
		raise FileNotFoundError(f"Sprite file not found: {full_path}")
	return full_path
