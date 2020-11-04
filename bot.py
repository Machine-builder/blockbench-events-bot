import json
import os
import math

import discord

client = discord.Client()


# aliases for commands can be setup like so;
# @client.command(aliases=['test','something'])

CONFIG = json.load( open( os.path.join(os.getcwd(), 'config.json') ,'r') )
PREFIX = CONFIG['bot_prefix']



def loadEventData():
    return json.load(open( os.path.join(os.getcwd(), CONFIG['event_info_file']), 'r'))
def dumpEventData(d):
    json.dump(d, open( os.path.join(os.getcwd(), CONFIG['event_info_file']), 'w'), indent=4)



@client.event
async def on_ready():
    print("Bot is online & awaiting commands.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    author = message.author
    author_name = author.display_name

    guild = message.guild

    try: roles = author.roles
    except: roles = []
    channel = message.channel

    message_conent = str( message.content )

    if not message_conent.startswith( PREFIX ):
        return
    
    # check which command was executed

    message_command = message_conent.split( PREFIX )[-1].strip().split(' ',1)[0]

    print(f"""\
command from user recieved:
 - USER: {author_name}
 - COMMAND: {message_command}
 - ROLES: { ', '.join( [r.name for r in roles] ) }""")


























    if message_command == 'new':
        # the new command
        # initiates a new competition

        try:
            y,z = message_conent.rsplit(' ',2)[-2:]
            announcement_message = message_conent.split('new',1)[-1].strip().split(' '.join([y,z]),1)[0]
            print(f'"new" command executed')
            print(f'y,z : {y},{z}')
            print(f"message : {announcement_message}")
            y = int(y) # [y] should be the total number of people allowed to enter the competition
            z = int(z) # [z] should be the group size
        except:
            # an error occured when trying to extract the arguments from the command
            await channel.send(f'Incorrect command syntax! Command example: ```{PREFIX} new Some Special Message 100 10```')
            return

        EVENT_DATA = loadEventData()

        if EVENT_DATA['event_running']:
            print('an event is already running. Cannot start a new one')
            await channel.send(f'''\
There is already an event running.
The current event must end before a new event can be started''')
            return
        
        group_amount = math.ceil( y/z )

        await channel.send(f'''\
```!event new command recieved!
y : {y} - total number of participants
z : {z} - group size
amount of groups : y/z : { group_amount }
message : {announcement_message}```''')

        msg = await channel.send(f'''\
Please read over the above message and confirm the information.
If you would like to continue with the event creation process,
react to this message with ✅''')

        await msg.add_reaction('✅')

        check_reactions = lambda reaction, user: ( user.id == author.id and reaction.emoji == '✅' and reaction.message.id == msg.id )
        
        valid_reaction = False

        try: await client.wait_for('reaction_add', timeout=30.0, check=check_reactions)
        except: await msg.remove_reaction('✅', client.user)
        else: valid_reaction = True

        if not valid_reaction:
            await channel.send(f'''\
Creation of event cancelled''')
            print('new event creation cancelled')
            return

        print('creating event...')

        EVENT_DATA['event_running'] = True
        dumpEventData(EVENT_DATA)

        # create channels for each of the groups in the event

        await channel.send(f'''\
Creating new text channels for each group...''')

        # group_channels = []

        group_channels_category_id = CONFIG['category_IDS']['group_channels_category']
        group_channels_category = None
        for c in guild.categories:
            if (c.id == group_channels_category_id):
                group_channels_category = c

        for group_n in range(group_amount):
            group_channel = await guild.create_text_channel( f'group{str(group_n+1)}-submissions', category=group_channels_category )
            group_channel_id = group_channel.id
            EVENT_DATA['created_channels'].append( group_channel_id )
            print(f'created channel for group {group_n+1} / {group_amount}')

        dumpEventData(EVENT_DATA)

























    if message_command == 'clean':
        # the clean command
        # cleans old roles and chats

        msg = await channel.send(f'''\
Are you sure you wish to remove event roles & channels?
react to this message with ✅ to confirm''')

        await msg.add_reaction('✅')

        check_reactions = lambda reaction, user: ( user.id == author.id and reaction.emoji == '✅' and reaction.message.id == msg.id )
        
        valid_reaction = False

        try: await client.wait_for('reaction_add', timeout=30.0, check=check_reactions)
        except: await msg.remove_reaction('✅', client.user)
        else: valid_reaction = True

        if not valid_reaction:
            return
        
        await channel.send('Removing roles & channels...')

        EVENT_DATA = loadEventData()

        for channel in guild.text_channels:
            if channel.id in EVENT_DATA['created_channels']:
                await channel.delete(reason="Removed channel")
        
        EVENT_DATA['created_channels'] = []
        EVENT_DATA['event_running'] = False
        dumpEventData(EVENT_DATA)























    if message_command == 'x':
        # the x command

        msg = await channel.send('.' + ( '\n'*40 ) + '.')





























# run the client using the token from token.txt in the same directory as the .py file
client.run( open( os.path.join(os.getcwd(), CONFIG['token_file']) ,'r').readline().strip() )