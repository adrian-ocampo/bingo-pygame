import pygame
import sys
from button import Button
from random import randint

class Tile:
    registry = []

    def __init__(self, tile, position):
        x,y = position
        x += 105
        y += 105
        self.position = position
        self.image = tile
        self.rect = tile.get_rect(center=(x,y))
        self.mask = pygame.mask.from_surface(self.image)
        self.registry.append(self)
        
    def update():
        del Tile.registry[:25]

    def get_image(self):
        return self.image
    
    def get_position(self):
        return self.position
    
    def get_mask(self):
        return self.mask


def scale_and_rotate(surface, width, height, angle):
    surface = pygame.transform.scale(surface, (width, height))
    surface = pygame.transform.rotate(surface, angle)
    return surface

def update_board(): # Redraw Surfaces
    for i in range(len(tiles)):
        for j in range(len(tiles)):
            Tile(tiles[i][j]["Type"], tiles[i][j]["Position"])
            win.blit(tiles[i][j]["Type"], tiles[i][j]["Position"])

    for i in range(len(Tile.registry)):  
        win.blit(Tile.registry[i].get_image(), Tile.registry[i].get_position())
    Tile.update()

def update_tiles(move_count, death_count, prev_count):
    j = -1
    k = 0
    for i in range(len(Tile.registry)):
        # Checks if mouse position overlaps mask (tile)
        pos_in_mask = GAME_MOUSE_POS[0] - Tile.registry[i].rect.x, GAME_MOUSE_POS[1] - Tile.registry[i].rect.y
        touching = Tile.registry[i].rect.collidepoint(GAME_MOUSE_POS) and Tile.registry[i].mask.get_at(pos_in_mask)
        k +=1
        # Every 5th i, will increment j and set k back to 0
        if i % 5 == 0:
            j += 1
            k = 0

        if touching and (tiles[j][k]["Type"] != bingo_black and tiles[j][k]["Type"] != bingo_red):
            move_count += 1
            death_count -= 1
            swap_tile(j,k) # Flips Clicked Tile
            swap_adjacent_tiles(j,k) # Flips Adjacent Tiles
            update_state() # Before checking bingos update hash map
            death_count, prev_count = check_bingo(death_count, prev_count)
            type_to_color(j , k) # Assigns Color Property based on Type Property
            for i in range(len(tiles)):
                for j in range(len(tiles)):
                    tiles_history.append(tiles[i][j]["Color"]) # Saves tile history for Undoing moves
            counter_history.append((move_count, death_count))
            break

    if debug_move_history:
        print("--- Counter History (Move Count / Death Count)---")
        print(counter_history)
    return move_count, death_count, prev_count
            
def update_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    win.blit(img, (x, y))

def swap_tile(j,k): 

    if tiles[j][k]["Type"] == tile_red:
        tiles[j][k]["Type"] = skull_red
    elif tiles[j][k]["Type"] == skull_red:
        tiles[j][k]["Type"] = tile_red
    if tiles[j][k]["Type"] == tile_black:
        tiles[j][k]["Type"] = skull_black
    elif tiles[j][k]["Type"] == skull_black:
        tiles[j][k]["Type"] = tile_black

def update_state():
    for i in range(len(tiles)):
        for j in range(len(tiles)):
            tiles[i][j]["Flipped"] = tile_states[tiles[i][j]["Type"]]

def check_bingo(death_count, prev_count):
    isBingo = False
    bingo_count = 0
    # Checks Vertical Bingos
    j = 0
    k = 0
    for k in range(len(tiles)):
        if all([tiles[j][k]["Flipped"], tiles[j+1][k]["Flipped"], tiles[j+2][k]["Flipped"], tiles[j+3][k]["Flipped"], tiles[j+4][k]["Flipped"]]):
            bingo_count +=1
            if k % 2 == 0:
                tiles[j][k]["Type"] = bingo_red
                tiles[j+1][k]["Type"] = bingo_black
                tiles[j+2][k]["Type"] = bingo_red
                tiles[j+3][k]["Type"] = bingo_black
                tiles[j+4][k]["Type"] = bingo_red
            else:
                tiles[j][k]["Type"] = bingo_black
                tiles[j+1][k]["Type"] = bingo_red
                tiles[j+2][k]["Type"] = bingo_black
                tiles[j+3][k]["Type"] = bingo_red
                tiles[j+4][k]["Type"] = bingo_black
    
    # Checks Horizontal Bingos
    k = 0
    for j in range(len(tiles)):
        if all([tiles[j][k]["Flipped"], tiles[j][k+1]["Flipped"], tiles[j][k+2]["Flipped"], tiles[j][k+3]["Flipped"], tiles[j][k+4]["Flipped"]]):
            bingo_count +=1
            if  j % 2 == 0:
                tiles[j][k]["Type"] = bingo_red
                tiles[j][k+1]["Type"] = bingo_black
                tiles[j][k+2]["Type"] = bingo_red
                tiles[j][k+3]["Type"] = bingo_black
                tiles[j][k+4]["Type"] = bingo_red
            else:
                tiles[j][k]["Type"] = bingo_black
                tiles[j][k+1]["Type"] = bingo_red
                tiles[j][k+2]["Type"] = bingo_black
                tiles[j][k+3]["Type"] = bingo_red
                tiles[j][k+4]["Type"] = bingo_black

    # Check for Diagonal Bingos
    j = 0
    k = 0        
    if all([tiles[j][k]["Flipped"], tiles[j+1][k+1]["Flipped"], tiles[j+2][k+2]["Flipped"], tiles[j+3][k+3]["Flipped"], tiles[j+4][k+4]["Flipped"]]):
            bingo_count +=1
            for i in range(len(tiles)):
                tiles[i][i]["Type"] = bingo_red 
    k = 4
    if all([tiles[j][k]["Flipped"], tiles[j+1][k-1]["Flipped"], tiles[j+2][k-2]["Flipped"], tiles[j+3][k-3]["Flipped"], tiles[j+4][k-4]["Flipped"]]):
            bingo_count +=1
            for i in range(len(tiles)):
                tiles[i][4-i]["Type"] = bingo_red 

    # If no bingo at 0 death counter, end game.
    if debug_bingo_count:
        print(f'Bingo Count: {bingo_count}')

    if (bingo_count >= prev_count + 1):
        isBingo = True

    # Win Condition
    if (bingo_count == 12):
        print("You won")
        sys.exit()

    # Lose Condition
    if (not isBingo and death_count == 0):
        print("You have died")
        sys.exit()
    elif (isBingo and death_count >= 0):
        death_count = 4

    return death_count, bingo_count

def swap_adjacent_tiles(j,k): 
    
    # Splash Adjacent Black Tiles
    if tiles[j][k]["Type"] in red_tiles:
        check_center(j,k)
        check_sides(j,k)
        check_corners(j,k)

    # Splash Adjacent Red Tiles
    if tiles[j][k]["Type"] in black_tiles:
        check_center(j,k)
        check_sides(j,k)

def check_center(j,k):
    if (j > 0 and j < 4) and (k > 0 and k < 4):
        tiles[j+1][k]["Type"] = flipped_tiles[tiles[j+1][k]["Type"]]
        tiles[j-1][k]["Type"] = flipped_tiles[tiles[j-1][k]["Type"]]
        tiles[j][k+1]["Type"] = flipped_tiles[tiles[j][k+1]["Type"]]
        tiles[j][k-1]["Type"] = flipped_tiles[tiles[j][k-1]["Type"]]

def check_sides(j,k):
    if (j > 0 and j < 4) or (k > 0 and k < 4):
        # Top Sides
        if (j == 0) and (k > 0 and k < 4):
            tiles[j+1][k]["Type"] = flipped_tiles[tiles[j+1][k]["Type"]]
            tiles[j][k+1]["Type"] = flipped_tiles[tiles[j][k+1]["Type"]]
            tiles[j][k-1]["Type"] = flipped_tiles[tiles[j][k-1]["Type"]]
        # Left Sides
        if (j > 0 and j < 4) and (k == 0):
            tiles[j+1][k]["Type"] = flipped_tiles[tiles[j+1][k]["Type"]]
            tiles[j-1][k]["Type"] = flipped_tiles[tiles[j-1][k]["Type"]]
            tiles[j][k+1]["Type"] = flipped_tiles[tiles[j][k+1]["Type"]]
        # Bottom Sides
        if (j == 4) and (k > 0 and k < 4):
            tiles[j-1][k]["Type"] = flipped_tiles[tiles[j-1][k]["Type"]]
            tiles[j][k-1]["Type"] = flipped_tiles[tiles[j][k-1]["Type"]]
            tiles[j][k+1]["Type"] = flipped_tiles[tiles[j][k+1]["Type"]]

        # Right Sides
        if (j > 0 and j < 4) and (k == 4):
            tiles[j+1][k]["Type"] = flipped_tiles[tiles[j+1][k]["Type"]]
            tiles[j-1][k]["Type"] = flipped_tiles[tiles[j-1][k]["Type"]]
            tiles[j][k-1]["Type"] = flipped_tiles[tiles[j][k-1]["Type"]]

def check_corners(j,k):
    # Top Left
    if (j == 0 and k == 0):
        tiles[j+1][k]["Type"] = flipped_tiles[tiles[j+1][k]["Type"]]
        tiles[j][k+1]["Type"] = flipped_tiles[tiles[j][k+1]["Type"]]

    # Top Right
    if (j == 0 and k == 4):
        tiles[j+1][k]["Type"] = flipped_tiles[tiles[j+1][k]["Type"]]
        tiles[j][k-1]["Type"] = flipped_tiles[tiles[j][k-1]["Type"]]

    # Bottom Left
    if (j == 4 and k == 0):
        tiles[j-1][k]["Type"] = flipped_tiles[tiles[j-1][k]["Type"]]
        tiles[j][k+1]["Type"] = flipped_tiles[tiles[j][k+1]["Type"]]

    # Bottom Right
    if (j == 4 and k == 4):
        tiles[j-1][k]["Type"] = flipped_tiles[tiles[j-1][k]["Type"]]
        tiles[j][k-1]["Type"] = flipped_tiles[tiles[j][k-1]["Type"]]

def type_to_color(i, j):
    for i in range(len(tiles)):
        for j in range(len(tiles)):
            tiles[i][j]["Color"] = colors[tiles[i][j]["Type"]]

def color_to_type(old_tiles):
    colors_reversed = {v : k for k, v in colors.items()}
    for i in range(len(old_tiles)):
        for j in range(len(old_tiles)):
            old_tiles[i][j]["Type"] = colors_reversed[old_tiles[i][j]["Color"]]

def reset():
    setup = [[
    {"Tile": "A5", "Type": tile_red, "Position": (500, 0), "Color": colors[tile_red], "Flipped": False},
    {"Tile": "B5", "Type": tile_black, "Position": (555, 55), "Color": colors[tile_black], "Flipped": False},
    {"Tile": "C5", "Type": tile_red, "Position": (610, 110), "Color": colors[tile_red], "Flipped": False},
    {"Tile": "D5", "Type": tile_black, "Position": (665, 165), "Color": colors[tile_black], "Flipped": False},
    {"Tile": "E5", "Type": tile_red, "Position": (720, 220), "Color": colors[tile_red], "Flipped": False}],
    [{"Tile": "A4", "Type": tile_black, "Position": (445, 55), "Color": colors[tile_black], "Flipped": False},
    {"Tile": "B4", "Type": tile_red, "Position": (500, 110), "Color": colors[tile_red], "Flipped": False},
    {"Tile": "C4", "Type": tile_black, "Position": (555, 165), "Color": colors[tile_black], "Flipped": False},
    {"Tile": "D4", "Type": tile_red, "Position": (610, 220), "Color": colors[tile_red], "Flipped": False},
    {"Tile": "E4", "Type": tile_black, "Position": (665, 275), "Color": colors[tile_black], "Flipped": False}],
    [{"Tile": "A3", "Type": tile_red, "Position": (390, 110), "Color": colors[tile_red], "Flipped": False},
    {"Tile": "B3", "Type": tile_black, "Position": (445, 165), "Color": colors[tile_black], "Flipped": False},
    {"Tile": "C3", "Type": tile_red, "Position": (500, 220), "Color": colors[tile_red], "Flipped": False},
    {"Tile": "D3", "Type": tile_black, "Position": (555, 275), "Color": colors[tile_black], "Flipped": False},
    {"Tile": "E3", "Type": tile_red, "Position": (610, 330), "Color": colors[tile_red], "Flipped": False}],
    [{"Tile": "A2", "Type": tile_black, "Position": (335, 165), "Color": colors[tile_black], "Flipped": False},
    {"Tile": "B2", "Type": tile_red, "Position": (390, 220), "Color": colors[tile_red], "Flipped": False},
    {"Tile": "C2", "Type": tile_black, "Position": (445, 275), "Color": colors[tile_black], "Flipped": False},
    {"Tile": "D2", "Type": tile_red, "Position": (500, 330), "Color": colors[tile_red], "Flipped": False},
    {"Tile": "E2", "Type": tile_black, "Position": (555, 385), "Color": colors[tile_black], "Flipped": False}],
    [{"Tile": "A1", "Type": tile_red, "Position": (280, 220), "Color": colors[tile_red], "Flipped": False},
    {"Tile": "B1", "Type": tile_black, "Position": (335, 275), "Color": colors[tile_black], "Flipped": False},
    {"Tile": "C1", "Type": tile_red, "Position": (390, 330), "Color": colors[tile_red], "Flipped": False},
    {"Tile": "D1", "Type": tile_black, "Position": (445, 385), "Color": colors[tile_black], "Flipped": False},
    {"Tile": "E1", "Type": tile_red, "Position": (500, 440), "Color": colors[tile_red], "Flipped": False}]]
    
    return setup

def undo():
    old_tiles = tiles
    
    k = len(tiles_history) - 50
    if len(tiles_history) > 25:
        for i in range(len(tiles)):
            for j in range(len(tiles)):
                old_tiles[i][j]["Color"] = tiles_history[k]
                k+=1
    color_to_type(old_tiles) # Helper Function --> Assigns Type Property based on Color Property

    if len(tiles_history) > 25: # Keep first 25 Elements to prevent undoing to non-existent index
       del tiles_history[(len(tiles_history)-25):len(tiles_history)] # Deletes last 25 elements 
    if len(counter_history) > 1:
        old_counters = counter_history[-2]
        del counter_history[-2:-1]
    else:
        old_counters = (0, 4)
        del counter_history[0]
    return old_tiles, *old_counters

def random_tiles():
    random_list = []
    for _ in range(amount_of_tiles):
        while True:
            random_row = randint(0,4)
            random_column = randint(0,4)
            if (random_row, random_column) not in random_list:
                random_list.append((random_row, random_column))
                break
        swap_tile(random_row, random_column)
        type_to_color(random_row, random_column)
        update_state()

# Debug Settings
debug_bingo_count = True
debug_move_count = False
debug_death_count = False
debug_move_history = True
debug_tile_history = False

# Setup
pygame.init()
WIDTH = 1280
HEIGHT = 720
resolution = WIDTH, HEIGHT
pygame.display.set_caption("Bingo")
win = pygame.display.set_mode(resolution)
clock = pygame.time.Clock()
clock.tick(60)
text_font = pygame.font.SysFont("comicsans", 30)


# Images
tile_black = pygame.image.load("resources/tile_black.png").convert_alpha()
tile_red = pygame.image.load("resources/tile_red.png").convert_alpha()
bingo_black = pygame.image.load("resources/bingo_black.png").convert_alpha()
bingo_red = pygame.image.load("resources/bingo_red.png").convert_alpha()
skull_black = pygame.image.load("resources/skull_black.png").convert_alpha()
skull_red = pygame.image.load("resources/skull_red.png").convert_alpha()
highlight = pygame.image.load("resources/hover.png").convert_alpha()
background = pygame.image.load("resources/background.png").convert_alpha()

# Rotation and Size
tile_black = scale_and_rotate(tile_black, 150, 150, -45)
tile_red = scale_and_rotate(tile_red, 150, 150, -45)
bingo_black = scale_and_rotate(bingo_black, 150, 150, -45)
bingo_red = scale_and_rotate(bingo_red, 150, 150, -45)
skull_black = scale_and_rotate(skull_black, 150, 150, -45)
skull_red = scale_and_rotate(skull_red, 150, 150, -45)
background = scale_and_rotate(background, 717, 716, -45)
highlight = scale_and_rotate(highlight, 72, 72, -45)
highlight.set_alpha(100)

# Color Dictionary
colors = {tile_red: "tile_red",
    tile_black: "tile_black",
    skull_red: "skull_red",
    skull_black: "skull_black",
    bingo_red: "bingo_red",
    bingo_black: "bingo_black"
}
# Tile States
tile_states = {
    tile_red : False,
    tile_black : False,
    skull_red : True,
    skull_black : True,
    bingo_red : True,
    bingo_black : True
}

flipped_tiles = {
    skull_black : tile_black,
    tile_black : skull_black,
    skull_red : tile_red,
    tile_red : skull_red,
    bingo_black : bingo_black,
    bingo_red : bingo_red
}

red_tiles = [tile_red, skull_red, bingo_red]
black_tiles = [tile_black, skull_black, bingo_black]

# Initalize Tiles and History
tiles = reset()
tiles_history = []
counter_history = []

# Counters
move_count = 0
death_count = 4
prev_count = 0

# Initalize n Random Starting Tiles
amount_of_tiles = 2
random_tiles()

# Initialize History and Instances
for i in range(len(tiles)):
    for j in range(len(tiles)):
        tiles_history.append(tiles[i][j]["Color"])

for i in range(len(tiles)):
    for j in range(len(tiles)):
        Tile(tiles[i][j]["Type"], tiles[i][j]["Position"])

# Menu
def menu():
    WHITE = (255,255,255)
    GREY = (166,166,166)
    PLAY_BUTTON = Button((WHITE), (WIDTH/2 - 150), 250, 300, 100, "Play")
    SETTINGS_BUTTON = Button((WHITE), (WIDTH/2 - 150), 400, 300, 100, "Settings")
    QUIT_BUTTON = Button((WHITE), (WIDTH/2 - 150), 550, 300, 100, "Quit")
    title_font = pygame.font.SysFont("comicsans", 80)
    text = title_font.render("Bingo", True, (216,202,173))

    while True:
        # Background
        # win.fill(pygame.Color("DarkGrey"))
        win.fill((16,11,34))
        win.blit(text, (WIDTH/2 - 95, 110))
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        PLAY_BUTTON.draw(win, True)
        SETTINGS_BUTTON.draw(win, True)
        QUIT_BUTTON.draw(win, True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.isOver(MENU_MOUSE_POS):
                    play()
                if SETTINGS_BUTTON.isOver(MENU_MOUSE_POS):
                    settings()
                if QUIT_BUTTON.isOver(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()  
            if event.type == pygame.MOUSEMOTION:
                if PLAY_BUTTON.isOver(MENU_MOUSE_POS):
                    PLAY_BUTTON.color = (GREY)
                else:
                    PLAY_BUTTON.color = (WHITE)
                if SETTINGS_BUTTON.isOver(MENU_MOUSE_POS):
                    SETTINGS_BUTTON.color = (GREY)
                else:
                    SETTINGS_BUTTON.color = (WHITE)
                if QUIT_BUTTON.isOver(MENU_MOUSE_POS):
                    QUIT_BUTTON.color = (GREY)
                else:
                    QUIT_BUTTON.color = (WHITE)
        pygame.display.flip()
        pygame.display.update()
        
# Game
def play():
    global move_count, death_count, prev_count, GAME_MOUSE_POS, tiles

    while True:
        # Background
        # win.fill(pygame.Color("DarkGrey"))
        win.fill((16,11,34))
        win.blit(background, (99,-180))
        GAME_MOUSE_POS = pygame.mouse.get_pos()

        # Text
        update_text("Move Count: {0}".format(move_count), text_font, (216,202,173), 750, 500)
        if death_count > 1:
            update_text("Score a bingo within {0} moves or lose.".format(death_count), text_font, (216,202,173), 350, 650)
        else:
            update_text("Score a bingo in the next move or lose.", text_font, (216,202,173), 350, 650)

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed() == (True,False,False):
                move_count, death_count, prev_count = update_tiles(move_count, death_count, prev_count)
                if debug_move_count:
                    print(f'Move Count: {move_count}')
                if debug_death_count:
                    print(f'Death Count: {death_count}')
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    tiles = reset()
                    counter_history = []
                    random_tiles()
                    move_count, death_count, prev_count = 0, 4, 0
                    del tiles_history[::]
                    for i in range(len(tiles)):
                        for j in range(len(tiles)):
                            tiles_history.append(tiles[i][j]["Color"])
                            
                if event.key == pygame.K_BACKSPACE and move_count != 0: 
                    tiles, move_count, death_count = undo()
                    if debug_move_history:
                        print("--- Counter History (Move Count / Death Count)---")
                        print(counter_history)
                    if debug_tile_history:
                        print("--- Tiles History---")
                        print(tiles_history)

        # Board
        update_board()
        
        # Hover-over Effect
        for i in range(len(Tile.registry)):
            pos_in_mask = GAME_MOUSE_POS[0] - Tile.registry[i].rect.x, GAME_MOUSE_POS[1] - Tile.registry[i].rect.y
            touching = Tile.registry[i].rect.collidepoint(GAME_MOUSE_POS) and Tile.registry[i].mask.get_at(pos_in_mask)
            if touching:
                win.blit(highlight, (Tile.registry[i].rect.x+57, Tile.registry[i].rect.y + 58))

        # Update
        pygame.display.flip()
        pygame.display.update()
        clock.tick(60)

def settings():
    print("Entered Settings")

if __name__ == "__main__":
    
    menu()