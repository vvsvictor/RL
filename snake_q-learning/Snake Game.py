"""
Snake Eater
Made with PyGame
"""

import pygame, sys, time, random, math
import numpy as np

#Q-learning matrix
Q = np.zeros([2**12, 4])
alpha = 0.1
gamma = 0.8

def upateQ(state, action, reward, next_state):
    #Q(s,a) = Q(s,a) + alpha*(reward + gamma*max(Q(s',a')) - Q(s,a))
    Q[state, action] = Q[state, action] + alpha*(reward + gamma*np.max(Q[next_state, :]) - Q[state, action])

# Difficulty settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
difficulty = 60

# Window size
frame_size_x = 720
frame_size_y = 480

# Checks for errors encountered
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')


# Initialise game window
pygame.display.set_caption('Snake Eater')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))


# Colors (R, G, B)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)


# FPS (frames per second) controller
fps_controller = pygame.time.Clock()


# Game variables
snake_pos = [100, 50]
snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]

food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
food_spawn = True

direction = 'RIGHT'
change_to = direction

score = 0

def get_state(dirSnake, snakePos, snake_body, foodPos):
    s = []
    # Snake direction
    s.append(int(dirSnake == 'UP'))
    s.append(int(dirSnake == 'DOWN'))
    s.append(int(dirSnake == 'LEFT'))
    s.append(int(dirSnake == 'RIGHT'))
    #Food direction
    s.append(int(snakePos[0] < foodPos[0])) #food is left
    s.append(int(snakePos[0] > foodPos[0])) #food is right
    s.append(int(snakePos[1] < foodPos[1])) #food is up
    s.append(int(snakePos[1] > foodPos[1])) #food is down
    #Danger and body
    s.append(int(snakePos[0] == 10 or [snakePos[0]-10, snakePos[1]] in snake_body)) #danger left
    s.append(int(snakePos[0] == frame_size_x-10 or [snakePos[0]+10, snakePos[1]] in snake_body)) #danger right
    s.append(int(snakePos[1] == 10 or [snakePos[0], snakePos[1]-10] in snake_body)) #danger up
    s.append(int(snakePos[1] == frame_size_y-10 or [snakePos[0], snakePos[1]+10] in snake_body)) #danger down
    #Body danger

    bin_chain = ''.join(str(bit) for bit in tuple(s))
    return int(bin_chain, 2)

def get_death_state():
    s = []
    for i in range(12):
        s.append(1)
    bin_chain = ''.join(str(bit) for bit in tuple(s))
    return int(bin_chain, 2)

# Game Over
def game_over():
    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (frame_size_x/2, frame_size_y/4)
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(0, red, 'times', 20)
    pygame.display.flip()
    time.sleep(3)
    pygame.quit()
    sys.exit()

def reset():
    global snake_pos, snake_body, food_pos, food_spawn, direction, change_to, score
    snake_pos = [100, 50]
    snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]
    food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
    food_spawn = True
    direction = 'RIGHT'
    change_to = direction
    score = 0

# Score
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frame_size_x/10, 15)
    else:
        score_rect.midtop = (frame_size_x/2, frame_size_y/1.25)
    game_window.blit(score_surface, score_rect)
    # pygame.display.flip()

def save_q_table_file(q_table):
    np.savetxt('q_table.txt', q_table, delimiter=",")

def load_q_table_file():
    return np.loadtxt('q_table.txt', delimiter=',')

it = 0

# Loading Q-table
Q = load_q_table_file()

# Main logic
while True:
    it+=1
    last_distance_to_food = (snake_pos[0] - food_pos[0])**2 + (snake_pos[1] - food_pos[1])**2 

    #Get current state
    state = get_state(direction, snake_pos, snake_body, food_pos)

    rand = random.uniform(0, 1)
    epsilon = 0
    if rand < epsilon:
        action = random.randint(0, 3)
    else:
        action = np.argmax(Q[state, :])

    if action == 0:
        change_to = 'UP'
    if action == 1:
        change_to = 'DOWN'
    if action == 2:
        change_to = 'LEFT'
    if action == 3:
        change_to = 'RIGHT'


    reward = 0
    #Penalize if snake is moving in the opposite direction
    if change_to == 'UP' and direction == 'DOWN':
        reward -= 10
    if change_to == 'DOWN' and direction == 'UP':
        reward -= 10
    if change_to == 'LEFT' and direction == 'RIGHT':
        reward -= 10
    if change_to == 'RIGHT' and direction == 'LEFT':
        reward -= 10

    # Making sure the snake cannot move in the opposite direction instantaneously
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

    # Moving the snake
    if direction == 'UP':
        snake_pos[1] -= 10
    if direction == 'DOWN':
        snake_pos[1] += 10
    if direction == 'LEFT':
        snake_pos[0] -= 10
    if direction == 'RIGHT':
        snake_pos[0] += 10
    # Snake body growing mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        food_spawn = False
        reward += 10000
    else:
        snake_body.pop()
    # Spawning food on the screen
    if not food_spawn:
        food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
    food_spawn = True

    # GFX
    game_window.fill(black)
    for pos in snake_body:
        # Snake body
        # .draw.rect(play_surface, color, xy-coordinate)
        # xy-coordinate -> .Rect(x, y, size_x, size_y)
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))

    new_state = get_state(direction, snake_pos, snake_body, food_pos)

    # Distance to the food
    distance_to_food = (snake_pos[0] - food_pos[0])**2 + (snake_pos[1] - food_pos[1])**2 #Euclidean distance
    # Reward for getting closer to the food
    if distance_to_food < last_distance_to_food:
        reward += 10

    # Snake food
    pygame.draw.rect(game_window, white, pygame.Rect(food_pos[0], food_pos[1], 10, 10))
    # Game Over conditions
    # Getting out of bounds
    if snake_pos[0] < 0 or snake_pos[0] > frame_size_x-10:
        reset()
        reward = -10000
        new_state = get_death_state()
    if snake_pos[1] < 0 or snake_pos[1] > frame_size_y-10:
        reset()
        reward = -10000
        new_state = get_death_state()
    # Touching the snake body
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            reset()
            reward = -10000
            new_state = get_death_state()

    # Update Q-Table
    upateQ(state, action, reward, new_state)

    show_score(1, white, 'consolas', 20)
    # Refresh game screen
    pygame.display.update()
    # Refresh rate
    fps_controller.tick(difficulty)