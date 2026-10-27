from graph import Graph
from character import Character
import ui_file
import astar
import random
import pygame
import time
import queue
import math
from collections import deque
import os
from login import LoginSystem
from score_db import save_score, get_high_scores

def set_window_position(x, y):
	os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

def create_grid(size):
	grid = Graph()
	for i in range(size):
		for j in range(size):
			grid.add_vertex((i, j))
	return grid

def create_maze(grid, vertex, completed=None, vertices=None):
	if vertices is None:
		vertices = grid.get_vertices()
	if completed is None:
		completed = [vertex]

	paths = list(int(i) for i in range(4))
	random.shuffle(paths)

	up = (vertex[0], vertex[1] - 1)
	down = (vertex[0], vertex[1] + 1)
	left = (vertex[0] - 1, vertex[1])
	right = (vertex[0] + 1, vertex[1])

	for direction in paths:
		if direction == 0:
			if up in vertices and up not in completed:
				grid.add_edge((vertex, up))
				grid.add_edge((up, vertex))
				completed.append(up)
				create_maze(grid, up, completed, vertices)
		elif direction == 1:
			if down in vertices and down not in completed:
				grid.add_edge((vertex, down))
				grid.add_edge((down, vertex))
				completed.append(down)
				create_maze(grid, down, completed, vertices)
		elif direction == 2:
			if left in vertices and left not in completed:
				grid.add_edge((vertex, left))
				grid.add_edge((left, vertex))
				completed.append(left)
				create_maze(grid, left, completed, vertices)
		elif direction == 3:
			if right in vertices and right not in completed:
				grid.add_edge((vertex, right))
				grid.add_edge((right, vertex))
				completed.append(right)
				create_maze(grid, right, completed, vertices)

	return grid

def draw_maze(screen, maze, size, colour, side_length, border_width, offset_x=0):
	for i in range(size):
		for j in range(size):
			if i != 0:
				if maze.is_edge(((i, j), (i - 1, j))):
					pygame.draw.rect(screen, colour, [
						offset_x + (side_length + border_width) * i,
						border_width + (side_length + border_width) * j,
						side_length + border_width,
						side_length
					])
			if i != size - 1:
				if maze.is_edge(((i, j), (i + 1, j))):
					pygame.draw.rect(screen, colour, [
						offset_x + border_width + (side_length + border_width) * i,
						border_width + (side_length + border_width) * j,
						side_length + border_width,
						side_length
					])
			if j != 0:
				if maze.is_edge(((i, j), (i, j - 1))):
					pygame.draw.rect(screen, colour, [
						offset_x + border_width + (side_length + border_width) * i,
						(side_length + border_width) * j,
						side_length,
						side_length + border_width
					])
			if j != size - 1:
				if maze.is_edge(((i, j), (i, j + 1))):
					pygame.draw.rect(screen, colour, [
						offset_x + border_width + (side_length + border_width) * i,
						border_width + (side_length + border_width) * j,
						side_length,
						side_length + border_width
					])

def draw_position(screen, side_length, border_width, current_point, colour, offset_x=0):
	x = offset_x + border_width + (side_length + border_width) * current_point[0]
	y = border_width + (side_length + border_width) * current_point[1]
	p_rect = pygame.Rect(x, y, side_length, side_length)
	radius = max(2, side_length // 4)
	pygame.draw.rect(screen, colour, p_rect, border_radius=radius)
	if side_length >= 8:
		inner_rect = p_rect.inflate(-side_length // 3, -side_length // 3)
		pygame.draw.rect(screen, (255, 255, 255), inner_rect, border_radius=max(1, radius // 2))

def draw_portal(screen, side_length, border_width, end_point, ticks, color=(245, 158, 11), offset_x=0, locked=False):
	"""Clean, colorful exit goal marker."""
	cx = offset_x + border_width + (side_length + border_width) * end_point[0] + side_length / 2.0
	cy = border_width + (side_length + border_width) * end_point[1] + side_length / 2.0
	base_r = max(4.0, side_length / 2.0 - 1.0)

	if locked:
		color = (239, 68, 68)

	# Clean solid circle base
	pygame.draw.circle(screen, color, (int(cx), int(cy)), int(base_r))

	# Inner star/square highlight
	if not locked:
		star_r = max(2.0, base_r * 0.45)
		pygame.draw.circle(screen, (255, 255, 255), (int(cx), int(cy)), int(star_r))
	else:
		# Draw clean locked X
		line_len = max(2, int(base_r * 0.5))
		pygame.draw.line(screen, (255, 255, 255), (cx - line_len, cy - line_len), (cx + line_len, cy + line_len), 2)
		pygame.draw.line(screen, (255, 255, 255), (cx - line_len, cy + line_len), (cx + line_len, cy - line_len), 2)

def apply_torchlight(screen, size, player_pos, side_length, border_width, ticks, offset_x=0):
	"""Simple, clean torchlight circle around the player."""
	radius = side_length * 4.5
	px = offset_x + border_width + (side_length + border_width) * player_pos[0] + side_length / 2.0
	py = border_width + (side_length + border_width) * player_pos[1] + side_length / 2.0

	fog = pygame.Surface(size, pygame.SRCALPHA)
	fog.fill((20, 24, 34, 240))

	# Soft light circle
	pygame.draw.circle(fog, (20, 24, 34, 120), (int(px), int(py)), int(radius))
	pygame.draw.circle(fog, (0, 0, 0, 0), (int(px), int(py)), int(radius * 0.6))
	screen.blit(fog, (0, 0))

def draw_hud(screen, size, elapsed_time, mode, keys_left=0, wall_breaks=0, torchlight=False):
	"""Clean, colorful bottom HUD bar."""
	hud_height = 42
	hud_rect = pygame.Rect(0, size[1] - hud_height, size[0], hud_height)

	# Surface & clean border line
	pygame.draw.rect(screen, (34, 39, 54), hud_rect)
	pygame.draw.line(screen, (54, 62, 84), (0, hud_rect.top), (size[0], hud_rect.top), 1)

	font = pygame.font.SysFont(["segoe ui", "arial", "helvetica"], 13, bold=True)
	small_font = pygame.font.SysFont(["segoe ui", "arial", "helvetica"], 11)

	# 1. Stopwatch on Left (in warm amber)
	mins = int(elapsed_time) // 60
	secs = int(elapsed_time) % 60
	time_str = f"⏱ Time: {mins:02d}:{secs:02d}"
	t_surf = font.render(time_str, True, (245, 158, 11))
	screen.blit(t_surf, (20, hud_rect.centery - t_surf.get_height() // 2))

	# 2. Middle status items
	if mode == 4:
		mid_x = size[0] // 2 - 110
		keys_str = f"🗝 Keys: {8 - keys_left}/8"
		k_surf = font.render(keys_str, True, (245, 158, 11) if keys_left == 0 else (240, 242, 248))
		screen.blit(k_surf, (mid_x, hud_rect.centery - k_surf.get_height() // 2))

		wb_str = f"🔨 Breaks: {wall_breaks} [SPACE]"
		wb_surf = font.render(wb_str, True, (16, 185, 129))
		screen.blit(wb_surf, (mid_x + 115, hud_rect.centery - wb_surf.get_height() // 2))
	elif mode == 1:
		p_info = "P1: WASD (Green)  |  P2: Arrows (Blue)"
		p_surf = font.render(p_info, True, (240, 242, 248))
		screen.blit(p_surf, (size[0] // 2 - p_surf.get_width() // 2, hud_rect.centery - p_surf.get_height() // 2))

	# 3. Torch & Menu Hint on Right
	right_x = size[0] - 210
	torch_color = (16, 185, 129) if torchlight else (156, 163, 175)
	torch_str = f"[T] Torch: {'ON' if torchlight else 'OFF'}"
	torch_surf = font.render(torch_str, True, torch_color)
	screen.blit(torch_surf, (right_x, hud_rect.centery - torch_surf.get_height() // 2))

	esc_surf = small_font.render("[ESC] Menu", True, (180, 186, 200))
	screen.blit(esc_surf, (size[0] - 80, hud_rect.centery - esc_surf.get_height() // 2))

def playerTwo(player2, maze, vertices, cooldown, timer):
	keys = pygame.key.get_pressed()
	if pygame.time.get_ticks() - timer > cooldown:
		current_point = player2.get_current_position()
		if keys[pygame.K_d]:
			if (current_point[0] + 1, current_point[1]) in vertices:
				next_point = (current_point[0] + 1, current_point[1])
				if maze.is_edge((current_point, next_point)):
					player2.move_character_smooth(next_point, 5)
			timer = pygame.time.get_ticks()
		if keys[pygame.K_a]:
			if (current_point[0] - 1, current_point[1]) in vertices:
				next_point = (current_point[0] - 1, current_point[1])
				if maze.is_edge((current_point, next_point)):
					player2.move_character_smooth(next_point, 5)
			timer = pygame.time.get_ticks()
		if keys[pygame.K_w]:
			if (current_point[0], current_point[1] - 1) in vertices:
				next_point = (current_point[0], current_point[1] - 1)
				if maze.is_edge((current_point, next_point)):
					player2.move_character_smooth(next_point, 5)
			timer = pygame.time.get_ticks()
		if keys[pygame.K_s]:
			if (current_point[0], current_point[1] + 1) in vertices:
				next_point = (current_point[0], current_point[1] + 1)
				if maze.is_edge((current_point, next_point)):
					player2.move_character_smooth(next_point, 5)
			timer = pygame.time.get_ticks()
	return timer

def update_path(next_point, dq):
	if len(dq) >= 2:
		first_pop = dq.pop()
		second_pop = dq.pop()
		if second_pop == next_point:
			dq.append(second_pop)
		else:
			dq.append(second_pop)
			dq.append(first_pop)
			dq.append(next_point)
		return dq
	else:
		dq.append(next_point)
		return dq

def update_path_a(start_point, end_point, maze, dq):
	closest_path = astar.astar(start_point, end_point, maze)
	if not closest_path:
		return update_path(end_point, dq)
	if closest_path[0] == start_point:
		closest_path.pop(0)
	if len(dq) + 1 > len(closest_path):
		dq.clear()
		for edge in closest_path:
			dq.append(edge)
		return dq
	else:
		return update_path(end_point, dq)

def break_wall(maze, current_point, next_point):
	if not maze.is_edge((current_point, next_point)):
		maze.add_edge((current_point, next_point))
		maze.add_edge((next_point, current_point))
	return maze

def get_character_position(character):
	assert character is not None
	return character.get_current_position()

def runGame(grid_size, side_length, mode, username="Player", torchlight=False):
	if not pygame.get_init():
		pygame.init()

	DARK_WALL = (26, 30, 42)              # Clean modern dark slate wall
	PATH_COLOR = (248, 250, 252)          # Clean warm off-white walkable path
	GRAY = (148, 163, 184)
	GOLD = (245, 158, 11)
	GREEN = (16, 185, 129)
	RED = (239, 68, 68)
	BLUE = (59, 130, 246)

	border_width = max(2, side_length // 5)
	maze_w = grid_size * (side_length + border_width) + border_width
	maze_h = grid_size * (side_length + border_width) + border_width

	hud_height = 42
	win_w = max(560, maze_w)
	win_h = maze_h + hud_height
	offset_x = max(0, (win_w - maze_w) // 2)

	size = (win_w, win_h)
	screen = pygame.display.set_mode(size)
	pygame.display.set_caption("Yet Another Maze - [ESC] Menu")
	carryOn = True
	clock = pygame.time.Clock()

	grid = create_grid(grid_size)
	maze = create_maze(grid, (grid_size // 2, grid_size // 2))

	screen.fill(DARK_WALL)
	vertices = maze.get_vertices()

	draw_maze(screen, maze, grid_size, PATH_COLOR, side_length, border_width, offset_x=offset_x)

	start_point = (0, 0)
	start_point2 = (grid_size - 1, grid_size - 1)
	end_point = (grid_size - 1, grid_size - 1)
	end_point2 = (0, 0)
	choice = random.randrange(4)

	if choice == 0:
		start_point = (grid_size - 1, grid_size - 1)
		start_point2 = (0, 0)
		end_point = (0, 0)
		end_point2 = (grid_size - 1, grid_size - 1)
	elif choice == 1:
		start_point = (0, grid_size - 1)
		start_point2 = (grid_size - 1, 0)
		end_point = (grid_size - 1, 0)
		end_point2 = (0, grid_size - 1)
	elif choice == 2:
		start_point = (grid_size - 1, 0)
		start_point2 = (0, grid_size - 1)
		end_point = (0, grid_size - 1)
		end_point2 = (grid_size - 1, 0)

	winner = 0
	player1 = Character(screen, side_length, border_width, vertices,
						start_point, end_point, start_point, GREEN, PATH_COLOR, offset_x=offset_x)
	player2 = None
	computer_character = None
	q = None
	dq = None
	computer_cooldown = 0
	computer_timer = 0
	initial_wait = 0
	initial_wait_timer = 0
	start_timer2 = 0
	waitCondition = False

	if mode == 1:
		player2 = Character(screen, side_length, border_width, vertices,
							start_point2, end_point2, start_point2, BLUE, PATH_COLOR, offset_x=offset_x)
	elif mode == 2:
		computer_character = Character(screen, side_length, border_width, vertices,
								 start_point2, end_point2, start_point2, GRAY, PATH_COLOR, offset_x=offset_x)
		path = astar.astar(start_point2, end_point2, maze)
		q = queue.Queue()
		for edge in path:
			q.put(edge)
		computer_cooldown = min(350, grid_size * 15)
		computer_timer = pygame.time.get_ticks()
	elif mode == 3:
		computer_character = Character(screen, side_length, border_width, vertices,
								 start_point, end_point, start_point, GRAY, PATH_COLOR, offset_x=offset_x)
		dq = deque()
		dq.append(start_point)
		computer_cooldown = min(300, grid_size * 10)
		initial_wait = 3000
		computer_timer = pygame.time.get_ticks()
		initial_wait_timer = pygame.time.get_ticks()
	elif mode == 4:
		x_coords = random.sample(range(1, grid_size - 1), 8)
		y_coords = random.sample(range(1, grid_size - 1), 8)
		unlock_keys = [(x_coords[i], y_coords[i]) for i in range(8)]

		player1 = Character(screen, side_length, border_width, vertices, start_point,
							end_point, start_point, GREEN, PATH_COLOR, True, unlock_keys, GOLD, offset_x=offset_x)
		computer_character = Character(screen, side_length, border_width, vertices,
								 start_point, end_point, start_point, GRAY, PATH_COLOR, offset_x=offset_x)
		dq = deque()
		dq.append(start_point)
		computer_cooldown = min(3000, grid_size * 100)
		initial_wait = 3000
		computer_timer = pygame.time.get_ticks()
		initial_wait_timer = pygame.time.get_ticks()

	cooldown = 100
	start_timer = pygame.time.get_ticks()
	if mode == 1:
		start_timer2 = pygame.time.get_ticks()

	game_start_time = time.time()

	while carryOn:
		current_ticks = pygame.time.get_ticks()
		elapsed_time = time.time() - game_start_time

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return -1, 0, torchlight
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					return -1, 0, torchlight
				elif event.key == pygame.K_t:
					torchlight = not torchlight

		keys = pygame.key.get_pressed()

		# Movement controls
		if current_ticks - start_timer > cooldown:
			current_point = player1.get_current_position()
			moved = False
			next_pt = None

			right_pressed = keys[pygame.K_RIGHT] or (mode != 1 and keys[pygame.K_d])
			left_pressed = keys[pygame.K_LEFT] or (mode != 1 and keys[pygame.K_a])
			up_pressed = keys[pygame.K_UP] or (mode != 1 and keys[pygame.K_w])
			down_pressed = keys[pygame.K_DOWN] or (mode != 1 and keys[pygame.K_s])

			if right_pressed:
				target = (current_point[0] + 1, current_point[1])
				if target in vertices:
					next_pt = target
			elif left_pressed:
				target = (current_point[0] - 1, current_point[1])
				if target in vertices:
					next_pt = target
			elif up_pressed:
				target = (current_point[0], current_point[1] - 1)
				if target in vertices:
					next_pt = target
			elif down_pressed:
				target = (current_point[0], current_point[1] + 1)
				if target in vertices:
					next_pt = target

			if next_pt:
				if maze.is_edge((current_point, next_pt)):
					player1.move_character_smooth(next_pt, 5)
					moved = True
					if mode == 3:
						dq = update_path(next_pt, dq)
					elif mode == 4:
						dq = update_path_a(get_character_position(computer_character), next_pt, maze, dq)
				else:
					if mode == 4 and keys[pygame.K_SPACE] and player1.get_wallBreaks() > 0:
						maze = break_wall(maze, current_point, next_pt)
						draw_maze(screen, maze, grid_size, PATH_COLOR, side_length, border_width, offset_x=offset_x)
						player1.move_character_smooth(next_pt, 5)
						player1.use_wallBreak()
						moved = True
						dq = update_path_a(get_character_position(computer_character), next_pt, maze, dq)

			if moved or right_pressed or left_pressed or up_pressed or down_pressed:
				start_timer = pygame.time.get_ticks()

		# Render maze frame
		screen.fill(DARK_WALL)
		draw_maze(screen, maze, grid_size, PATH_COLOR, side_length, border_width, offset_x=offset_x)

		# Render characters & goals
		if mode == 1:
			assert player2 is not None
			start_timer2 = playerTwo(player2, maze, vertices, cooldown, start_timer2)
			draw_portal(screen, side_length, border_width, end_point, current_ticks, GREEN, offset_x=offset_x)
			draw_portal(screen, side_length, border_width, end_point2, current_ticks, BLUE, offset_x=offset_x)
			player2.draw_position()
			player1.draw_position()

		elif mode == 2:
			assert computer_character is not None and q is not None
			if current_ticks - computer_timer > computer_cooldown:
				if not q.empty():
					computer_character.move_character_smooth(q.get(), 5)
				computer_timer = pygame.time.get_ticks()

			draw_portal(screen, side_length, border_width, end_point, current_ticks, GREEN, offset_x=offset_x)
			draw_portal(screen, side_length, border_width, end_point2, current_ticks, GRAY, offset_x=offset_x)
			computer_character.draw_position()
			player1.draw_position()

		elif mode in (3, 4):
			assert computer_character is not None and dq is not None
			if mode == 4:
				player1.draw_keys()
				is_unlocked = player1.collected_all()
				draw_portal(screen, side_length, border_width, end_point, current_ticks,
							GREEN if is_unlocked else RED, offset_x=offset_x, locked=not is_unlocked)
				if player1.increase_computer_speed():
					computer_cooldown = max(100, computer_cooldown / 2)
			else:
				draw_portal(screen, side_length, border_width, end_point, current_ticks, GOLD, offset_x=offset_x)

			waitCondition = current_ticks - initial_wait_timer > initial_wait
			if waitCondition:
				if current_ticks - computer_timer > computer_cooldown:
					if dq:
						computer_character.move_character_smooth(dq.popleft(), 5)
					computer_timer = pygame.time.get_ticks()

			computer_character.draw_position()
			player1.draw_position()

		elif mode == 0:
			draw_portal(screen, side_length, border_width, end_point, current_ticks, GOLD, offset_x=offset_x)
			player1.draw_position()

		# Apply Torchlight if active
		if torchlight:
			apply_torchlight(screen, size, player1.get_current_position(), side_length, border_width, current_ticks, offset_x=offset_x)

		# Render Clean HUD
		draw_hud(
			screen, size, elapsed_time, mode,
			keys_left=player1.get_keys_left() if mode == 4 else 0,
			wall_breaks=player1.get_wallBreaks() if mode == 4 else 0,
			torchlight=torchlight
		)

		# Victory Conditions
		if mode == 0:
			if player1.reached_goal():
				carryOn = False
		elif mode == 1:
			assert player2 is not None
			if player1.reached_goal():
				winner = 1
				carryOn = False
			elif player2.reached_goal():
				winner = 2
				carryOn = False
		elif mode == 2:
			assert computer_character is not None
			if player1.reached_goal():
				winner = 1
				carryOn = False
			elif computer_character.reached_goal():
				winner = 2
				carryOn = False
		elif mode == 3:
			assert computer_character is not None
			if player1.reached_goal():
				winner = 1
				carryOn = False
			elif computer_character.get_current_position() == player1.get_current_position() and waitCondition:
				winner = 2
				carryOn = False
		elif mode == 4:
			assert computer_character is not None
			if player1.escaped():
				winner = 1
				carryOn = False
			elif computer_character.get_current_position() == player1.get_current_position() and waitCondition:
				winner = 2
				carryOn = False

		pygame.display.flip()
		clock.tick(60)

	if mode == 0:
		final_time = int(time.time() - game_start_time)
		return mode, final_time, torchlight
	else:
		return mode, winner, torchlight

# ----------------- MAIN STATE MACHINE -----------------
if __name__ == "__main__":
	login_system = LoginSystem()
	username = login_system.login()

	if username is None:
		print("Login cancelled or closed. Exiting.")
	else:
		set_window_position(50, 50)

		STATE_MENU = "MENU"
		STATE_GAMEPLAY = "GAMEPLAY"
		STATE_GAMEOVER = "GAMEOVER"

		current_state = STATE_MENU
		settings = {
			'grid_size': 20,
			'side_length': 10,
			'mode': 0,
			'torchlight': False
		}
		last_result = None
		screen = None

		running = True
		while running:
			if current_state == STATE_MENU:
				run_bool, g_size, s_len, mode, torch = ui_file.startScreen(screen, settings)
				if not run_bool:
					pygame.quit()
					break
				settings['grid_size'] = g_size
				settings['side_length'] = s_len
				settings['mode'] = mode
				settings['torchlight'] = torch
				current_state = STATE_GAMEPLAY

			elif current_state == STATE_GAMEPLAY:
				result_mode, value, torch = runGame(
					settings['grid_size'],
					settings['side_length'],
					settings['mode'],
					username,
					settings['torchlight']
				)
				settings['torchlight'] = torch

				if result_mode == -1:  # Player pressed ESC to return to menu
					current_state = STATE_MENU
				else:
					if result_mode == 0:
						save_score(username, value, settings['grid_size'], result_mode)
					last_result = (result_mode, value)
					current_state = STATE_GAMEOVER

			elif current_state == STATE_GAMEOVER:
				mode, val = last_result
				action = ui_file.endGame(mode, val, screen)
				if action == "replay":
					current_state = STATE_GAMEPLAY
				else:
					current_state = STATE_MENU