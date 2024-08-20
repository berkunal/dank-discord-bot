import discord
from discord.ext import commands
import os
from gtts import gTTS
import asyncio
from datetime import datetime
import pytz
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('discord')
logger.name = 'bot'

TOKEN = os.getenv('DISCORD_TOKEN')
TEST_CHANNEL = os.getenv('TEST_CHANNEL')
OWNER_ID = os.getenv('OWNER_ID')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

NAMES = {
    'animalbender': 'emir',
    'oto_nat': 'onat',
    'maglor_carnesir': 'berk'
}
istanbul_tz = pytz.timezone('Europe/Istanbul')

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize the generative AI model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name='gemini-1.5-flash',
                              system_instruction='You are a flirty female character. Please respond without using any emojis. You speak only Turkish.')

async def is_owner(ctx):
    return ctx.author.id == OWNER_ID

@bot.event
async def on_ready():
    logger.info(f'Logged in as {bot.user}')

@bot.event
async def on_voice_state_update(member, before, after):
    if member.name.lower() == 'hasanberk':
        return

    member_name = NAMES[member.name.lower()]

    if before.channel is None and after.channel is not None:
        await generate_ai_response_and_send(after.channel, f'{member_name} geldi ve karsinda duruyor')
    elif before.channel is not None and after.channel is None:
        text_channel = await bot.fetch_channel(TEST_CHANNEL)
        response = await generate_ai_response(f'{member_name} ortamdan ayrildi. onunla uzun uzun konustun bugun. onunla yedinci bulusmanizdi. ona gule gule mesaji yaz.')
        if response.text is not None:
            await text_channel.send(response.text)
    elif before.channel is after.channel:
        await generate_ai_response_and_send(after.channel, f'{member_name} ekran paylasiyor')
    else:
        await send_voice_message(after.channel, f'{member_name} nerden geldin, nereye gidiyon')

@bot.command(help='Displays the current status of the bot.')
async def status(ctx):
    await ctx.send('Hasanberk is cooking!')
    
@bot.command(help='Displays the current latency of the bot.')
async def ping(ctx):
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

@bot.command(name='shutdown-bot', help='Shuts down the bot. Only the owner can use this command.')
@commands.check(is_owner)
async def shutdown_bot(ctx):
    await ctx.send('Shutting down Hasaberk...')
    await bot.close()

@bot.command(help='Shuts down the machine. Only the owner can use this command.')
@commands.check(is_owner)
async def shutdown(ctx):
    await ctx.send('Shutting down machine...')
    os.system('sudo shutdown -h now')

@bot.command(help='Reboots the machine. Only the owner can use this command.')
@commands.check(is_owner)
async def reboot(ctx):
    await ctx.send('Rebooting machine...')
    os.system('sudo reboot')

@bot.command(help='Text to speech. Usage: !tts "<text>"') 
async def tts(ctx, text: str):
    if ctx.author.voice is None:
        await ctx.send('You are not connected to a voice channel.')
        return

    voice_channel = ctx.author.voice.channel

    await send_voice_message(voice_channel, text)

@bot.command(help='Generates text using the Gemini model. Usage: !gemini "<text>"')
async def gemini(ctx, text: str):
    if ctx.author.voice is None:
        await ctx.send('You are not connected to a voice channel.')
        return

    response = await generate_ai_response(text)

    if response.text is None:
        await ctx.send(f'Sorry, I could not generate text')
        return

    voice_channel = ctx.author.voice.channel
    await send_voice_message(voice_channel, response.text)
    
async def send_voice_message(voice_channel, text: str):
    logger.info('Joining voice channel...')
    vc = await voice_channel.connect()

    tts = gTTS(text=text, lang='tr')
    tts.save('tts.mp3')
    
    vc.play(discord.FFmpegPCMAudio('tts.mp3'), after=lambda e: os.remove('tts.mp3'))

    while vc.is_playing():
        await asyncio.sleep(1)
    
    await vc.disconnect()
    logger.info('Disconnected from voice channel.')

async def generate_ai_response(text: str):
    return model.generate_content(text, safety_settings=[
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}])

async def generate_ai_response_and_send(voice_channel, text: str):
    response = await generate_ai_response(text)

    if response.text is None:
        return

    await send_voice_message(voice_channel, response.text)

bot.run(TOKEN)
