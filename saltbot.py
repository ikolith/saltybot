#!/usr/bin/env python3
#

import discord
import sqlite3
import os
import asyncio
from random import randint
from dotenv import load_dotenv


load_dotenv()
token = os.getenv('BOT_TOKEN')
if(not token):
    print("no token found. Please create a file called .env in the same directory as saltybot and put in that file the text: BOT_TOKEN=\"whatever.your.bot.token.is.blah.blah.blah\"")
    print("the rest of the script will attempt to run now, but almost certainly will not work.")
    print()
client = discord.Client()
game_channel = ''

async def salt_spawn():
    while True:
        await asyncio.sleep(1)
        #print(game_channel)
        if game_channel != '':
            time_to_salt_spawn = randint(5,500)
            await asyncio.sleep(time_to_salt_spawn)
            print('send salt')
            await game_channel.send('salt')
            print(time_to_salt_spawn)


@client.event
async def on_ready():
    print(f'{client.user} ready.')
    #await salt_spawn()
    await salt_spawn()

@client.event
async def on_message(message):

    if message.author == client.user:
        return #don't react to our own messages

    if message.content.lower().startswith('!test'):
        await message.channel.send(':salt:')
    
    if message.content.lower().startswith('!gamehere'):
        print('got it: game_channel = ' + str(message.channel))
        global game_channel
        game_channel = message.channel

#TODO: we probably want a more elegant dispatch system than string startswith checking
        #this code could be compressed/refactored.
#TODO: gosh, we're gonna have to parse, aren't we? yee haw.
#TODO: also the more elegant system should check game channel and so forth
    if message.content.lower().startswith('!leanin'):
        await message.channel.send(message.author.name + " activates Lean In Stance, gaining +1 to offensive moves!")
        #TODO: this doesnt do anything yet lol

    if message.content.lower().startswith('!getout'):
        await message.channel.send(message.author.name + " activates Get Out Stance, gaining +1 to retreative moves!")
        #TODO: this doesnt do anything yet lol

    if message.content.lower().startswith('!playchicken'):
        await message.channel.send(message.author.name + " remembers what Herbert the Affectionate Insectoid said about chicken, and runs off a cliff for no reason!")
        #TODO: this should actually let you play chicken

    if message.content.lower().startswith('!saltman'):
        await message.channel.send(':snowman2:')
    if message.content.lower().startswith('!jungledog'):
        await message.channel.send(':dog2:')
    if message.content.lower().startswith('!scrip'):
        #TODO: should require paper and writing utensil (or... any object? put scrip on a dog lol)
        #TODO: this should really be !scrip [object from inventory] [quantity of money or other object]
        await message.channel.send(message.author.name + " writes '$5' on a piece of paper and signs it!")
        
    #if message.content.lower().startswith('')

client.run(token)
