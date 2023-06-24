import discord
import random
from discord import app_commands
from discord.ext import commands

import functions
import tokens

bot = commands.Bot(command_prefix = '!', intents = discord.Intents.all(), help_command=commands.DefaultHelpCommand())
TOKEN = tokens.token

#Command Groups
class commandGroup(app_commands.Group):
    ...
randomGroup = commandGroup(name = 'random', description = "random generators")
playerListGroup = commandGroup(name = 'list', description = "manage player list")

@bot.event
async def on_ready():           #on startup
    print(f'{bot.user} is now running')
    try:
        bot.tree.add_command(randomGroup)
        bot.tree.add_command(playerListGroup)
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

@bot.tree.command(name='hello', description='Say hello to the bot')                                 #define bot command
async def hello(interaction: discord.Interaction):                                                  #define python command
    await interaction.response.send_message(f'hello {interaction.user.mention}', ephemeral=True)    #return python function

@bot.tree.command(name='help', description='get help')               
async def help(interaction: discord.Interaction):
    message = ""
    message += ":white_check_mark: **PLAYER POINTS:**\n"
    message += "   `/playerpoint` Give player points\n"
    message += "   `/check_points` Check your player points\n"
    message += "   `/leaderboard` View leaderboard\n\n"

    message += ":arrows_counterclockwise: **RANDOMIZERS:**\n"
    message += "   `/random number (num)` Gives random integer between 0 and given (num)\n"
    message += "   `/random user` Gives random user\n\n"

    message += ":1234: **TEAM GENERATOR:**\n"
    message += "   `/generate (amount)` Generate (amount) number of teams\n"
    
    message += "   > /random user and /generate pulls users from player list below\n\n"

    message += ":notepad_spiral: **PLAYER LIST:**\n"
    message += "   `/list view` View player list\n"
    message += "   `/list add` Add player to list\n"
    message += "   `/list remove` Remove player from list\n"
    message += "   `/list clear` Clear player list\n"
    message += "   `/list fill` Fill player list\n\n"

    await interaction.response.send_message(message)

###########################
###  RANDOM GENERATORS  ###
###########################

#random number generator
@randomGroup.command(name='number', description="get random number between 0 and given number")
@app_commands.describe(num = "maximum number")
async def random_num(interaction: discord.Interaction, num: int):
    num = random.randrange(0,num)
    await interaction.response.send_message(num)    

#random user generator
@randomGroup.command(name='user', description="get random user from Player List")
async def random_user(interaction: discord.Interaction):
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')
    names.pop()

    user = random.choice(names)
    await interaction.response.send_message(user) 

#######################
###  PLAYER POINTS  ###
#######################

#award/remove player points    
@bot.tree.command(name='playerpoint', description="give player points")
async def playerpoint(interaction: discord.Interaction, *, member: discord.Member, amount: float):
    functions.store_user_data(interaction.guild.id, member.id, amount)
    await interaction.response.send_message(f"{interaction.user.mention} gave {member.mention} {amount} player point(s)! They now have {functions.get_user_data(interaction.guild.id, member.id)} player points.")    
    
#check player points
@bot.tree.command(name='check_points', description="check player points")
async def check_points(interaction: discord.Interaction):
    points = functions.get_user_data(interaction.guild.id, interaction.user.id)
    await interaction.response.send_message(f'You have {points} player points.', ephemeral=True)

#player point leaderboard
@bot.tree.command(name='leaderboard', description="display playerpoint leaderboard")
async def leaderboard(interaction: discord.Interaction):
    em = discord.Embed(title = "Player Point Leaderboard")
    count = 0
    board = functions.get_leaderboard(interaction.guild.id)

    #create embed
    for i in board:
        count += 1
        user = await bot.fetch_user(i)
        em.add_field(name = (f'{count}. {user.name}'), value = (f'Points: {board[i]}'), inline=False)
    await interaction.response.send_message(embed = em)

########################
###  TEAM GENERATOR  ###
########################

#generate teams
@bot.tree.command(name='generate', description="generate teams")
@app_commands.describe(amount = "number of teams")
async def teams(interaction: discord.Interaction, amount: int):
    #get names
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')
    names.pop()

    #create teams
    random.shuffle(names)
    teams = []
    for i in range(amount):
        teams.append([])
    for count, name in enumerate(names):
        teams[count%amount].append(name)

    #create message
    message = ""
    for count, team in enumerate(teams):
        message += "Team " + str(count+1) + ": "
        for person in team:
            if person != team[-1]:
                message += person + ", "
            else:
                message += person + "\n"
    
    await interaction.response.send_message(message)

#####################
###  PLAYER LIST  ###
#####################

#helper func to create player list embed
def display_list(names):
    #create embed
    em = discord.Embed(title = "Player List")
    for i in range(len(names)-1):
        em.add_field(name = (f'{i+1}. {names[i]}'), value='', inline=False)
    
    return em

#get player list
@playerListGroup.command(name='view', description="view list of players")
async def view(interaction: discord.Interaction):
    #initialize vars
    # file = functions.check_txt_file(interaction, interaction.guild.id)
    # names = file.read().split('\n')
    
    # await interaction.response.send_message(embed = display_list(names))
    names = functions.get_list(interaction.guild.id)

    await interaction.response.send_message(embed = display_list(names))

#fill player list
@playerListGroup.command(name='fill', description="fill list of players")
async def fill(interaction: discord.Interaction):
    # initialize vars
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')
    
    #open file for appending
    file = open(f'data//{interaction.guild.id}_names.txt', 'a', encoding='utf8')
    for member in interaction.guild.members:
        if member not in names and not member.bot:
            file.write(f'{member.name}\n')
    file.truncate()

    #read file again
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')

    await interaction.response.send_message(embed = display_list(names))    

#clear list
@playerListGroup.command(name='clear', description="clear list of players")
async def clear(interaction: discord.Interaction):
    # functions.check_txt_file(interaction, interaction.guild.id)
    # open(f'data//{interaction.guild.id}_names.txt', 'w', encoding='utf8')
    functions.clear_list(interaction.guild.id)
    await interaction.response.send_message(f"Player list cleared")

#add player
@playerListGroup.command(name='add', description="add player to list")
async def add(interaction: discord.Interaction, member: discord.Member):
    #initialize vars
    # file = functions.check_txt_file(interaction, interaction.guild.id)
    # names = file.read().split('\n')

    # #check if member in list
    # if member.name in names:
    #     await interaction.response.send_message(f"{member.name} already in list")
    # else:
    #     file.close()
    #     file = open(f'data//{interaction.guild.id}_names.txt', 'a', encoding='utf8')       #reopen file to append
    #     file.write(f'{member.name}\n')                                                     #append new member
    #     await interaction.response.send_message(f"{member.name} added")
    functions.add_player(interaction.guild.id, member.name)
    await interaction.response.send_message(f"{member.name} added")

#remove player
@playerListGroup.command(name='remove', description="remove player from list")
async def remove(interaction: discord.Interaction, member: discord.Member):
    #initalize vars
    # file = functions.check_txt_file(interaction, interaction.guild.id)
    # names = file.read().split('\n')

    # #check if member in list
    # if member.name in names:
    #     #rewrite file, but do not include removed member
    #     with open(f'data//{interaction.guild.id}_names.txt', 'r', encoding='utf8') as f:
    #         lines = f.readlines()
    #     with open(f'data//{interaction.guild.id}_names.txt', 'w', encoding='utf8') as f:
    #         for line in lines:
    #             if line.strip('\n') != member.name:
    #                 f.write(line)
    #     await interaction.response.send_message(f"{member.name} removed")
    # else:
    #     await interaction.response.send_message(f"{member.name} not in list")
    functions.remove_player(interaction.guild.id, member.name)
    await interaction.response.send_message(f"{member.name} removed")

bot.run(TOKEN)