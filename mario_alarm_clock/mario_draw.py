"""Mario-themed drawing functions for tkinter Canvas."""

import math

# Mario sprite pixel grid (16 tall x 14 wide)
# R=red, S=skin, B=brown, U=blue, W=white, .=transparent
MARIO_PIXELS = [
    ".....RRR......",   # 0  cap top
    "....RRRRR.....",   # 1  cap
    "....BSBSB.....",   # 2  cap brim + hair
    "...BSSSSSB....",   # 3  face
    "...BSWWWSB....",   # 4  face with eyes
    "....BSSSB.....",   # 5  lower face
    "....BBBB......",   # 6  mustache/neck
    "....RRRR......",   # 7  shirt collar
    "...RRRRRR.....",   # 8  shirt
    "..RRRRRRRR....",   # 9  shirt
    "..RRRRRRRRR...",   # 10 shirt + arms
    "..RUUUUUUR....",   # 11 overalls top — fixed to 14 wide
    "..UUUUUUUU....",   # 12 overalls — fixed to 14 wide
    "...UU..UU.....",   # 13 overalls legs
    "...BB..BB.....",   # 14 shoes
    "...BB..BB.....",   # 15 shoes bottom
]

COLOR_MAP = {
    'R': '#E52521',
    'S': '#FDBC7A',
    'B': '#6B3A00',
    'U': '#0048C0',
    'W': '#FFFFFF',
    'Y': '#FFD700',
    '.': None,
}

# Color palette
PIPE_GREEN = '#00A800'
PIPE_DARK_GREEN = '#007800'
BRICK_ORANGE = '#C84C09'
QUESTION_YELLOW = '#F8A800'
SKY_BLUE = '#5C94FC'
GROUND_BROWN = '#A05020'
GROUND_GREEN = '#38B838'
CLOUD_WHITE = '#F0F8FF'
HILL_GREEN = '#38A838'
HILL_DARK_GREEN = '#2D8C2D'
FLAG_POLE_GRAY = '#888888'
FLAG_GREEN = '#00C800'
BUSH_GREEN = '#30A830'
BUSH_OUTLINE = '#208020'


def lighten_color(hex_color, amount=0.3):
    """Lighten a hex color by the given amount (0..1)."""
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = min(255, int(r + (255 - r) * amount))
    g = min(255, int(g + (255 - g) * amount))
    b = min(255, int(b + (255 - b) * amount))
    return f'#{r:02x}{g:02x}{b:02x}'


def draw_pixel_art(canvas, pixels, start_x, start_y, pixel_size=6, color_map=None):
    """Draw pixel art from a grid of characters onto a canvas."""
    if color_map is None:
        color_map = COLOR_MAP
    rects = []
    for row_idx, row in enumerate(pixels):
        for col_idx, char in enumerate(row):
            color = color_map.get(char)
            if color is None:
                continue
            x1 = start_x + col_idx * pixel_size
            y1 = start_y + row_idx * pixel_size
            x2 = x1 + pixel_size
            y2 = y1 + pixel_size
            r = canvas.create_rectangle(x1, y1, x2, y2, fill=color,
                                        outline=color, width=0)
            rects.append(r)
    return rects


def draw_mario(canvas, x, y, pixel_size=6):
    """Draw Mario at the given position."""
    return draw_pixel_art(canvas, MARIO_PIXELS, x, y, pixel_size)


def draw_sky(canvas, width, height):
    """Draw gradient sky blue background."""
    steps = 20
    step_h = height // steps
    for i in range(steps):
        ratio = i / steps
        r = int(0x5C + (0x9C - 0x5C) * ratio)
        g = int(0x94 + (0xD4 - 0x94) * ratio)
        b = int(0xFC + (0xFF - 0xFC) * ratio)
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_rectangle(0, i * step_h, width, (i + 1) * step_h + 1,
                                fill=color, outline='')


def draw_cloud(canvas, x, y, scale=1.0):
    """Draw a rounded Mario-style cloud."""
    r = int(20 * scale)
    offsets = [(0, 8), (15, 0), (35, 4), (50, 8)]
    for ox, oy in offsets:
        canvas.create_oval(x + ox, y + oy, x + ox + r * 2, y + oy + r * 2,
                           fill=CLOUD_WHITE, outline='', width=0)


def draw_hill(canvas, x, bottom_y, width=120, height=50):
    """Draw a green hill in the background."""
    canvas.create_arc(x, bottom_y - height, x + width, bottom_y + height,
                      start=0, extent=180, fill=HILL_GREEN,
                      outline=HILL_DARK_GREEN, width=2)
    canvas.create_arc(x + 10, bottom_y - height + 10, x + width // 2 - 5,
                      bottom_y + height - 20,
                      start=0, extent=180, fill='', outline='#4CC84C', width=1)


def draw_ground(canvas, width, ground_y, block_size=40):
    """Draw the ground strip with alternating colored blocks."""
    blocks = []
    for col in range(0, width + block_size, block_size):
        i = col // block_size
        fill = GROUND_GREEN if i % 2 == 0 else '#30A830'
        b = canvas.create_rectangle(col, ground_y, col + block_size,
                                    ground_y + block_size,
                                    fill=fill, outline='#206020', width=1)
        blocks.append(b)
        fill = GROUND_BROWN if i % 2 == 1 else '#904018'
        b = canvas.create_rectangle(col, ground_y + block_size, col + block_size,
                                    ground_y + block_size * 2,
                                    fill=fill, outline='#603010', width=1)
        blocks.append(b)
    return blocks


def draw_pipe(canvas, x, pipe_top_y, pipe_bottom_y):
    """Draw a green Mario pipe with 3D shading."""
    pipe_width = 60
    canvas.create_rectangle(x + 5, pipe_top_y + 15, x + pipe_width + 5,
                            pipe_bottom_y + 3, fill='#005000', outline='', width=0)
    canvas.create_rectangle(x, pipe_top_y + 15, x + pipe_width, pipe_bottom_y,
                            fill=PIPE_GREEN, outline='#006000', width=2)
    canvas.create_rectangle(x - 8, pipe_top_y, x + pipe_width + 8, pipe_top_y + 20,
                            fill=PIPE_DARK_GREEN, outline='#004000', width=2)
    canvas.create_rectangle(x + 5, pipe_top_y + 25, x + 15, pipe_bottom_y - 5,
                            fill='#30D830', outline='', width=0)


def draw_question_block(canvas, x, y, block_size=36):
    """Draw a yellow ? block. Returns list of canvas item IDs."""
    items = []
    canvas.create_rectangle(x + 2, y + 2, x + block_size + 2, y + block_size + 2,
                            fill='#A06000', outline='', width=0)
    r = canvas.create_rectangle(x, y, x + block_size, y + block_size,
                                fill=QUESTION_YELLOW, outline='#C88000', width=3)
    items.append(r)
    r = canvas.create_rectangle(x + 3, y + 3, x + block_size - 3, y + block_size - 3,
                                fill='', outline='#FFC800', width=1)
    items.append(r)
    font_size = int(block_size * 0.7)
    t = canvas.create_text(x + block_size // 2, y + block_size // 2,
                           text='?', font=('Arial', font_size, 'bold'),
                           fill='#C88000')
    items.append(t)
    return items


def draw_brick_block(canvas, x, y, block_size=36):
    """Draw a detailed brick-pattern block."""
    canvas.create_rectangle(x, y, x + block_size, y + block_size,
                            fill=BRICK_ORANGE, outline='#803000', width=2)
    h = block_size // 2
    q = block_size // 4
    canvas.create_line(x, y + h, x + block_size, y + h, fill='#803000', width=1)
    canvas.create_line(x + h, y, x + h, y + h, fill='#803000', width=1)
    canvas.create_line(x + q, y + h, x + q, y + block_size, fill='#803000', width=1)
    canvas.create_line(x + h + q, y + h, x + h + q, y + block_size, fill='#803000', width=1)
    canvas.create_line(x + 2, y + 2, x + block_size - 2, y + 2, fill='#E06020', width=1)


def draw_flag(canvas, x, bottom_y, pole_height=120):
    """Draw a goal flag pole."""
    pole_top = bottom_y - pole_height
    canvas.create_rectangle(x - 2, pole_top, x + 2, bottom_y,
                            fill=FLAG_POLE_GRAY, outline='#666666', width=1)
    canvas.create_oval(x - 6, pole_top - 12, x + 6, pole_top,
                       fill='#44DD44', outline='#228822', width=1)
    flag_w, flag_h = 30, 20
    canvas.create_polygon(x + 2, pole_top + 5,
                          x + 2 + flag_w, pole_top + 5 + flag_h // 2,
                          x + 2, pole_top + 5 + flag_h,
                          fill=FLAG_GREEN, outline='#008800', width=1)


def draw_coin(canvas, x, y, size=16):
    """Draw a spinning coin (ellipse)."""
    canvas.create_oval(x, y, x + size, y + size // 2,
                       fill='#FFD700', outline='#C88000', width=1)
    canvas.create_oval(x + 3, y + 1, x + size - 3, y + size // 2 - 1,
                       fill='', outline='#FFE860', width=1)


def draw_star(canvas, x, y, size=20):
    """Draw a Mario star shape."""
    points = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = size if i % 2 == 0 else size * 0.4
        points.extend([x + r * math.cos(angle), y + r * math.sin(angle)])
    canvas.create_polygon(points, fill='#FFD700', outline='#C88000', width=1)


def draw_bush(canvas, x, bottom_y):
    """Draw a simple green bush using overlapping ovals."""
    for dx, dy, r in [(0, 0, 16), (20, -6, 13), (-15, -4, 12)]:
        canvas.create_oval(x + dx, bottom_y + dy,
                           x + dx + r * 2, bottom_y + dy + r * 2,
                           fill=BUSH_GREEN, outline=BUSH_OUTLINE, width=1)
