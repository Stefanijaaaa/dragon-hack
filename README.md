# Educational Song Generator

A simple desktop app that uses AI to generate short educational songs or Gen Z-style explanations based on any topic you type in.

## Features

- Two generation styles:
  - **EduPoem**: A 10-line educational poem that's catchy and easy to remember.
  - **GenZ Type Shii**: A short, slang-filled explanation using Gen Z humor and references.
- Built-in text-to-speech support (reads out the generated text).
- Scrollable output area for longer responses.
- Clean and minimal UI built with Pygame.
- Uses Gemini (Google's AI model) for content generation.

## Requirements

- Python 3.x
- An internet connection (for the AI)
- A Gemini API key

## Setup

1. Install the required Python packages:

   ```bash
   pip install pygame python-dotenv google-generativeai pyttsx3

2. Create a .env file in the project folder and add your Gemini API key:

   GEMINI_API_KEY=Your_key_here

3. Run the script: 

   python main.py
