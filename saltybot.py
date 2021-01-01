#!/usr/bin/env python3

import discord
import json
import os
import time
import atexit
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

#these should probably go into state eventually
available_items = []
spawn_channel = ''

#Don't step on my bread!
state = {"players": {}, "items": {}}

async def spawn_handler(item_type, time_to_spawn_low, time_to_spawn_high, spawn_message, time_until_expiration, expiration_message):
    while True:
        await asyncio.sleep(1)
        if spawn_channel != '':
            time_to_spawn = randint(time_to_spawn_low,time_to_spawn_high) #should replace this with a tuple or something later
            await asyncio.sleep(time_to_spawn)
            #print(time_to_spawn) #here for testing, the two above lines will probably get consolidated later
            item_query = [item for item in state.items if item["item_type"] == item_type]
            item_query = item_query[0]
            available_items.append(item_query)
            await spawn_channel.send(spawn_message, file = discord.File ( "./art/"+item_query[3], filename = item_query[3]))
            await asyncio.sleep(time_until_expiration)
            available_items.remove(item_query)
            await spawn_channel.send('-'+item_query[0]+'- ' + expiration_message)

    #query('INSERT INTO owned_items (discord_id, item_type) VALUES (?,?)',(message.author_id, item))

#CODE should YELL at YOU
#"\"You get nothing. You LOSE, sir!\""
def write_state():
    global state
    with open("tmp.backup.json.bak", "w") as f:
        json.dump(state, f)
    with open("state.json", "w") as f:
        json.dump(state, f)
    os.replace('tmp.backup.json.bak', "statebackups/"+str(int(time.time()))+" - "+time.strftime("%Y-%m-%d--%H-%M-%S")+' - state.json.bak') #moves a file. the .bak files serves as a backup
    #this would be time_ns but I'm scared to update my python installation.

atexit.register(write_state) #when process ends or crashes (unless it crashes really badly...) it will write out the state. #should think about periodically writing out state anyway.

def insert_new_player(discord_id):
    global state
    if discord_id not in state["players"].keys():
        state["players"][str(discord_id)] = {}
def print_players():
    global state
    print(state["players"])

@client.event
async def on_ready():
    global state
    print(f'{client.user} ready.')
    try:
        with open('state.json') as f:
            #TODO: This makes everything a string, which may or may not be a problem.
            state = json.load(f)
    except:
        print("Couldn't load state.json, so we default to the empty shell of a state given near the top of this file")
    print("state: "+ str(state))
    print_players()
    insert_new_player(42) #idempotent
    print_players()

    await asyncio.gather(
        spawn_handler('pickaxe',1,3,'A -pickaxe- lies on the ground.',100,'Stabby Jim runs by and swipes the pickaxe.'),
        spawn_handler('salt rock',1,3,'A -salt rock- rolls into view.',100,'crawls up the cave wall and disappears into it.'))

bot_prefix = "!"

@client.event
async def on_message(message):
    global state
    command = message.content.lower()
    print(command)
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
    
    if str(message.author.id) not in state["players"].keys():
        insert_new_player(message.author.id)
        print("I'm inserting here!")

    if consume('test'):
        await message.channel.send('loaf')

    if consume('spawnhere'):
        print('got it: spawn_channel = ' + str(message.channel))
        global spawn_channel
        spawn_channel = message.channel

    if consume('take'):
        for item in available_items:
            print(item)
        #print(available_items)
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
        #TODO: should require paper (or... any object? put scrip on a dog lol) and writing utensil
        #TODO: this should really be !scrip [object from inventory] [quantity of money or other object]
        await message.channel.send(message.author.name + " writes '$5' on a piece of paper and signs it!")
    npcs = {
        "walrus": ":gun:",
        "herbert": '"Eheheh so you want to know how to play chicken, huh?" says Herbert the Affectionate Insectoid. "Well it\'s simple. Just !playchicken to run off a cliff!"',
        #TODO: broify these?
        "brofucius": 'Brofucius say, "The philosopher Yu said, \'When agreements are made according to what is right, what is spoken can be made good. When respect is shown according to what is proper, one keeps far from shame and disgrace. When the parties upon whom a man !leanin are proper persons to be intimate with, he can make them his guides and masters.\'"',
        "brozi": '"Holding and filling it, are not as good as !getout," says Brozi.',
        'joe': "As soon as you make eye contact with the Duke of Joe, his eyes flash red. \"The pact is sealed,\" he chuckles, \" you are now a boo hoo boy for the Tong of Joe!\"",
        'sanders': "As soon as you make eye contact with the Duke of Sanders, his eyes flash red. \"The pact is sealed,\" he chuckles, \" you are now a boo hoo boy for the Tong of Sanders!\"", #Duke of Sanders is a grizzly bear
        'ben':  "Ben Stiller, The Actor, The American One, From Real Life (No Relation), takes a puff of his pipe. \"Ah, yes, to quote https://en.wikipedia.org/wiki/Ben_Stiller, Benjamin Edward Meara Stiller (born November 30, 1965) is an American actor, comedian, film producer, film director, and writer. He is the son of the late comedians and actors Jerry Stiller and Anne Meara.[1] After beginning his acting career with a play, Stiller wrote several mockumentaries and was offered his own show, titled The Ben Stiller Show, which he produced and hosted for its 13-episode run. Having previously acted in television, he began acting in films. He made his directorial debut with Reality Bites. Throughout his career he has written, starred in, directed, or produced more than 50 films including The Secret Life of Walter Mitty, Zoolander, The Cable Guy, There's Something About Mary, the Meet the Parents trilogy, DodgeBall, Tropic Thunder, the Madagascar series, and the Night at the Museum trilogy. He has also made numerous cameos in music videos, television shows, and films.[2] Stiller is a member of a group of comedic actors colloquially known as the Frat Pack. His films have grossed more than $2.6 billion in Canada and the United States, with an average of $79 million per film.[3] Throughout his career, he has received various awards and honors, including an Emmy Award, multiple MTV Movie Awards, a Britannia Award and a Teen Choice Award.\" He takes another puff of his pipe. \"Not me though.\"",
        'papa': "Papa Conflictdollar says, \"more like crapiDEADism, if you know what i mean!\"",
        'paul': "\"Where are we?\" you ask Paul Rizer. Paul looks at you like you're stupid. \"Neoklahoma,\" he responds, \"The greatest country on earth!\"."
    }
    npcs["Kwan"] = "Kwan Titty lists all the people he knows: "+ " ".join(npcs) #don't include hot towel guy in this list
    if consume('ask '):
        for key, value in npcs.items():
            if consume(key):
                await message.channel.send(value)
                return

client.run(BOT_TOKEN)
