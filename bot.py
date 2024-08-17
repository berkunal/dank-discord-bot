import discord
from discord.ext import commands
import os
from gtts import gTTS
import asyncio
from datetime import datetime
import pytz
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('discord')
logger.name = 'bot'

TOKEN = os.getenv('DISCORD_TOKEN')
TEST_CHANNEL = os.getenv('TEST_CHANNEL')
OWNER_ID = os.getenv('OWNER_ID')

NAMES = {
    'animalbender': 'emir bey',
    'oto_nat': 'onat bey',
    'maglor_carnesir': 'maglor bey'
}
istanbul_tz = pytz.timezone('Europe/Istanbul')

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix='!', intents=intents)

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
        if member_name == 'maglor bey':
            await send_voice_message(after.channel, f'Selam berkcim')
        elif member_name == 'emir bey':
            await send_voice_message(after.channel, f'{member_name} geldi sakin olun.')
        else:
            await send_voice_message(after.channel, f'Beyler dağılın, Onat abiniz geldi.')
    elif before.channel is not None and after.channel is None:
        text_channel = await bot.fetch_channel(TEST_CHANNEL)
        message = f'Iyi geceler, {member_name}' if is_night() else f'Iyi gunler, {member_name}'
        await text_channel.send(message)
    elif before.channel is after.channel:
        await send_voice_message(after.channel, f'{member_name} deminden shimdiye geldi')
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

def is_night():
    now = datetime.now(tz=istanbul_tz)
    return now.hour >= 21 and now.hour < 6

bot.run(TOKEN)
