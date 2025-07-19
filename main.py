import tkinter as tk
import numpy as np
import sounddevice as sd
import random
import time
import math
from noise import pnoise2
notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

note_freqs = {
    'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13, 'E': 329.63,
    'F': 349.23, 'F#': 369.99, 'G': 392.00, 'G#': 415.30, 'A': 440.00,
    'A#': 466.16, 'B': 493.88
}
patterns = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
rows = 7
cols = 8
circle_radius = 25
x_spacing = 90
y_spacing = 90

NORMAL_COLOR = 'lightyellow'

root = tk.Tk()
root.title("Tonnetz Pattern Generator")
root.configure(bg=NORMAL_COLOR)

canvas_width = cols * x_spacing + 100
canvas_height = rows * y_spacing + 100
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg=NORMAL_COLOR)
canvas.pack()
rows2, cols2 = 6, 7
steps = 10

# -------------------
# Eulerian Random Path
# -------------------
def eulerian_random_path(rows2, cols2, steps=20):
    start = (random.randint(0, rows2-1), random.randint(0, cols2-1))

    # Pick a faraway point
    while True:
        target = (random.randint(0, rows-1), random.randint(0, cols2-1))
        dist = abs(target[0] - start[0]) + abs(target[1] - start[1])
        if dist >= (rows2 + cols2) // 2:
            break
    
    path = [start]
    current = start

    for _ in range(steps-1):
        possible_moves = []
        for dy, dx in [(-1,0), (1,0), (0,-1), (0,1)]:
            ny, nx = current[0]+dy, current[1]+dx
            if 0 <= ny < rows2 and 0 <= nx < cols2 and (ny, nx) not in path:
                possible_moves.append((ny, nx))
        
        if not possible_moves:
            break

        # Choose move that gets closer to target
        possible_moves.sort(key=lambda p: abs(p[0]-target[0]) + abs(p[1]-target[1]))
        current = possible_moves[0]
        path.append(current)

    return path

# -------------------
# Perlin Noise Pattern
# -------------------
def perlin_noise_pattern(rows2, cols2, steps=20, scale=0.1):
    noise_map = []
    for row2 in range(rows):
        for col2 in range(cols):
            n = pnoise2(row2 * scale, col2 * scale)
            noise_map.append(((row2, col2), n))
    
    noise_map.sort(key=lambda x: x[1])
    path = [pos for pos, _ in noise_map[:steps]]
    return path

# -------------------
# Lissajous Random Pattern
# -------------------
def lissajous_random_pattern(rows2, cols2, steps=20):
    path = []
    A = (cols2-1) / 2
    B = (rows2-1) / 2
    cx = (cols2-1) / 2
    cy = (rows2-1) / 2

    a = random.randint(1, 5)
    b = random.randint(1, 5)
    delta = random.uniform(0, math.pi)

    i = 0
    while len(path) < steps and i < steps * 10:
        t = (i / steps) * 2 * math.pi
        x = int(round(cx + A * math.sin(a * t + delta)))
        y = int(round(cy + B * math.sin(b * t)))

        pos = (y, x)
        if pos not in path and 0 <= y < rows2 and 0 <= x < cols2:
            path.append(pos)

        i += 1

    return path

def play_note(note, duration=0.25, sample_rate=44100):
    freq = note_freqs[note]
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(2 * np.pi * freq * t)
    tone += 0.3 * np.sin(2 * np.pi * freq * 2 * t)
    attack_time = 0.02
    decay_time = 0.1
    envelope = np.ones_like(t)
    attack_samples = int(sample_rate * attack_time)
    decay_samples = int(sample_rate * decay_time)
    envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    envelope[-decay_samples:] = np.linspace(1, 0, decay_samples)
    tone = tone * envelope
    tone *= 0.3
    sd.play(tone, samplerate=sample_rate)
    sd.wait()

positions = []
circles = {}
last_pressed = []

def aesthetic_random_color():
    r = random.randint(180, 255)
    g = random.randint(140, 230)
    b = random.randint(180, 255)
    return f'#{r:02x}{g:02x}{b:02x}'

for row in range(rows):
    row_positions = []
    for col in range(cols):
        x_offset = (x_spacing / 2) if row % 2 else 0
        x = col * x_spacing + x_offset + 50
        y = row * y_spacing + 50
        note_index = (row * 4 + col * 7) % 12
        note = notes[note_index]
        row_positions.append((x, y, note))
    positions.append(row_positions)

for row in range(rows):
    for col in range(cols):
        x1, y1, _ = positions[row][col]
        neighbors = []
        if col + 1 < len(positions[row]):
            neighbors.append(positions[row][col + 1])
        if row + 1 < rows:
            if row % 2 == 0:
                if col < len(positions[row + 1]):
                    neighbors.append(positions[row + 1][col])
            else:
                if col + 1 < len(positions[row + 1]):
                    neighbors.append(positions[row + 1][col + 1])
        if row + 1 < rows:
            if row % 2 == 0:
                if col - 1 >= 0:
                    neighbors.append(positions[row + 1][col - 1])
            else:
                if col < len(positions[row + 1]):
                    neighbors.append(positions[row + 1][col])
        for x2, y2, _ in neighbors:
            canvas.create_line(x1, y1, x2, y2, fill='black', width=2)

is_dragging = False

def play_note_and_color(circle_id, note):
    color = aesthetic_random_color()
    canvas.itemconfig(circle_id, fill=color)
    canvas.update_idletasks()
    play_note(note)
    last_pressed.append(circle_id)
    if len(last_pressed) > 3:
        to_reset = last_pressed.pop(0)
        canvas.itemconfig(to_reset, fill=NORMAL_COLOR)

def check_collision(event):
    for cid, (x, y, note) in circles.items():
        dist = ((event.x - x) ** 2 + (event.y - y) ** 2) ** 0.5
        if dist <= circle_radius:
            play_note_and_color(cid, note)
            break
def fibonacci_pattern(rows2, cols2, steps=20):
    fib_seq = [0, 1]
    while len(fib_seq) < (steps * 2):  
# enough values for positions
        fib_seq.append(fib_seq[-1] + fib_seq[-2])

    path = []
    i = 0
    while len(path) < steps and i < len(fib_seq) - 1:
        row = fib_seq[i] % rows2
        col = fib_seq[i + 1] % cols2
        pos = (row, col)
        if pos not in path:
            path.append(pos)
        i += 1

    return path

def on_mouse_down(event):
    global is_dragging
    is_dragging = True
    check_collision(event)

def on_mouse_up(event):
    global is_dragging
    is_dragging = False

def on_mouse_move(event):
    if is_dragging:
        check_collision(event)

for row in range(rows):
    for col in range(cols):
        x, y, note = positions[row][col]
        circle = canvas.create_oval(
            x - circle_radius, y - circle_radius,
            x + circle_radius, y + circle_radius,
            fill=NORMAL_COLOR, outline='black', width=2
        )
        label = canvas.create_text(x, y, text=note, font=('Arial', 12, 'bold'))
        circles[circle] = (x, y, note)

canvas.bind('<ButtonPress-1>', on_mouse_down)
canvas.bind('<ButtonRelease-1>', on_mouse_up)
canvas.bind('<B1-Motion>', on_mouse_move)
eul = eulerian_random_path(rows, cols, steps)
perl = perlin_noise_pattern(rows, cols, steps)
lisalisa = lissajous_random_pattern(rows, cols, steps)
# 📦 List of unique 10-note patterns
#for i in range (20):
patterns = [
    eulerian_random_path(rows, cols, steps),
    fibonacci_pattern(rows, cols, steps),
    [(0,1),(0,2),(1,2),(2,2),(2,1),(1,0),(0,1),(0,2),(1,2),(2,2),(2,1),(1,0),(0,1),(0,2),(1,2),(2,2),(2,1),(1,0)],
    [
    (0,0),
    (1,0),
    (0,1),
    (1,1),
    (0,2),
    (1,2),
    (0,3),
    (1,3),
    (0,4),
    (1,4),
    (0,5),
    (1,5),
    (0,6),
    (1,6),
    (0,7),
    (1,7)

   ],
   [
    
    (0,0),
    (1,0),
    (0,1),
    (1,1),
    (0,2),
    (1,2),
    (2,0),
    (3,0),
    (2,1),
    (3,1),
    (2,2),
    (3,2),
    (4,0),
    (5,0),
    (4,1),
    (5,1),
    (4,2),
    (5,2),
   ],
   [
    
    (0,3),
    (1,3),
    (0,4),
    (1,4),
    (0,5),
    (1,5),
    (2,3),
    (3,3),
    (2,4),
    (3,4),
    (2,5),
    (3,5),
    (4,3),
    (5,3),
    (4,4),
    (5,4),
    (4,5),
    (5,5),
   ] ,




    perlin_noise_pattern(rows, cols, steps),
    lissajous_random_pattern(rows, cols, steps)
]
# ⬇️ Pattern generator
def generate_pattern():
    pattern_coords = random.choice(patterns)
    for row, col in pattern_coords:
        if row < rows and col < cols:
            x, y, note = positions[row][col]
            for cid, (cx, cy, n) in circles.items():
                if abs(cx - x) < 2 and abs(cy - y) < 2:
                    play_note_and_color(cid, note)
                    time.sleep(0.2)
                    root.update()

# Add button to window
button = tk.Button(root, text="Generate Pattern", font=('Arial', 14), command=generate_pattern)
button.pack(pady=10)

root.mainloop()
