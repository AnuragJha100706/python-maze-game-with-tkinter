'''
Character class - Clean, colorful player tokens and items
'''
import pygame
from time import sleep

class Character:
	def __init__(self, screen, side_length, border_width, _valid_points, start_point, end_point, current_position, a_colour, na_colour,\
				 escape=False, keys=None, k_colour=None, offset_x=0):

		self.screen = screen
		self.side_length = side_length
		self.border_width = border_width
		self.start_point = start_point
		self.end_point = end_point
		self.current_position = current_position
		self.a_colour = a_colour
		self.na_colour = na_colour
		self.offset_x = offset_x
		
		self.escape = escape
		self.keys = keys if keys is not None else []
		self.k_colour = k_colour if k_colour is not None else (241, 196, 15)
		self.unlocked = False
		self.wallBreaks = 1
		self.increaseCompSpeed = False

		# Floating "+1 KEY!" text particles
		self.floating_texts = []

		self.draw_position()

	def _get_cell_rect(self, pos):
		return pygame.Rect(
			self.offset_x + self.border_width + (self.side_length + self.border_width) * pos[0],
			self.border_width + (self.side_length + self.border_width) * pos[1],
			self.side_length,
			self.side_length
		)

	def draw_position(self):
		"""Draw a clean, colorful circular player token with a crisp border."""
		cx = self.offset_x + self.border_width + (self.side_length + self.border_width) * self.current_position[0] + self.side_length / 2.0
		cy = self.border_width + (self.side_length + self.border_width) * self.current_position[1] + self.side_length / 2.0
		radius = max(3.0, self.side_length / 2.0 - 1.0)

		# Outer border circle for crisp visibility
		border_color = (
			max(0, self.a_colour[0] - 50),
			max(0, self.a_colour[1] - 50),
			max(0, self.a_colour[2] - 50)
		)
		pygame.draw.circle(self.screen, border_color, (int(cx), int(cy)), int(radius))

		# Main colorful inner circle
		inner_rad = max(1.0, radius - 1.5)
		pygame.draw.circle(self.screen, self.a_colour, (int(cx), int(cy)), int(inner_rad))

		# Clean highlight gleam
		if radius >= 4.0:
			shine_rad = max(1, int(radius * 0.25))
			shine_x = int(cx - radius * 0.28)
			shine_y = int(cy - radius * 0.28)
			pygame.draw.circle(self.screen, (255, 255, 255), (shine_x, shine_y), shine_rad)

		# Render any active floating text
		self.update_floating_texts()

	def move_character(self, next_position):
		curr_rect = self._get_cell_rect(self.current_position)
		next_rect = self._get_cell_rect(next_position)

		# Restore clean path background
		pygame.draw.rect(self.screen, self.na_colour, curr_rect)

		self.current_position = next_position
		self.draw_position()

		pygame.display.update(curr_rect)
		pygame.display.update(next_rect)

		# Key collection logic
		if self.escape is True:
			grid_pos = (round(self.current_position[0]), round(self.current_position[1]))
			if grid_pos in self.keys:
				self.keys.remove(grid_pos)
				kx = self.offset_x + self.border_width + (self.side_length + self.border_width) * grid_pos[0] + self.side_length / 2.0
				ky = self.border_width + (self.side_length + self.border_width) * grid_pos[1]
				self.floating_texts.append({
					'text': '+1 KEY!',
					'x': kx,
					'y': ky - 4,
					'alpha': 255,
					'color': (241, 196, 15)
				})
				if len(self.keys) % 2 == 0:
					self.wallBreaks += 1
					self.increaseCompSpeed = True

	def move_character_smooth(self, next_position, steps):
		if next_position[0] != self.current_position[0]:
			for i in range(1, steps + 1):
				sleep(0.003)
				difference = (next_position[0] - self.current_position[0]) * i / steps
				next_pos = (self.current_position[0] + difference, self.current_position[1])
				self.move_character(next_pos)
		else:
			for i in range(1, steps + 1):
				sleep(0.003)
				difference = (next_position[1] - self.current_position[1]) * i / steps
				next_pos = (self.current_position[0], self.current_position[1] + difference)
				self.move_character(next_pos)

	def get_current_position(self):
		return (round(self.current_position[0]), round(self.current_position[1]))

	def reached_goal(self):
		curr = self.get_current_position()
		return curr == self.end_point

	def get_wallBreaks(self):
		return self.wallBreaks

	def use_wallBreak(self):
		self.wallBreaks -= 1

	def get_keys_left(self):
		return len(self.keys) if self.keys else 0

	def draw_keys(self):
		"""Draw clean, colorful golden key items."""
		r = max(3.0, self.side_length / 2.0 - 1.0)

		for key in self.keys:
			kx = self.offset_x + self.border_width + (self.side_length + self.border_width) * key[0] + self.side_length / 2.0
			ky = self.border_width + (self.side_length + self.border_width) * key[1] + self.side_length / 2.0

			# Outer diamond in warm gold
			outer_pts = [
				(kx, ky - r),
				(kx + r, ky),
				(kx, ky + r),
				(kx - r, ky)
			]
			pygame.draw.polygon(self.screen, (243, 156, 18), outer_pts)

			# Inner diamond in bright yellow/gold
			if r >= 3.5:
				inner_r = r * 0.6
				inner_pts = [
					(kx, ky - inner_r),
					(kx + inner_r, ky),
					(kx, ky + inner_r),
					(kx - inner_r, ky)
				]
				pygame.draw.polygon(self.screen, (254, 240, 138), inner_pts)

	def update_floating_texts(self):
		"""Render floating text particles."""
		if not self.floating_texts:
			return
		font = pygame.font.SysFont(["segoe ui", "arial", "helvetica"], max(11, int(self.side_length * 0.9)), bold=True)
		for ft in list(self.floating_texts):
			ft['y'] -= 0.5
			ft['alpha'] -= 7
			if ft['alpha'] <= 0:
				self.floating_texts.remove(ft)
			else:
				t_surf = font.render(ft['text'], True, ft['color'])
				t_surf.set_alpha(int(ft['alpha']))
				t_rect = t_surf.get_rect(center=(int(ft['x']), int(ft['y'])))
				self.screen.blit(t_surf, t_rect)

	def increase_computer_speed(self):
		if self.increaseCompSpeed:
			self.increaseCompSpeed = False
			return True
		return False

	def collected_all(self):
		if not self.keys:
			self.unlocked = True
			return True
		return False

	def escaped(self):
		return self.unlocked and self.reached_goal()