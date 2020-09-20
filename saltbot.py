import discord
#import sqlite3
import os
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('BOT_TOKEN')
client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} ready.')

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.lower().startswith('!test'):
        await message.channel.send(':salt:')
client.run(token)