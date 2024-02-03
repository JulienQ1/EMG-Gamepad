import threading
import time
import pygame
from pylsl import StreamInlet, resolve_stream
import random

# Initialize global variables
user_input = 0
running = True

ST_MAX = 0.5
ST_MIN = 0.05

ST_OLD_MIN = 0
ST_OLD_MAX = 0

def fetch_data():
    global user_input  # Use global variable to communicate with the main thread
    while running:
        sample, timestamp = inlet.pull_sample(timeout=0.01)
        if sample is None:
            continue
        
        # Get the integer value from user input
        try:
            EMB_Value = round((abs(sample[1])-ST_MIN)/(ST_MAX-ST_MIN)*100)
            user_input = EMB_Value
            if user_input < 0: user_input = 0
            if user_input > 100: user_input = 100
        
        except ValueError:
            user_input = 0

# Initialize LSL stream
streams = resolve_stream()
inlet = StreamInlet(streams[0])
'''
q = input("Provide a minimum strength:")

i = 3
j = 0
while True:
    while True:
        sample, timestamp = inlet.pull_sample()
        if abs(sample[1]) >= ST_OLD_MIN:
            ST_OLD_MIN = abs(sample[1])
        time.sleep(0.001)
        if j >= 1000:
            break
        else:
            j += 1
    if i <= 0:
        ST_MIN = ST_OLD_MIN
        print("Minimum value: ",ST_MIN)
        break
    else:
        print(i)
        i -= 1

q = input("Provide a maximum strength:")
i = 3
j = 0
while True:
    while True:
        sample, timestamp = inlet.pull_sample()
        if abs(sample[1]) >= ST_OLD_MAX:
            ST_OLD_MAX = abs(sample[1])
        time.sleep(0.001)
        if j >= 1000:
            break
        else:
            j += 1
    if i <= 0:
        ST_MAX = ST_OLD_MAX
        print("Maximum value: ",ST_MAX)
        break
    else:
        print(i)
        i -= 1
'''

# Initialize pygame
pygame.init()

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Screen dimensions
WIDTH = 480
HEIGHT = 640

# Bird attributes
bird_y = HEIGHT // 2
bird_velocity = 0

# Pipe attributes
pipe_gap = 300
pipe_width = 75
pipe_velocity = 2
upper_pipe_height = random.randint(50, HEIGHT - pipe_gap - 50)
lower_pipe_height = HEIGHT - upper_pipe_height - pipe_gap
pipe_x = WIDTH

# Set up screen and clock
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird')
clock = pygame.time.Clock()

# Start auxiliary thread
data_thread = threading.Thread(target=fetch_data)
data_thread.start()

while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Decide bird's velocity based on user_input
    if user_input > 5:
        bird_velocity = -user_input / 10

    # Update bird's position
    bird_velocity += 1
    bird_y += bird_velocity
    if bird_y + 20 > HEIGHT:
        bird_y = HEIGHT - 20
        bird_velocity = 0
    
    # Draw bird
    pygame.draw.circle(screen, RED, (WIDTH // 4, bird_y), 20)

    # Update pipe position
    pipe_x -= pipe_velocity

    # Draw pipes
    pygame.draw.rect(screen, GREEN, (pipe_x, 0, pipe_width, upper_pipe_height))
    pygame.draw.rect(screen, GREEN, (pipe_x, upper_pipe_height + pipe_gap, pipe_width, lower_pipe_height))

    # Regenerate pipes if they move off the left side of the screen
    if pipe_x + pipe_width < 0:
        pipe_x = WIDTH
        upper_pipe_height = random.randint(50, HEIGHT - pipe_gap - 50)
        lower_pipe_height = HEIGHT - upper_pipe_height - pipe_gap
    
    # Update the screen
    pygame.display.flip()
    clock.tick(60)

# Terminate the auxiliary thread
running = False
data_thread.join()  

pygame.quit()
