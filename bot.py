import discord
from discord.ext import commands
import os
from gtts import gTTS
import asyncio
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
TEST_CHANNEL = os.getenv('TEST_CHANNEL')

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

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
        message = f'Iyi geceler, {member_name}' if not is_night() else f'Iyi gunler, {member_name}'
        await text_channel.send(message)
    else:
        await send_voice_message(after.channel, f'Bu hareket neydi {member_name}')

@bot.command()
async def status(ctx):
    await ctx.send('Raspberry Pi is running smoothly!')

@bot.command()
async def tts(ctx, text: str):
    if ctx.author.voice is None:
        await ctx.send('You are not connected to a voice channel.')
        return

    voice_channel = ctx.author.voice.channel

    await send_voice_message(voice_channel, text)
    
async def send_voice_message(voice_channel, text: str):
    print('Joining voice channel...')
    vc = await voice_channel.connect()
    
    tts = gTTS(text=text, lang='tr')
    tts.save('tts.mp3')
    
    vc.play(discord.FFmpegPCMAudio('tts.mp3'), after=lambda e: os.remove('tts.mp3'))

    while vc.is_playing():  
        await asyncio.sleep(1)
    
    await vc.disconnect()
    print('Disconnected from voice channel.')

def is_night():
    now = datetime.now(tz=istanbul_tz)
    return now.hour >= 21 and now.hour < 6

bot.run(TOKEN)
