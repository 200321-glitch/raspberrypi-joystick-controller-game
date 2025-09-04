rom ursina import *
import random
from ursina import *
import random

app = Ursina()

window.color = color.green  # Whole screen is green area

# Boundaries for movement
BOUND_X = 8
BOUND_Z = 4.5

# Speed setting
CUBE_SPEED = 0.1

# Load PNG textures
img1 = load_texture('IMG_5032.png')  # Loojaw's texture
img2 = load_texture('IMG_7939.png')  # Sahisa's texture

# Player 1 (Loojaw)
player1 = Entity(
    model='cube',
    texture=img1,
    position=(-2, 0, 0),
    collider='box',
    texture_rotation=90
)
player1_label = Text(
    text='Loojaw',
    origin=(0, 0),
    scale=1.5,
    position=(player1.x, player1.y + 1.5, player1.z)
)

# Player 2 (Sahisa)
player2 = Entity(
    model='cube',
    texture=img2,
    position=(2, 0, 0),
    collider='box',
    texture_rotation=90
)
player2_label = Text(
    text='Sahisa',
    origin=(0, 0),
    scale=1.5,
    position=(player2.x, player2.y + 1.5, player2.z)
)
# Camera setup (top-down)
camera.position = (0, 20, -0.1)
camera.rotation_x = 90

# Game over text
game_over_text = Text(
    text='Game Over! Press R to Restart',
    origin=(0, 0),
    scale=2,
    color=color.red,
    visible=False
)

# Timer and score
timer_text = Text(
    text='60',
    position=(0.85, 0.45),
    scale=2,
    color=color.black
)

score_text = Text(
    text='Loojaw: 0   Sahisa: 0',
    position=(0, 0.45),
    origin=(0, 0),
    scale=2,
    color=color.black
)

# Game variables
game_time = 60
score1 = 0
score2 = 0
apples = []
APPLE_COUNT = 2

def spawn_apple():
    x = random.uniform(-BOUND_X + 0.5, BOUND_X - 0.5)
    z = random.uniform(-BOUND_Z + 0.5, BOUND_Z - 0.5)
    apple = Entity(
        model='cube',
        color=color.red,
        position=(x, 0, z),
        scale=0.4,
        collider='box'
    )
    apples.append(apple)

def spawn_initial_apples():
    for apple in apples:
        destroy(apple)
    apples.clear()
    for _ in range(APPLE_COUNT):
        spawn_apple()

def restart_game():
    global game_time, score1, score2
    player1.position = (-2, 0, 0)
    player2.position = (2, 0, 0)
    game_time = 60
    score1 = 0
    score2 = 0
    spawn_initial_apples()
    update_score_text()
    timer_text.text = str(int(game_time))
    game_over_text.visible = False

def keep_inside_bounds(entity):
    entity.x = max(-BOUND_X, min(BOUND_X, entity.x))
    entity.z = max(-BOUND_Z, min(BOUND_Z, entity.z))

def update_score_text():
    score_text.text = f"Loojaw: {score1}   Sahisa: {score2}"

def update():
    global game_time, score1, score2

    # Move name labels with cubes
    player1_label.position = (player1.x, player1.y + 1.5, player1.z)
    player2_label.position = (player2.x, player2.y + 1.5, player2.z)
    # Restart
    if game_over_text.visible and held_keys['r']:
        restart_game()

    if not game_over_text.visible:
        game_time -= time.dt
        timer_text.text = str(int(game_time))
        if game_time <= 0:
            game_over_text.text = 'Time Up! Press R to Restart'
            game_over_text.visible = True
            return

        # Player 1 controls (WASD)
        if held_keys['w']:
            player1.z += CUBE_SPEED
        if held_keys['s']:
            player1.z -= CUBE_SPEED
        if held_keys['a']:
            player1.x -= CUBE_SPEED
        if held_keys['d']:
            player1.x += CUBE_SPEED

        # Player 2 controls (arrow keys)
        if held_keys['up arrow']:
            player2.z += CUBE_SPEED
        if held_keys['down arrow']:
            player2.z -= CUBE_SPEED
        if held_keys['left arrow']:
            player2.x -= CUBE_SPEED
        if held_keys['right arrow']:
            player2.x += CUBE_SPEED

        keep_inside_bounds(player1)
        keep_inside_bounds(player2)
  # Apple collection
        for apple in apples[:]:
            if player1.intersects(apple).hit:
                score1 += 1
                update_score_text()
                apples.remove(apple)
                destroy(apple)
                spawn_apple()
            elif player2.intersects(apple).hit:
                score2 += 1
                update_score_text()
                apples.remove(apple)
                destroy(apple)
                spawn_apple()

        # Collision between players
        if player1.intersects(player2).hit:
            game_over_text.text = 'Game Over! Press R to Restart'
            game_over_text.visible = True

# Start the game
spawn_initial_apples()
app.run()

