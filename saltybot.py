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
spawn_channel = ''

db = sqlite3.connect("database.sqlite3") # we have just one of these for the whole program, since we don't need to share state with other processes or anything
cursor = db.cursor() # we have just one of these for the whole program, since we don't need to share state with other processes or anything
def query(query, values_to_substitute_in = ()):
    cursor.execute(query, values_to_substitute_in)
    db.commit() # commit any changes to the database file
    return cursor.fetchall() # return a list of all our findings #this seems to usually return a tuple of tuples of length one? weird

async def spawn_handler(item_type, time_to_spawn_low, time_to_spawn_high, spawn_message, time_until_expiration, expiration_message):
    while True:
        await asyncio.sleep(1)
        if spawn_channel != '':
            time_to_spawn = randint(time_to_spawn_low,time_to_spawn_high) #should replace this with a tuple or something later
            await asyncio.sleep(time_to_spawn)
            #print(time_to_spawn) #here for testing, the two above lines will probably get consolidated later
            item_query = query('SELECT * FROM items WHERE item_type = ?',[item_type])
            item_query = item_query[0]
            available_items.append(item_query)
            await spawn_channel.send(spawn_message, file = discord.File ( "./art/"+item_query[3], filename = item_query[3]))
            await asyncio.sleep(time_until_expiration)
            available_items.remove(item_query)
            await spawn_channel.send('-'+item_query[0]+'- ' + expiration_message)

def take_item(message):
    take_list = []
    print(available_items)
    message_list = message.content.split(' ')
    for item in available_items:
        if item[0] in message_list:
            take_list.append(item)
    print(take_list)
    #query('INSERT INTO owned_items (discord_id, item_type) VALUES (?,?)',(message.author_id, item))

#CODE should YELL at YOU
def get_schema(): return query("SELECT sql FROM sqlite_master WHERE type='table';")
def get_schema_as_lines(): return "\n".join([i[0] for i in get_schema()])

def sql_repl(): #TODO: there is no way to make statements without commiting, which is a bit dangerous
    while True:
        response = input("please enter a sql statement, \"help\" (\"h\"/\"?\"), or \"quit\" (\"q\"/\"x\")> ")
        if response.lower() == "help" or response.lower() == "h" or response.lower() == "?":
            print("you are beyond help")
        elif response.lower() == "quit" or response.lower() == "q" or response.lower() == "x":
            return
        else:
            try:
                print(query(response))
            except sqlite3.OperationalError as e:
                print(e)

def create_tables():
    with open('schema.sql','r') as f:
        for line in f.readlines():
            try:
                query(line)
            except sqlite3.OperationalError as e:
                print(e)

def sync_schema():
    with open('schema.sql','r') as f:
        extant_schema = f.read() #I think this doesn't work to read twice, so we have to cache it
        if any(get_schema()) and extant_schema != get_schema_as_lines():
            print("!!!SCHEMA CONFLICT DETECTED!!!")
            print("schema.sql:")
            print(extant_schema)
            print("internal schema:")
            print(get_schema_as_lines())
            with open('tmp.schema.sql','w') as tmp:
                tmp.write(get_schema_as_lines())
            print("The database schema specified in schema.sql does not match the schema in the current database, which has been printed to tmp.schema.sql")
            print("This likely means that the database schema has been updated since you last ran this project.")
            print("Your three options are to [d]elete the current database and remake it with the new schema (ALL YOUR DATA WILL BE LOST!), [a]lter the database here on the command line using statements like ALTER TABLE table_name ADD column_name datatype; (safe if you know what you're doing), or a[b]ort this run of the program and try to alter the table through some external means like a sqlite3 database editing tool.")
            print("Secret option: if you're sure the difference in schema consists only in new tables having been added, you can type literally anything else to just proceed with the program.")
            response = input("d, a, b? > ")
            if response == "d":
                db.close()
                os.replace('database.sqlite3', 'database.sqlite3.bak') #moves a file. the .bak files serves as a backup 
            elif response == "a":
                sql_repl()
                print("Attempting to proceed...")
                sync_schema() #is this going to try to open f again?
            elif response == "b":
                exit()
        create_tables() #is this going to try to open f again?

def write_schema():
    os.replace('schema.sql', 'schema.sql.bak') #moves a file. the .bak files serves as a backup
    with open('schema.sql',"w") as f:
        for line in get_schema():
            f.write(line[0]+'\n')

def insert_new_player(discord_id):
    query("INSERT INTO players VALUES (?, ?)", (discord_id, 0))
def print_players():
    print(query("SELECT * FROM players")) #could also fetchone if we wanted only one player

#def return_items(discord_id):
    #return query("SELECT * FROM items WHERE player = ?",discord_id)
#def take_item(discord_id, item):
    #query()

@client.event
async def on_ready():
    print(f'{client.user} ready.')
    print(get_schema())
    sync_schema()
    print_players()
    try:
        insert_new_player(42)
    except:
        pass #there's already a player there (mostly because this is dummy example code)
    print_players()
    #we could make a more sophiticated system, but for now if you want to make or alter a table just paste the line here when you put it into create_tables

    #and remove it afterwards; that way it will execute once even though tables are already created
    # or you could just put the line at the TOP of create_tables, before the ones that are already created, I guess.
    #write_schema() #TODO: we can create tables from schema and write the schema down, but what about when we want to populate semi-constant tables, like types of item? #and altering tables could get messy...
    await asyncio.gather(
        spawn_handler('pickaxe',1,3,'A -pickaxe- lies on the ground.',100,'Stabby Jim runs by and swipes the pickaxe.'),
        spawn_handler('salt rock',1,3,'A -salt rock- rolls into view.',100,'crawls up the cave wall and disappears into it.'))

bot_prefix = "!"

@client.event
async def on_message(message):
    command = message.content.lower()
    def consume(eat_this):  #this may not be named great
        nonlocal command
        if command.lower().startswith(eat_this.lower()):
            command = command.lower().replace(eat_this.lower(),"",1)
            return True
        else:
            return False
    if not consume(bot_prefix):
            return
    #print(message) #debug feature TODO: a way to turn this off/on
    #print(message.content)
    if message.author == client.user:
        return #don't react to our own messages
    
    if message.author.id not in [id for tuple in query('SELECT discord_id FROM players') for id in tuple]:
        insert_new_player(message.author.id)

    if consume('test'):
        await message.channel.send('loaf')

    if consume('spawnhere'): #can't use check_message because that checks in spawn_channel is set
        print('got it: spawn_channel = ' + str(message.channel))
        global spawn_channel
        spawn_channel = message.channel

    if consume('take'):
        take_item(message)
    #now we get into the big boy parsing #TODO: implement parsing

    if consume('leanin'):
        await message.channel.send(message.author.name + " activates Lean In Stance, gaining +1 to offensive moves!")
        #TODO: this doesnt do anything yet lol

    if consume('getout'):
        await message.channel.send(message.author.name + " activates Get Out Stance, gaining +1 to retreative moves!")
        #TODO: this doesnt do anything yet lol

    if consume('playchicken'):
        await message.channel.send(message.author.name + " runs off a cliff for no reason!")
        #TODO: this should actually let you play chicken

    if consume('saltman'):
        await message.channel.send(':snowman2:')
    if consume('jungledog'):
        await message.channel.send(':dog2:')
    if consume('scrip'):
        #TODO: should require paper and writing utensil (or... any object? put scrip on a dog lol)
        #TODO: this should really be !scrip [object from inventory] [quantity of money or other object]
        await message.channel.send(message.author.name + " writes '$5' on a piece of paper and signs it!")
    npcs = {
        "walrus": ":gun:",
        "herbert": '"Eheheh so you want to know how to play chicken, huh?" says Herbert the Affectionate Insectoid. "Well it\'s simple. Just !playchicken to run off a cliff!"',
        #TODO: broify these?
        "brofucius": 'Brofucius say, "The philosopher Yu said, \'When agreements are made according to what is right, what is spoken can be made good. When respect is shown according to what is proper, one keeps far from shame and disgrace. When the parties upon whom a man !leanin are proper persons to be intimate with, he can make them his guides and masters.\'"',
        "brozi": '"Holding and filling it, are not as good as !getout," says Brozi.',
        'joe': "As soon as you make eye contact with the Duke of Joe, his eyes flash red. \"The pact is sealed,\" he chuckles, \" you are now a boo hoo boy for the Tong of Joe!\"",
        'sanders': "As soon as you make eye contact with the Duke of Sanders, his eyes flash red. \"The pact is sealed,\" he chuckles, \" you are now a boo hoo boy for the Tong of Sanders!\"" #Duke of Sanders is a grizzly bear
    }
    npcs["paul"] = "Paul Rizer lists all the people he knows: "+ " ".join(npcs)
    if consume('ask '):
        for key, value in npcs.items():
            if consume(key):
                await message.channel.send(value)
                return

client.run(BOT_TOKEN)
