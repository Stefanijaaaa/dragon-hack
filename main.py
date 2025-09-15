import os
import pygame
import math
import threading
import queue
import uuid
from dotenv import load_dotenv
import google.generativeai as genai
from gtts import gTTS
import pygame.mixer

pygame.mixer.init()

speech_queue = queue.Queue()

icon = pygame.image.load('cup.png')  
pygame.display.set_icon(icon)

def speech_player():
    while True:
        text = speech_queue.get()
        try:
            unique_id = str(uuid.uuid4())
            filename = f"speech_{unique_id}.mp3"
            tts = gTTS(text)
            tts.save(filename)

            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)

            pygame.mixer.music.stop()
            os.remove(filename)

        except Exception as e:
            print(f"Speech error: {e}")

threading.Thread(target=speech_player, daemon=True).start()

def speak_text(text):
    speech_queue.put(text)

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

pygame.init()
pygame.font.init()


WIDTH, HEIGHT = 720, 540
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Don't Cry Over Spilt Coffee!")

WHITE = (250, 250, 250)
LIGHT = (240, 240, 240)
DARK = (40, 40, 40)
GRAY = (200, 200, 200)
BLUE = (100, 149, 237)


def get_font(size):
    return pygame.font.SysFont("Segoe UI Emoji", size)

TITLE_FONT = get_font(34)
LABEL_FONT = get_font(20)
INPUT_FONT = get_font(22)
OUTPUT_FONT = get_font(18)

input_rect = pygame.Rect(60, 125, 600, 45)
input_color = GRAY
active = False
text = ''
verse_lines = []
loading = False
angle = 0

output_x = 60
output_y = 190
output_width = 600
output_height = 280
scroll_offset = 0
content_height = 0

cursor_timer = 0
show_cursor = True

def draw_spinner(center_x, center_y, radius, angle):
    length = 8
    for i in range(length):
        fade = 255 - int((255 / length) * i)
        fade_color = (BLUE[0], BLUE[1], BLUE[2], fade)
        radians = angle + (2 * math.pi / length) * i
        x = center_x + radius * math.cos(radians)
        y = center_y + radius * math.sin(radians)
        pygame.draw.circle(screen, fade_color[:3], (int(x), int(y)), 6)

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
    Output only the 10 lines of the poem but do not number them. The title should be given without any " or * before it.
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

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + ' ' + word if current_line else word
        test_width = font.render(test_line, True, DARK).get_width()
        if test_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

clock = pygame.time.Clock()
running = True
model_selected = "EduPoem"
button_width = 200
button_height = 40
total_width = button_width * 2 + 20
edu_poem_x = (WIDTH // 2) - (total_width // 2)
gen_z_shii_x = edu_poem_x + button_width + 10

buttons = {
    "edu_poem": pygame.Rect(edu_poem_x, 70, button_width, button_height),
    "gen_z_shii": pygame.Rect(gen_z_shii_x, 70, button_width, button_height)
}

def render_button(text, rect, color, hover_color):
    mouse_pos = pygame.mouse.get_pos()
    pygame.draw.rect(screen, hover_color if rect.collidepoint(mouse_pos) else color, rect, border_radius=10)
    if (rect == buttons["edu_poem"] and model_selected == "EduPoem") or (rect == buttons["gen_z_shii"] and model_selected == "GenZ Type Shii"):
        pygame.draw.rect(screen, DARK, rect, border_radius=10)
    text_surface = LABEL_FONT.render(text, True, WHITE)
    screen.blit(text_surface, (rect.x + (rect.width - text_surface.get_width()) // 2, rect.y + (rect.height - text_surface.get_height()) // 2))

while running:
    screen.fill(LIGHT)
    angle += 0.1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if buttons["edu_poem"].collidepoint(event.pos):
                model_selected = "EduPoem"
            elif buttons["gen_z_shii"].collidepoint(event.pos):
                model_selected = "GenZ Type Shii"
            active = input_rect.collidepoint(event.pos)
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
                    scroll_offset = max(scroll_offset - 30, output_height - content_height)
                else:
                    text += event.unicode

        elif event.type == pygame.MOUSEWHEEL:
            scroll_offset = max(min(scroll_offset + event.y * 30, 0), output_height - content_height)

    cursor_timer += clock.get_time()
    if cursor_timer >= 500:
        cursor_timer = 0
        show_cursor = not show_cursor

    model_surface = TITLE_FONT.render(f"🎓 {model_selected} Generator", True, DARK)
    screen.blit(model_surface, (WIDTH // 2 - model_surface.get_width() // 2, 20))

    input_label = LABEL_FONT.render("Enter a topic (e.g. Gravity, Photosynthesis):", True, DARK)
    screen.blit(input_label, (input_rect.x, input_rect.y))

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

    render_button("EduPoem", buttons["edu_poem"], BLUE, DARK)
    render_button("GenZ Type Shii", buttons["gen_z_shii"], BLUE, DARK)

    pygame.draw.rect(screen, WHITE, (output_x, output_y + 15, output_width, output_height + 15), border_radius=15)

    if loading:
        draw_spinner(WIDTH // 2, HEIGHT // 2, 30, angle)
    else:
        y_start = output_y + scroll_offset + 23
        content_height = 0
        rendered_lines = []
        for line in verse_lines:
            if line.strip():
                wrapped_lines = wrap_text(line.strip(), OUTPUT_FONT, output_width - 20)
                for wrapped_line in wrapped_lines:
                    rendered_line = OUTPUT_FONT.render(wrapped_line, True, DARK)
                    rendered_lines.append((rendered_line, y_start + content_height))
                    content_height += 26

        for rendered_line, y_position in rendered_lines:
            screen.blit(rendered_line, (output_x + 10, y_position))

    pygame.display.update()
    clock.tick(60)


