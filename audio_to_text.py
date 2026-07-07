import asyncio
import os
import uuid
from aiogram import Bot, Dispatcher, F
from groq import Groq

# Initialize Bot and Dispatcher
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(F.voice | F.video | F.video_note)
async def voice_to_text(m):
    status_msg = await m.reply("Processing.....")

    uid = str(uuid.uuid4())
    input_file = f"input_{uid}"
    output_mp3 = f"audio_{uid}.mp3"


    # Get file info and download the .ogg file from Telegram servers
    if m.voice:
        file_id = m.voice.file_id
    elif m.video_note:
        file_id = m.video_note.file_id
    elif m.video:
        file_id = m.video.file_id

    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, input_file)

    os.system(f"ffmpeg -i {input_file} -vn -acodec libmp3lame -ac 1 -ar 16000 -ab 24k {output_mp3} -y -loglevel quiet")

    try:
      with open(output_mp3, "rb") as audio_file:
        transcription = groq_client.audio.transcriptions.create(
          model="whisper-large-v3-turbo",
          file=audio_file,
          language="ru",
          prompt="Текст может содержать как русский, так и украинский или английский языки. Пиши точно, расставляй знаки препинания."
        )

      text = transcription.text.strip()
      await status_msg.edit_text(text if text else "Can't recognize text.")

    except Exception as e:
        await status_msg.edit_text(f"Recognition error {e}")
    finally:
        for f in [input_file, output_mp3]:
            if os.path.exists(f): os.remove(f)


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
