import asyncio, os, speech_recognition as sr
from aiogram import Bot, Dispatcher, F
import uuid
import os

# Initialize Bot and Dispatcher
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
rec = sr.Recognizer()


@dp.message(F.voice | F.video | F.video_note)
async def voice_to_text(m):
    status_msg = await m.reply("Proccessing.....\n Pay attention that you can transcribe <=60 sec audio or <=20mb video")

    uid = str(uuid.uuid4())
    input_file = f"input_{uid}"
    output_wav = f"audio_{uid}.wav"


    # Get file info and download the .ogg file from Telegram servers
    if m.voice:
        file_id = m.voice.file_id
    elif m.video_note:
        file_id = m.video_note.file_id
    elif m.video:
        file_id = m.video.file_id

    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, input_file)

    # Convert OGG to WAV using ffmpeg (Google API requires WAV/FLAC)
    os.system(f"ffmpeg -i {input_file} -vn -ac 1 -ar 16000 {output_wav} -y -loglevel quiet")


    try:
        # Open the converted file and record audio data
        with sr.AudioFile(output_wav) as s:
            # Send audio data to Google Speech Recognition API
            t = rec.recognize_google(rec.record(s), language="ru-RU,en-US")
            await status_msg.edit_text(t)
    except Exception:
        # Handle recognition errors (e.g., silence or no internet)
        import traceback
        traceback.print_exc()
        await m.answer("Recognition error")
    finally:
        for f in [input_file, output_wav]:
            if os.path.exists(f): os.remove(f)


if __name__ == "__main__":
    # Start the polling process
    asyncio.run(dp.start_polling(bot))
