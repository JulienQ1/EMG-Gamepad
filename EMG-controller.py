import pygame
import pyautogui
from pylsl import StreamInlet, resolve_stream
import threading
import time
# Initialize Pygame
pygame.init()

# Set up the window with double buffering
width, height = 200, 400
win = pygame.display.set_mode((width, height), pygame.DOUBLEBUF)
pygame.display.set_caption("Delimiter Control with EMG")

# Constants
BAR_WIDTH = 50
BAR_HEIGHT = 300
BAR_X = (width - BAR_WIDTH) // 2
BAR_Y = height - BAR_HEIGHT - 10
ST_MIN = 0.010
ST_MAX = 0.2
FPS = 30  # Desired Frames Per Second

# Normalize and map EMG value to 0-100 for display
def normalize_emg(value):
    return round((value - ST_MIN) / (ST_MAX - ST_MIN) * 100)

# Calculate levels based on percentage increases from ST_MIN
LEVELS = {
    ST_MIN + (ST_MAX - ST_MIN) * 0.25: 'Z',
    ST_MIN + (ST_MAX - ST_MIN) * 0.50: 'Z',
    ST_MIN + (ST_MAX - ST_MIN) * 0.75: 'X',
    ST_MAX: 'X'
}

# EMG Data Handling
EMG_Value = ST_MIN  # Initial EMG value
data_lock = threading.Lock()

def fetch_data():
    global EMG_Value
    streams = resolve_stream()
    inlet = StreamInlet(streams[0])
    while running:
        sample, timestamp = inlet.pull_sample(timeout=0.01)
        if sample is not None:
            with data_lock:
                EMG_Value = abs(sample[1])

# Key Press Handling
pressed_key = None

def handle_key_presses():
    global pressed_key
    last_pressed_level = None  # Keep track of the last pressed level

    while running:
        with data_lock:
            current_EMG_Value = EMG_Value

        # Determine the current level based on EMG value
        current_level = None
        for level, key in sorted(LEVELS.items()):
            if current_EMG_Value >= level:
                current_level = level

        # Check for automatic key presses based on EMG value
        if current_level is not None and last_pressed_level != current_level:
            pyautogui.press(LEVELS[current_level])
            last_pressed_level = current_level
        elif current_level is None:
            last_pressed_level = None

        # Reduce CPU usage
        time.sleep(1/60)


# Start the EMG data fetching and key press threads
running = True
data_thread = threading.Thread(target=fetch_data)
data_thread.start()

key_thread = threading.Thread(target=handle_key_presses)
key_thread.start()

# Clock for FPS control
clock = pygame.time.Clock()

# Main loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Get the latest EMG value
    with data_lock:
        current_EMG_Value = EMG_Value
    bar_level = normalize_emg(current_EMG_Value)

    # Clear the screen before drawing
    win.fill((255, 255, 255))

    # Drawing
    pygame.draw.rect(win, (0, 0, 255), (BAR_X, BAR_Y + BAR_HEIGHT - bar_level * 3, BAR_WIDTH, bar_level * 3))
    for level in LEVELS:
        normalized_level = normalize_emg(level)
        pygame.draw.line(win, (255, 0, 0), (BAR_X, BAR_Y + BAR_HEIGHT - normalized_level * 3), (BAR_X + BAR_WIDTH, BAR_Y + BAR_HEIGHT - normalized_level * 3))

    # Update the display with double buffering
    pygame.display.flip()

    # Control the frame rate
    clock.tick(FPS)

# Cleanup
running = False
data_thread.join()
key_thread.join()
pygame.quit()
