import os
import pygame
import math
import threading
from dotenv import load_dotenv
import google.generativeai as genai
import pyttsx3

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Init Pygame
pygame.init()
pygame.font.init()

# Initialize TTS engine
engine = pyttsx3.init()

# Window settings
WIDTH, HEIGHT = 720, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎵 Educational Song Generator")

# Colors
WHITE = (250, 250, 250)
LIGHT = (240, 240, 240)
DARK = (40, 40, 40)
GRAY = (200, 200, 200)
BLUE = (100, 149, 237)
SOFT_SHADOW = (230, 230, 230)

# Fonts
def get_font(size):
    return pygame.font.SysFont("Segoe UI Emoji", size)

TITLE_FONT = get_font(34)
LABEL_FONT = get_font(20)
INPUT_FONT = get_font(22)
OUTPUT_FONT = get_font(18)

# Input box setup
input_rect = pygame.Rect(60, 125, 600, 45)
input_color = GRAY
active = False
text = ''
verse_lines = []
loading = False
angle = 0

# Output area
output_x = 60
output_y = 190
output_width = 600
output_height = 280
scroll_offset = 0
content_height = 0

# Scrollbar
scrollbar_rect = pygame.Rect(output_x + output_width - 10, output_y, 6, output_height)
scrollbar_color = GRAY
scrollbar_dragging = False
scrollbar_handle_rect = pygame.Rect(0, 0, 6, 50)

# Cursor blinking
cursor_timer = 0
show_cursor = True

# Spinner
def draw_spinner(center_x, center_y, radius, angle):
    length = 8
    for i in range(length):
        fade = 255 - int((255 / length) * i)
        fade_color = (BLUE[0], BLUE[1], BLUE[2], fade)
        radians = angle + (2 * math.pi / length) * i
        x = center_x + radius * math.cos(radians)
        y = center_y + radius * math.sin(radians)
        pygame.draw.circle(screen, fade_color[:3], (int(x), int(y)), 6)

# Function to generate speech from text
def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# Model generator functions
def generate_edu_song(topic):
    global verse_lines, loading
    loading = True
    prompt = f"""
    Create a fun, catchy educational poem long 10 lines about the topic: "{topic}".
    - Begin with a song title.
    - Make it engaging and easy to remember.
    - Use simple language suitable for learners.
    - Ensure it teaches the topic effectively through the lyrics.
    - Keep it playful, musical, and informative.
    Output only the 10 lines of the poem but do not number them.
    """
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(prompt)
    verse_lines = response.text.strip().splitlines()
    loading = False
    speak_text("\n".join(verse_lines))

def generate_genz_shii_song(topic):
    global verse_lines, loading
    loading = True
    prompt = f"""
    Create a Gen Z "Type Shii" educational explanation about the topic: "{topic}".
    - Use exaggerated Gen Z slang and humor.
    - Keep it energetic, fun, and full of energy.
    - Make it relatable, using meme references and "type shii" culture.
    - Ensure it teaches the topic effectively but in a super cool way.

    Make sure you only output the explanation text, don't say anything else. No emojis. 120 words max.
    """
    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(prompt)
    verse_lines = response.text.strip().splitlines()
    loading = False
    speak_text("\n".join(verse_lines))

# Function to wrap text
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''

    for word in words:
        # Check the width of the current line plus the new word
        test_line = current_line + ' ' + word if current_line else word
        test_width = font.render(test_line, True, DARK).get_width()
        
        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word  # Start a new line with the current word
    
    # Add the last line
    if current_line:
        lines.append(current_line)
    
    return lines

# Main loop
clock = pygame.time.Clock()
running = True

# Dropdown menu state
model_selected = "EduPoem"
dropdown_open = False

# Button sizes and center calculation
button_width = 200
button_height = 40

# Centering buttons side by side
total_width = button_width * 2 + 20  # 20px space between buttons
edu_poem_x = (WIDTH // 2) - (total_width // 2)
gen_z_shii_x = edu_poem_x + button_width + 10  # 10px space between buttons

# Button rectangles
buttons = {
    "edu_poem": pygame.Rect(edu_poem_x, 70, button_width, button_height),
    "gen_z_shii": pygame.Rect(gen_z_shii_x, 70, button_width, button_height)
}

def render_button(text, rect, color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, rect, border_radius=10)
    else:
        pygame.draw.rect(screen, color, rect, border_radius=10)
    
    # If the button is selected, change the color to a darker shade
    if (rect == buttons["edu_poem"] and model_selected == "EduPoem") or (rect == buttons["gen_z_shii"] and model_selected == "GenZ Type Shii"):
        pygame.draw.rect(screen, DARK, rect, border_radius=10)
    
    text_surface = LABEL_FONT.render(text, True, WHITE)
    screen.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2, rect.y + (rect.height - text_surface.get_height()) // 2))

# Main loop
while running:
    screen.fill(LIGHT)  # Fill screen with light color to avoid black background

    angle += 0.1  # Spinner angle update

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if buttons["edu_poem"].collidepoint(event.pos):
                model_selected = "EduPoem"
            elif buttons["gen_z_shii"].collidepoint(event.pos):
                model_selected = "GenZ Type Shii"

            if input_rect.collidepoint(event.pos):
                active = True
            else:
                active = False
            input_color = BLUE if active else GRAY

        elif event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN and not loading and text.strip():
                    verse_lines = []
                    scroll_offset = 0
                    if model_selected == "EduPoem":
                        threading.Thread(target=generate_edu_song, args=(text,), daemon=True).start()
                    elif model_selected == "GenZ Type Shii":
                        threading.Thread(target=generate_genz_shii_song, args=(text,), daemon=True).start()
                    text = ''
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif event.key == pygame.K_UP:
                    scroll_offset = min(scroll_offset + 30, 0)
                elif event.key == pygame.K_DOWN:
                    scroll_offset -= 30
                    scroll_offset = max(min(scroll_offset, 0), content_height - output_height)
                else:
                    text += event.unicode

        elif event.type == pygame.MOUSEWHEEL:
            scroll_offset += event.y * 30
            scroll_offset = max(min(scroll_offset, 0), content_height - output_height)

    # Blinking cursor logic
    cursor_timer += clock.get_time()
    if cursor_timer >= 500:
        cursor_timer = 0
        show_cursor = not show_cursor

    # Dropdown menu as title
    model_selected_surface = TITLE_FONT.render(f"🎓 {model_selected} Generator", True, DARK)
    screen.blit(model_selected_surface, (WIDTH // 2 - model_selected_surface.get_width() // 2, 20))

    # Input label
    input_label = LABEL_FONT.render("Enter a topic (e.g. Gravity, Photosynthesis):", True, DARK)
    screen.blit(input_label, (input_rect.x, input_rect.y))

    # Input box
    input_rect.y += 23
    pygame.draw.rect(screen, input_color, input_rect, border_radius=10)
    input_surface = INPUT_FONT.render(text, True, DARK)
    screen.blit(input_surface, (input_rect.x + 10, input_rect.y + 10))
    input_rect.y -= 23

    if active and show_cursor:
        cursor_x = input_rect.x + 10 + input_surface.get_width() + 2
        cursor_y = input_rect.y + 33
        cursor_height = input_surface.get_height()
        pygame.draw.line(screen, DARK, (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_height), 2)

    # Render buttons next to each other
    render_button("EduPoem", buttons["edu_poem"], BLUE, DARK)
    render_button("GenZ Type Shii", buttons["gen_z_shii"], BLUE, DARK)

    # Output background
    # Output background with rounded corners
    pygame.draw.rect(screen, WHITE, (output_x, output_y + 15, output_width, output_height + 15), border_radius=15)

    # Spinner or song text
    if loading:
        draw_spinner(WIDTH // 2, HEIGHT // 2, 30, angle)
    else:
        y_start = output_y + scroll_offset + 23
        content_height = 0
        rendered_lines = []

        for line in verse_lines:
            if line.strip():
                # Wrap the line to fit the output area width
                wrapped_lines = wrap_text(line.strip(), OUTPUT_FONT, output_width - 20)  # 20px padding
                for wrapped_line in wrapped_lines:
                    rendered_line = OUTPUT_FONT.render(wrapped_line, True, DARK)
                    rendered_lines.append((rendered_line, y_start + content_height))
                    content_height += 26  # Adjust line height

        # Draw the wrapped lines
        for rendered_line, y_position in rendered_lines:
            screen.blit(rendered_line, (output_x + 10, y_position))

    pygame.display.update()  # Update the screen
    clock.tick(60)  # FPS control
