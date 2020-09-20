import discord
import sqlite3
import os
import asyncio
from random import randint
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('BOT_TOKEN')
client = discord.Client()
game_channel = 'not set'

async def salt_spawn():
    while True:
        await asyncio.sleep(1)
        #print(game_channel)
        if game_channel != 'not set':
            time_to_salt_spawn = randint(2,5)
            await asyncio.sleep(time_to_salt_spawn)
            print('send salt')
            print(time_to_salt_spawn)


@client.event
async def on_ready():
    print(f'{client.user} ready.')
    #await salt_spawn()
    await salt_spawn()

@client.event
async def on_message(message):

    if message.author == client.user:
        return

    if message.content.lower().startswith('!test'):
        await message.channel.send(':salt:')
    
    if message.content.lower().startswith('!gamehere'):
        print('got it')
        global game_channel
        game_channel = message.channel

        print(game_channel)
    #if message.content.lower().startswith('')

client.run(token)