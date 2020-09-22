#!/usr/bin/env python3

import discord
import sqlite3
import os
import asyncio
from random import randint
token_error = "No token found. Please create a file called secret_token.py in the same directory as saltybot and put in that file the text: BOT_TOKEN=\"whatever.your.bot.token.is.blah.blah.blah\"\nthe rest of the script will attempt to run now, but almost certainly will not work.\n"
try:
    from secret_token import BOT_TOKEN
except:
    print(token_error)
if(not BOT_TOKEN):
    print(token_error)
client = discord.Client()

game_channel = ''

db = sqlite3.connect("database.sqlite3") # we have just one of these for the whole program, since we don't need to share state with other processes or anything
cursor = db.cursor() # we have just one of these for the whole program, since we don't need to share state with other processes or anything
def query(query, values_to_substitute_in = ()):
    cursor.execute(query, values_to_substitute_in)
    db.commit() # commit any changes to the database file
    return cursor.fetchall() # return a list of all our findings

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
# you can also alter tables later, that's cool. there are many more commands
#CODE should YELL at YOU
def create_tables():
    #there are ways we could create this using other programs or tools, but in-code is probably best for us to keep track of it.
    query("CREATE TABLE players (discord_id INT UNIQUE, points INT)")
    query("CREATE TABLE owned_items (discord_id INT UNIQUE, item_type INT, scrip TEXT, FOREIGN KEY(item_type) REFERENCES items(item_type))")
    query("CREATE TABLE items (item_type INT, description TEXT, price INT)")

    # I guess all tables in sqlite have a hidden ROWID which works as an autoincrementing integer primary key https://sqlite.org/autoinc.html
    # which is useful for making "pointers" from one table to another, I think
def insert_new_player(discord_id):
    query("INSERT INTO players VALUES (?, ?)", (discord_id, 0))
def print_players():
    print(query("SELECT * FROM players")) #could also fetchone if we wanted only one player
def check_message(message,cue):
    if game_channel != '' or message.content.lower().startswith('!gamehere'):
        #this check could be moved to on_ready to save some time later..?
        return message.content.lower().startswith('!'+ cue)
    else: 
        return False
#def return_items(discord_id):
    #return query("SELECT * FROM items WHERE player = ?",discord_id)
def take_item(discord_id, item):
    query()

@client.event
async def on_ready():
    print(f'{client.user} ready.')
    #example code
    try:
        create_tables()
    except sqlite3.OperationalError as e:
        print(e)
        print("aborting table creation")
    print_players()
    try:
        insert_new_player(42)
    except:
        pass #there's already a player there (mostly because this is dummy example code)
    print_players()
    #we could make a more sophiticated system, but for now if you want to make or alter a table just paste the line here when you put it into create_tables

    #and remove it afterwards; that way it will execute once even though tables are already created
    # or you could just put the line at the TOP of create_tables, before the ones that are already created, I guess.
    print(query("SELECT * FROM sqlite_master WHERE type='table';")) #TODO: print this out to a file to track schema changes. MAYBE: read that file in in create_tables()
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

client.run(BOT_TOKEN)
