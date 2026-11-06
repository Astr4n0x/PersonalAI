
import asyncio
import edge_tts
import pygame
import time
from dotenv import dotenv_values

env = dotenv_values(".env")

VOICE = env.get("AI_voice", "en-US-AndrewNeural")
AUDIO_FILE = "voice.mp3"


async def generate_voice(text):
    communicate = edge_tts.Communicate(
        text=text,
        voice=VOICE,
        rate="-5%",
        pitch="+0Hz",
        volume="+0%",
    )

    await communicate.save(AUDIO_FILE)


def play_audio():
    pygame.mixer.init()
    pygame.mixer.music.load(AUDIO_FILE)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.05)

    pygame.mixer.music.unload()
    pygame.mixer.quit()


def speak(text):
    asyncio.run(generate_voice(text))
    play_audio()


if __name__ == "__main__":
    while True:
        msg = input("\nYou: ")

        if msg.lower() in ("exit", "quit"):
            break

        speak(msg)
