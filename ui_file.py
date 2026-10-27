'''
User interface file - Clean, colorful, modern UI
'''
import pygame
import time
import os
from score_db import get_high_scores

# ----------------- CLEAN & COLORFUL PALETTE -----------------
COLOR_BG = (26, 30, 42)              # Clean modern dark slate
COLOR_SURFACE = (36, 42, 58)         # Clean card background
COLOR_SURFACE_HOVER = (46, 54, 74)   # Subtle hover tint
COLOR_BORDER = (54, 62, 84)          # Card outline
COLOR_TEXT_MAIN = (248, 250, 252)    # Crisp clean white
COLOR_TEXT_MUTED = (160, 168, 185)   # Friendly gray-blue subtext

# Friendly category colors
COLOR_GREEN = (16, 185, 129)         # Play / Success / Player 1
COLOR_GOLD = (245, 158, 11)          # High Scores / Gold / Coins
COLOR_BLUE = (59, 130, 246)          # Settings / Info / Player 2
COLOR_RED = (239, 68, 68)            # Exit / Danger / Defeat
COLOR_SILVER = (195, 195, 205)       # 2nd place
COLOR_BRONZE = (205, 127, 50)        # 3rd place

FONT_FAMILIES = ["segoe ui", "arial", "helvetica", "trebuchet ms", "dejavusans"]

_font_cache = {}

def get_font(size, bold=False):
    key = (size, bold)
    if key not in _font_cache:
        _font_cache[key] = pygame.font.SysFont(FONT_FAMILIES, size, bold=bold)
    return _font_cache[key]

def safe_set_cursor(cursor):
    try:
        pygame.mouse.set_cursor(cursor)
    except Exception:
        pass

# ----------------- DRAWING HELPERS -----------------
def draw_card(surface, rect, is_hover=False, bg_color=None, border_color=None, radius=10, width=1):
    bg = bg_color or (COLOR_SURFACE_HOVER if is_hover else COLOR_SURFACE)
    b_color = border_color or (COLOR_BLUE if is_hover else COLOR_BORDER)
    pygame.draw.rect(surface, bg, rect, border_radius=radius)
    if width > 0:
        pygame.draw.rect(surface, b_color, rect, width=width, border_radius=radius)

def draw_text(surface, text, font, color, center=None, topleft=None):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = center
    elif topleft:
        rect.topleft = topleft
    surface.blit(rendered, rect)
    return rect

def displayMessage(text, colour, screen, size, screen_size, y_pos, screen_update=None):
    font = get_font(size, bold=True)
    textSurface = font.render(text, True, colour)
    textRect = textSurface.get_rect(center=(screen_size[0] // 2, y_pos))
    screen.blit(textSurface, textRect)
    if screen_update is None:
        screen_update = textRect
    pygame.display.update(screen_update)

def displayMenuSelection(screen, screen_size, choice, bg_colour=COLOR_BG, a_colour=COLOR_GOLD, na_colour=COLOR_TEXT_MAIN):
    pass

def displaySettingsSeleciton(screen, screen_size, choice, bg_colour, a_colour, na_colour, grid_size, side_length, mode_text):
    pass

# ----------------- HIGH SCORES SCREEN -----------------
def displayHighScores(screen, screen_size, bg_colour=None, a_colour=None, na_colour=None):
    scores = get_high_scores()
    width, height = screen_size

    screen.fill(COLOR_BG)

    # Header
    draw_text(screen, "HALL OF FAME", get_font(32, bold=True), COLOR_GOLD, center=(width // 2, 48))
    draw_text(screen, "Fastest Solo Maze Completions", get_font(15), COLOR_TEXT_MUTED, center=(width // 2, 82))

    # Leaderboard Card
    card_rect = pygame.Rect(40, 110, width - 80, height - 195)
    draw_card(screen, card_rect, is_hover=False, radius=12)

    # Table Header
    headers = [("RANK", 85), ("PLAYER", 195), ("TIME", 345), ("GRID", 435)]
    header_y = 135
    for title, h_x in headers:
        draw_text(screen, title, get_font(13, bold=True), COLOR_GOLD, center=(h_x, header_y))
    
    pygame.draw.line(screen, COLOR_BORDER, (55, header_y + 16), (width - 55, header_y + 16), 1)

    # Score rows
    row_y = 175
    if scores:
        for i, score in enumerate(scores[:10]):
            rank = i + 1
            uname = str(score[0])
            s_time = f"{score[1]}s"
            g_size = f"{score[2]}x{score[2]}" if len(score) > 2 and score[2] else "-"

            if rank == 1:
                rank_str = "1st"
                r_color = COLOR_GOLD
            elif rank == 2:
                rank_str = "2nd"
                r_color = COLOR_SILVER
            elif rank == 3:
                rank_str = "3rd"
                r_color = COLOR_BRONZE
            else:
                rank_str = f"#{rank}"
                r_color = COLOR_TEXT_MUTED

            draw_text(screen, rank_str, get_font(15, bold=(rank <= 3)), r_color, center=(85, row_y))
            draw_text(screen, uname, get_font(15, bold=(rank <= 3)), COLOR_TEXT_MAIN, center=(195, row_y))
            draw_text(screen, s_time, get_font(15, bold=True), COLOR_GOLD if rank == 1 else COLOR_TEXT_MAIN, center=(345, row_y))
            draw_text(screen, g_size, get_font(14), COLOR_TEXT_MUTED, center=(435, row_y))
            
            row_y += 31
    else:
        draw_text(screen, "No scores recorded yet!", get_font(17, bold=True), COLOR_TEXT_MAIN, center=(width // 2, 235))
        draw_text(screen, "Complete a Solo maze to claim your spot!", get_font(14), COLOR_TEXT_MUTED, center=(width // 2, 268))

    # Return Button
    btn_rect = pygame.Rect(width // 2 - 110, height - 68, 220, 44)
    mouse_pos = pygame.mouse.get_pos()
    is_btn_hover = btn_rect.collidepoint(mouse_pos)
    draw_card(screen, btn_rect, is_hover=is_btn_hover, radius=10,
              bg_color=(50, 58, 80) if is_btn_hover else COLOR_SURFACE,
              border_color=COLOR_TEXT_MAIN if is_btn_hover else COLOR_BORDER)
    draw_text(screen, "Back to Menu [ESC]", get_font(14, bold=True), COLOR_TEXT_MAIN, center=btn_rect.center)

    pygame.display.flip()
    return btn_rect

def handleHighScoresInput(screen=None, screen_size=None):
    clock = pygame.time.Clock()
    screen_size = screen_size or (560, 620)
    screen = screen or pygame.display.get_surface()

    while True:
        btn_rect = displayHighScores(screen, screen_size)
        mouse_pos = pygame.mouse.get_pos()
        is_hover = btn_rect.collidepoint(mouse_pos)
        safe_set_cursor(pygame.SYSTEM_CURSOR_HAND if is_hover else pygame.SYSTEM_CURSOR_ARROW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(event.pos):
                    return True

        clock.tick(60)

# ----------------- SETTINGS SCREEN -----------------
def settingsMenu(screen, screen_size, bg_colour=None, a_colour=None, na_colour=None, cooldown=150, start_timer=0, g_size=20, s_length=10, torchlight=False):
    initial_grid_size = g_size
    initial_side_length = s_length
    initial_mode = 0
    initial_torch = torchlight

    modes = {
        0: ("Solo", "Classic time attack. Reach the exit as fast as possible."),
        1: ("Two Player", "Local 1v1 split race: Player 1 (WASD) vs Player 2 (Arrows)."),
        2: ("Race", "Race against the computer A* pathfinder to the exit!"),
        3: ("Chase", "Don't get caught! The hunter tracks your steps."),
        4: ("Escape", "Collect 8 hidden keys and break walls to unlock the exit.")
    }
    
    current_mode = initial_mode
    grid_size = g_size
    side_length = s_length
    torch_mode = torchlight
    selected_row = 0

    width, height = screen_size
    pygame.display.set_caption("Yet Another Maze - Settings")
    clock = pygame.time.Clock()

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(COLOR_BG)

        # Title
        draw_text(screen, "SETTINGS", get_font(30, bold=True), COLOR_BLUE, center=(width // 2, 38))
        draw_text(screen, "Adjust maze dimensions and game mode", get_font(14), COLOR_TEXT_MUTED, center=(width // 2, 68))

        # Card 1: Grid Size
        row1_rect = pygame.Rect(45, 95, width - 90, 78)
        row1_hover = row1_rect.collidepoint(mouse_pos) or selected_row == 0
        draw_card(screen, row1_rect, is_hover=row1_hover, radius=10,
                  border_color=COLOR_BLUE if (selected_row == 0 or row1_hover) else COLOR_BORDER)
        draw_text(screen, "GRID SIZE", get_font(12, bold=True), COLOR_BLUE, topleft=(65, 105))
        draw_text(screen, f"{grid_size} x {grid_size} cells", get_font(17, bold=True), COLOR_TEXT_MAIN, topleft=(65, 128))
        
        grid_minus_rect = pygame.Rect(width - 150, 114, 38, 38)
        grid_plus_rect = pygame.Rect(width - 100, 114, 38, 38)
        draw_card(screen, grid_minus_rect, is_hover=grid_minus_rect.collidepoint(mouse_pos), radius=8)
        draw_card(screen, grid_plus_rect, is_hover=grid_plus_rect.collidepoint(mouse_pos), radius=8)
        draw_text(screen, "-", get_font(20, bold=True), COLOR_TEXT_MAIN, center=grid_minus_rect.center)
        draw_text(screen, "+", get_font(20, bold=True), COLOR_TEXT_MAIN, center=grid_plus_rect.center)

        # Card 2: Cell Size
        row2_rect = pygame.Rect(45, 185, width - 90, 78)
        row2_hover = row2_rect.collidepoint(mouse_pos) or selected_row == 1
        draw_card(screen, row2_rect, is_hover=row2_hover, radius=10,
                  border_color=COLOR_BLUE if (selected_row == 1 or row2_hover) else COLOR_BORDER)
        draw_text(screen, "CELL SIZE", get_font(12, bold=True), COLOR_BLUE, topleft=(65, 195))
        draw_text(screen, f"{side_length} px", get_font(17, bold=True), COLOR_TEXT_MAIN, topleft=(65, 218))
        
        cell_minus_rect = pygame.Rect(width - 150, 204, 38, 38)
        cell_plus_rect = pygame.Rect(width - 100, 204, 38, 38)
        draw_card(screen, cell_minus_rect, is_hover=cell_minus_rect.collidepoint(mouse_pos), radius=8)
        draw_card(screen, cell_plus_rect, is_hover=cell_plus_rect.collidepoint(mouse_pos), radius=8)
        draw_text(screen, "-", get_font(20, bold=True), COLOR_TEXT_MAIN, center=cell_minus_rect.center)
        draw_text(screen, "+", get_font(20, bold=True), COLOR_TEXT_MAIN, center=cell_plus_rect.center)

        # Card 3: Game Mode
        row3_rect = pygame.Rect(45, 275, width - 90, 135)
        row3_hover = row3_rect.collidepoint(mouse_pos) or selected_row == 2
        draw_card(screen, row3_rect, is_hover=row3_hover, radius=10,
                  border_color=COLOR_BLUE if (selected_row == 2 or row3_hover) else COLOR_BORDER)
        draw_text(screen, "GAME MODE", get_font(12, bold=True), COLOR_BLUE, topleft=(65, 285))
        
        mode_title, mode_desc = modes[current_mode]
        draw_text(screen, f"Mode {current_mode + 1}: {mode_title}", get_font(18, bold=True), COLOR_TEXT_MAIN, topleft=(65, 308))
        
        desc_rect = pygame.Rect(65, 345, width - 130, 52)
        pygame.draw.rect(screen, (30, 35, 48), desc_rect, border_radius=6)
        draw_text(screen, mode_desc, get_font(12), COLOR_TEXT_MUTED, center=desc_rect.center)

        mode_prev_rect = pygame.Rect(width - 150, 294, 38, 38)
        mode_next_rect = pygame.Rect(width - 100, 294, 38, 38)
        draw_card(screen, mode_prev_rect, is_hover=mode_prev_rect.collidepoint(mouse_pos), radius=8)
        draw_card(screen, mode_next_rect, is_hover=mode_next_rect.collidepoint(mouse_pos), radius=8)
        draw_text(screen, "<", get_font(18, bold=True), COLOR_TEXT_MAIN, center=mode_prev_rect.center)
        draw_text(screen, ">", get_font(18, bold=True), COLOR_TEXT_MAIN, center=mode_next_rect.center)

        # Card 4: Torchlight Toggle
        row4_rect = pygame.Rect(45, 422, width - 90, 78)
        row4_hover = row4_rect.collidepoint(mouse_pos) or selected_row == 3
        draw_card(screen, row4_rect, is_hover=row4_hover, radius=10,
                  border_color=COLOR_BLUE if (selected_row == 3 or row4_hover) else COLOR_BORDER)
        draw_text(screen, "TORCHLIGHT / FOG OF WAR", get_font(12, bold=True), COLOR_BLUE, topleft=(65, 432))
        torch_status = "Enabled (Press [T] in game to toggle)" if torch_mode else "Disabled (Full maze visible)"
        draw_text(screen, torch_status, get_font(14), COLOR_GREEN if torch_mode else COLOR_TEXT_MUTED, topleft=(65, 455))
        
        torch_btn_rect = pygame.Rect(width - 130, 442, 70, 38)
        draw_card(screen, torch_btn_rect, is_hover=torch_btn_rect.collidepoint(mouse_pos), radius=8,
                  bg_color=COLOR_GREEN if torch_mode else (48, 54, 72),
                  border_color=COLOR_GREEN if torch_mode else COLOR_BORDER)
        draw_text(screen, "ON" if torch_mode else "OFF", get_font(14, bold=True),
                  (255, 255, 255) if torch_mode else COLOR_TEXT_MUTED, center=torch_btn_rect.center)

        # Card 5: Save & Return Button
        save_btn_rect = pygame.Rect(width // 2 - 120, height - 72, 240, 46)
        save_hover = save_btn_rect.collidepoint(mouse_pos) or selected_row == 4
        draw_card(screen, save_btn_rect, is_hover=save_hover, radius=8,
                  bg_color=COLOR_BLUE if save_hover else (45, 52, 72),
                  border_color=COLOR_BLUE)
        draw_text(screen, "Save & Return [ENTER]", get_font(14, bold=True), COLOR_TEXT_MAIN, center=save_btn_rect.center)

        any_clickable = any(r.collidepoint(mouse_pos) for r in [
            grid_minus_rect, grid_plus_rect, cell_minus_rect, cell_plus_rect,
            mode_prev_rect, mode_next_rect, torch_btn_rect, save_btn_rect,
            row1_rect, row2_rect, row3_rect, row4_rect
        ])
        safe_set_cursor(pygame.SYSTEM_CURSOR_HAND if any_clickable else pygame.SYSTEM_CURSOR_ARROW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return initial_grid_size, initial_side_length, initial_mode, initial_torch
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return grid_size, side_length, current_mode, torch_mode
                elif event.key == pygame.K_UP:
                    selected_row = (selected_row - 1) % 5
                elif event.key == pygame.K_DOWN:
                    selected_row = (selected_row + 1) % 5
                elif event.key == pygame.K_LEFT:
                    if selected_row == 0:
                        grid_size = max(10, grid_size - 1)
                    elif selected_row == 1:
                        side_length = max(6, side_length - 1)
                    elif selected_row == 2:
                        current_mode = (current_mode - 1) % len(modes)
                    elif selected_row == 3:
                        torch_mode = not torch_mode
                elif event.key == pygame.K_RIGHT:
                    if selected_row == 0:
                        grid_size = min(35, grid_size + 1)
                    elif selected_row == 1:
                        side_length = min(20, side_length + 1)
                    elif selected_row == 2:
                        current_mode = (current_mode + 1) % len(modes)
                    elif selected_row == 3:
                        torch_mode = not torch_mode
                elif event.key == pygame.K_RETURN:
                    if selected_row == 3:
                        torch_mode = not torch_mode
                    else:
                        return grid_size, side_length, current_mode, torch_mode

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if grid_minus_rect.collidepoint(event.pos):
                    grid_size = max(10, grid_size - 1)
                    selected_row = 0
                elif grid_plus_rect.collidepoint(event.pos):
                    grid_size = min(35, grid_size + 1)
                    selected_row = 0
                elif cell_minus_rect.collidepoint(event.pos):
                    side_length = max(6, side_length - 1)
                    selected_row = 1
                elif cell_plus_rect.collidepoint(event.pos):
                    side_length = min(20, side_length + 1)
                    selected_row = 1
                elif mode_prev_rect.collidepoint(event.pos):
                    current_mode = (current_mode - 1) % len(modes)
                    selected_row = 2
                elif mode_next_rect.collidepoint(event.pos):
                    current_mode = (current_mode + 1) % len(modes)
                    selected_row = 2
                elif torch_btn_rect.collidepoint(event.pos) or row4_rect.collidepoint(event.pos):
                    torch_mode = not torch_mode
                    selected_row = 3
                elif save_btn_rect.collidepoint(event.pos):
                    return grid_size, side_length, current_mode, torch_mode
                elif row1_rect.collidepoint(event.pos):
                    selected_row = 0
                elif row2_rect.collidepoint(event.pos):
                    selected_row = 1
                elif row3_rect.collidepoint(event.pos):
                    selected_row = 2

        pygame.display.flip()
        clock.tick(60)

    return grid_size, side_length, current_mode, torch_mode

# ----------------- MAIN MENU SCREEN -----------------
def startScreen(screen=None, current_settings=None):
    if not pygame.get_init():
        pygame.init()

    if current_settings:
        grid_size = current_settings.get('grid_size', 20)
        side_length = current_settings.get('side_length', 10)
        mode = current_settings.get('mode', 0)
        torchlight = current_settings.get('torchlight', False)
    else:
        grid_size = 20
        side_length = 10
        mode = 0
        torchlight = False

    screen_size = (560, 620)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Yet Another Maze - Main Menu")

    # Options with individual color themes
    options = [
        ("Start Game", "Enter and solve the maze", "▶", COLOR_GREEN),
        ("High Scores", "View fastest completion records", "🏆", COLOR_GOLD),
        ("Settings", "Configure size, mode & torch", "⚙", COLOR_BLUE),
        ("Exit Game", "Quit to desktop", "✕", COLOR_RED)
    ]
    current_selection = 0

    width, height = screen_size
    clock = pygame.time.Clock()

    Settings = False
    HighScores = False

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(COLOR_BG)

        # Header Title
        draw_text(screen, "Yet Another Maze", get_font(34, bold=True), COLOR_TEXT_MAIN, center=(width // 2, 85))
        draw_text(screen, "Classic Labyrinth Game", get_font(15), COLOR_TEXT_MUTED, center=(width // 2, 122))

        # Menu Cards
        button_rects = []
        btn_start_y = 175
        btn_height = 68
        btn_spacing = 16

        for i, (title, subtitle, icon, accent_col) in enumerate(options):
            b_rect = pygame.Rect(60, btn_start_y + i * (btn_height + btn_spacing), width - 120, btn_height)
            button_rects.append(b_rect)

            is_hover = b_rect.collidepoint(mouse_pos)
            is_active = (i == current_selection)

            # Clean card with color accent on hover
            card_bg = (44, 52, 72) if (is_hover or is_active) else COLOR_SURFACE
            card_border = accent_col if (is_hover or is_active) else COLOR_BORDER
            pygame.draw.rect(screen, card_bg, b_rect, border_radius=10)
            pygame.draw.rect(screen, card_border, b_rect, width=2 if (is_hover or is_active) else 1, border_radius=10)

            # Colorful icon box
            icon_rect = pygame.Rect(b_rect.x + 16, b_rect.y + 15, 38, 38)
            pygame.draw.rect(screen, accent_col, icon_rect, border_radius=8)
            draw_text(screen, icon, get_font(18, bold=True), (255, 255, 255), center=icon_rect.center)

            # Text labels
            text_color = (255, 255, 255) if (is_hover or is_active) else COLOR_TEXT_MAIN
            draw_text(screen, title, get_font(17, bold=True), text_color, topleft=(b_rect.x + 68, b_rect.y + 14))
            draw_text(screen, subtitle, get_font(13), COLOR_TEXT_MUTED, topleft=(b_rect.x + 68, b_rect.y + 37))

        # Bottom Hint
        draw_text(screen, "Select with Mouse or Arrow Keys [↑/↓] • [ENTER] Confirm", get_font(12),
                  COLOR_TEXT_MUTED, center=(width // 2, height - 35))

        # Cursor
        any_hover = any(r.collidepoint(mouse_pos) for r in button_rects)
        safe_set_cursor(pygame.SYSTEM_CURSOR_HAND if any_hover else pygame.SYSTEM_CURSOR_ARROW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, grid_size, side_length, mode, torchlight

            if event.type == pygame.MOUSEMOTION:
                for idx, r in enumerate(button_rects):
                    if r.collidepoint(event.pos):
                        current_selection = idx

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for idx, r in enumerate(button_rects):
                    if r.collidepoint(event.pos):
                        if idx == 0:
                            return True, grid_size, side_length, mode, torchlight
                        elif idx == 1:
                            HighScores = True
                        elif idx == 2:
                            Settings = True
                        elif idx == 3:
                            return False, grid_size, side_length, mode, torchlight

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    current_selection = (current_selection - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    current_selection = (current_selection + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if current_selection == 0:
                        return True, grid_size, side_length, mode, torchlight
                    elif current_selection == 1:
                        HighScores = True
                    elif current_selection == 2:
                        Settings = True
                    elif current_selection == 3:
                        return False, grid_size, side_length, mode, torchlight
                elif event.key == pygame.K_ESCAPE:
                    return False, grid_size, side_length, mode, torchlight

        if Settings:
            res = settingsMenu(screen, screen_size, COLOR_BG, COLOR_BLUE, COLOR_TEXT_MAIN,
                               150, pygame.time.get_ticks(), grid_size, side_length, torchlight)
            if len(res) >= 4:
                grid_size, side_length, mode, torchlight = res
            else:
                grid_size, side_length, mode = res
            pygame.display.set_caption("Yet Another Maze - Main Menu")
            Settings = False

        if HighScores:
            handleHighScoresInput(screen, screen_size)
            pygame.display.set_caption("Yet Another Maze - Main Menu")
            HighScores = False

        pygame.display.flip()
        clock.tick(60)

    return False, grid_size, side_length, mode, torchlight

# ----------------- GAME OVER / VICTORY SCREEN -----------------
def endGame(mode, value, screen=None):
    if not pygame.get_init():
        pygame.init()

    screen_size = (560, 620)
    screen = screen or pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Yet Another Maze - Game Result")

    width, height = screen_size
    clock = pygame.time.Clock()

    if mode == 0:
        headline = "MAZE COMPLETED!"
        h_color = COLOR_GREEN
        stat_main = f"{value} seconds"
        stat_label = "Your Time"
        sub_desc = "Nice run! Score saved to High Scores."
    elif mode == 1:
        headline = f"PLAYER {value} WINS!"
        h_color = COLOR_GREEN if value == 1 else COLOR_BLUE
        stat_main = f"Player {value} reached the goal first!"
        stat_label = "Winner"
        sub_desc = "Great race!"
    elif mode in (2, 3):
        if value == 1:
            headline = "YOU WON!"
            h_color = COLOR_GREEN
            stat_main = "You reached the goal first!"
            stat_label = "Result"
            sub_desc = "Outran the computer player!"
        else:
            headline = "COMPUTER WON!"
            h_color = COLOR_RED
            stat_main = "Computer reached the goal first"
            stat_label = "Result"
            sub_desc = "Better luck next time!"
    elif mode == 4:
        if value == 1:
            headline = "YOU ESCAPED!"
            h_color = COLOR_GREEN
            stat_main = "All 8 Keys Gathered!"
            stat_label = "Result"
            sub_desc = "Successfully exited the maze."
        else:
            headline = "CAUGHT!"
            h_color = COLOR_RED
            stat_main = "The hunter caught you"
            stat_label = "Result"
            sub_desc = "Try breaking walls faster!"
    else:
        headline = "GAME OVER"
        h_color = COLOR_BLUE
        stat_main = str(value)
        stat_label = "Result"
        sub_desc = ""

    # Action buttons: Play Again & Main Menu
    btn_replay = pygame.Rect(width // 2 - 200, height - 90, 185, 46)
    btn_menu = pygame.Rect(width // 2 + 15, height - 90, 185, 46)

    carryOn = True
    action = "menu"

    while carryOn:
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(COLOR_BG)

        # Result Card
        card_rect = pygame.Rect(45, 75, width - 90, height - 200)
        draw_card(screen, card_rect, is_hover=False, radius=12, border_color=h_color)

        # Headline
        draw_text(screen, headline, get_font(28, bold=True), h_color, center=(width // 2, 130))

        # Stat box
        stat_box = pygame.Rect(card_rect.centerx - 160, 180, 320, 85)
        pygame.draw.rect(screen, (30, 35, 48), stat_box, border_radius=8)
        draw_text(screen, stat_label.upper(), get_font(12, bold=True), COLOR_GOLD, center=(stat_box.centerx, stat_box.y + 24))
        draw_text(screen, stat_main, get_font(22, bold=True), COLOR_TEXT_MAIN, center=(stat_box.centerx, stat_box.y + 54))

        # Description
        draw_text(screen, sub_desc, get_font(15), COLOR_TEXT_MUTED, center=(width // 2, 305))

        # Play Again Button (Green)
        hover_replay = btn_replay.collidepoint(mouse_pos)
        draw_card(screen, btn_replay, is_hover=hover_replay, radius=8,
                  bg_color=COLOR_GREEN if hover_replay else (20, 150, 105),
                  border_color=COLOR_GREEN)
        draw_text(screen, "Play Again [ENTER]", get_font(14, bold=True), (255, 255, 255), center=btn_replay.center)

        # Main Menu Button (Blue/Slate)
        hover_menu = btn_menu.collidepoint(mouse_pos)
        draw_card(screen, btn_menu, is_hover=hover_menu, radius=8,
                  bg_color=(50, 60, 80) if hover_menu else (38, 45, 62),
                  border_color=COLOR_TEXT_MUTED)
        draw_text(screen, "Main Menu [ESC]", get_font(14, bold=True), COLOR_TEXT_MAIN, center=btn_menu.center)

        any_btn_hover = hover_replay or hover_menu
        safe_set_cursor(pygame.SYSTEM_CURSOR_HAND if any_btn_hover else pygame.SYSTEM_CURSOR_ARROW)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                action = "menu"
                carryOn = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    action = "replay"
                    carryOn = False
                elif event.key == pygame.K_ESCAPE:
                    action = "menu"
                    carryOn = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_replay.collidepoint(event.pos):
                    action = "replay"
                    carryOn = False
                elif btn_menu.collidepoint(event.pos):
                    action = "menu"
                    carryOn = False

        pygame.display.flip()
        clock.tick(60)

    return action
