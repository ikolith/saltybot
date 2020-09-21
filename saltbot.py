#!/usr/bin/env python3
#

import discord
import sqlite3
import os
import asyncio
from random import randint
from secret_token import BOT_TOKEN

token = BOT_TOKEN
if(not token):
    print("no token found. Please create a file called secret_token.py in the same directory as saltybot and put in that file the text: BOT_TOKEN=\"whatever.your.bot.token.is.blah.blah.blah\"")
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
            print(time_to_salt_spawn)
            await asyncio.sleep(time_to_salt_spawn)
            print('send salt')
            await game_channel.send('salt')

#if we want to use sqlite3, here's how we would do it: (based on https://docs.python.org/3/library/sqlite3.html)
#see on_ready for this code in use
#by the way, all these commands are case insentive so i suggest we use lowercase to be super cas.
# you can also alter tables later, that's cool. there are many more commands
def create_database():
    #there are ways we could create this using other programs or tools, but in-code is probably best for us to keep track of it.
    db = sqlite3.connect("database.sqlite3") # i guess we could have just one of these for the whole file, since we don't need to share state with other processes or anything
    cursor = db.cursor()
    cursor.execute("create table players (discord_id int unique, points int)")
    # I guess all tables in sqlite have a hidden ROWID which works as an autoincrementing integer primary key https://sqlite.org/autoinc.html
    # which is useful for making "pointers" from one table to another, I think
    db.commit() # commit the changes to the database file
    db.close() # close connect (will discard uncommited changes)
def insert_new_player(discord_id):
    db = sqlite3.connect("database.sqlite3")
    cursor = db.cursor()
    cursor.execute("insert into players values (?, ?)", (discord_id, 0)) #NEVER use regular string interpolation!
    db.commit()
    db.close()
def print_players():
    db = sqlite3.connect("database.sqlite3")
    cursor = db.cursor()
    cursor.execute("select * from players")
    print(cursor.fetchall()) #could also fetchone if we wanted only one player
    db.close()
def check_message(message,cue):
   return message.content.lower().startswith('!'+ cue)

@client.event
async def on_ready():
    print(f'{client.user} ready.')
    #example code
    try:
        create_database()
    except:
        pass
    print_players()
    try:
        insert_new_player(42)
    except:
        pass #there's already a player there (mostly because this is dummy example code)
    print_players()
    await salt_spawn()

@client.event
async def on_message(message):

    if message.author == client.user:
        return #don't react to our own messages

    if check_message(message,'test'):
        await message.channel.send(':salt:')
    
    if check_message(message,'gamehere'):
        print('got it: game_channel = ' + str(message.channel))
        global game_channel
        game_channel = message.channel

#TODO: we probably want a more elegant dispatch system than string startswith checking
        #this code could be compressed/refactored.
#TODO: gosh, we're gonna have to parse, aren't we? yee haw.
#TODO: also the more elegant system should check game channel and so forth
    if check_message(message,'leanin'):
        await message.channel.send(message.author.name + " activates Lean In Stance, gaining +1 to offensive moves!")
        #TODO: this doesnt do anything yet lol

    if check_message(message,'getout'):
        await message.channel.send(message.author.name + " activates Get Out Stance, gaining +1 to retreative moves!")
        #TODO: this doesnt do anything yet lol

    if check_message(message,'playchicken'):
        await message.channel.send(message.author.name + " remembers what Herbert the Affectionate Insectoid said about chicken, and runs off a cliff for no reason!")
        #TODO: this should actually let you play chicken

    if check_message(message,'saltman'):
        await message.channel.send(':snowman2:')
    if check_message(message,'jungledog'):
        await message.channel.send(':dog2:')
    if check_message(message,'scrip'):
        #TODO: should require paper and writing utensil (or... any object? put scrip on a dog lol)
        #TODO: this should really be !scrip [object from inventory] [quantity of money or other object]
        await message.channel.send(message.author.name + " writes '$5' on a piece of paper and signs it!")
        
    #if message.content.lower().startswith('')

client.run(token)
