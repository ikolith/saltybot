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

available_items = []
game_channel = ''

db = sqlite3.connect("database.sqlite3") # we have just one of these for the whole program, since we don't need to share state with other processes or anything
cursor = db.cursor() # we have just one of these for the whole program, since we don't need to share state with other processes or anything
def query(query, values_to_substitute_in = ()):
    cursor.execute(query, values_to_substitute_in)
    db.commit() # commit any changes to the database file
    return cursor.fetchall() # return a list of all our findings
'''
async def post_and_spawn_item(item_query,spawn_message = ''):

    available_items.remove(item_query)
    await game_channel.send('-'+item_query[0][0]+'-' + ' crawls up the cave wall and disappears into it.')

async def salt_spawn():
    while True:
        await asyncio.sleep(1)
        #print(game_channel)
        if game_channel != '':
            time_to_salt_spawn = randint(5,500)
            print(time_to_salt_spawn)
            await asyncio.sleep(time_to_salt_spawn)
            salt_rock = query('SELECT * FROM items WHERE item_type = 'salt rock' ')
            await item_spawn(salt_rock,'You spot a -salt rock-.')
'''
async def spawn_handler(item_type, time_to_spawn_low, time_to_spawn_high, spawn_message, time_until_expiration, expiration_message):
    while True:
        await asyncio.sleep(1)
        if game_channel != '':
            time_to_spawn = randint(time_to_spawn_low,time_to_spawn_high) #should replace this with a tuple or something later
            await asyncio.sleep(time_to_spawn)
            #print(time_to_spawn) #here for testing, the two above lines will probably get consolidated later
            item_query = query('SELECT * FROM items WHERE item_type = ?',[item_type])
            available_items.append(item_query)
            await game_channel.send(spawn_message, file = discord.File ( ".\\art\\"+item_query[0][3], filename = item_query[0][3]))
            await asyncio.sleep(time_until_expiration)
            available_items.remove(item_query)
            await game_channel.send('-'+item_query[0][0]+'- ' + expiration_message)

async def take_item(message):
    #message.autho
    print('whoops didnt make this yet, gonna do the player registration')

#if we want to use sqlite3, here's how we would do it: (based on https://docs.python.org/3/library/sqlite3.html)
#see on_ready for this code in use
# you can also alter tables later, that's cool. there are many more commands
# I guess all tables in sqlite have a hidden ROWID which works as an autoincrementing integer primary key https://sqlite.org/autoinc.html
# which is useful for making foreign key references from one table to another, I think
#CODE should YELL at YOU
def create_tables():
    with open('schema.sql','r') as f:
        for line in f.readlines():
            try:
                query(line)
            except sqlite3.OperationalError as e:
                print(e)

def write_schema():
    with open('schema.sql',"w") as f:
        for result in query("SELECT sql FROM sqlite_master WHERE type='table';"):
            f.write(result[0]+'\n')

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
#def take_item(discord_id, item):
    #query()

@client.event
async def on_ready():
    print(f'{client.user} ready.')
    create_tables()
    print_players()
    try:
        insert_new_player(42)
    except:
        pass #there's already a player there (mostly because this is dummy example code)
    print_players()
    #we could make a more sophiticated system, but for now if you want to make or alter a table just paste the line here when you put it into create_tables

    #and remove it afterwards; that way it will execute once even though tables are already created
    # or you could just put the line at the TOP of create_tables, before the ones that are already created, I guess.
    write_schema() #TODO: we can create tables from schema and write the schema down, but what about when we want to populate semi-constant tables, like types of item? #and altering tables could get messy...
    await asyncio.gather(
        spawn_handler('pickaxe',10,30,'You spot a -pickaxe- on the ground',100,'Stabby Jim runs by and swipes the pickaxe.'),
        spawn_handler('salt rock',10,30,'You spot a -salt rock-.',100,'crawls up the cave wall and disappears into it.'))
    

@client.event
async def on_message(message):

    if message.author == client.user:
        return #don't react to our own messages
    
    if message.author.id not in [id for tuple in query('SELECT discord_id FROM players') for id in tuple]:
        insert_new_player(message.author.id)

    if check_message(message,'test'):
        await message.channel.send(':salt:')

    if check_message(message,'rasc'):
        await message.channel.send('rascd')
    
    if check_message(message,'take'):
        take_item(message)
    
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
