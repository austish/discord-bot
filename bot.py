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
    message += ":white_check_mark:**PLAYER POINTS:**\n"
    message += "`/playerpoint` Give player points\n"
    message += "`/check_points` Check your player points\n"
    message += "`/leaderboard` View leaderboard\n\n"
    
    message += ":basketball_player:**PLAYER LIST:**\n"
    message += "`/view` View player list\n"
    message += "`/add` Add player to list\n"
    message += "`/remove` Remove player from list\n"
    message += "`/clear` Clear player list\n\n"
    
    # embed = discord.Embed(title = '```Commands```', description='Player points and team generator', color=0x3aa1e8)

    # embed.add_field(name='```Team Generator:```', value='', inline=False)
    # embed.add_field(name='/add', value='add player to list', inline=True)
    # embed.add_field(name='/remove', value='remove player from list', inline=True)
    # embed.add_field(name='/view', value='view player list', inline=True)
    # embed.add_field(name='/clear', value='clears player list', inline=True)
    # embed.add_field(name='/generate', value='generates teams', inline=True)
    await interaction.response.send_message(message)


###########################
###  RANDOM GENERATORS  ###
###########################

#random number generator
@randomGroup.command(name='number', description="get random number between 0 and given number")
async def random_num(interaction: discord.Interaction, number: int):
    num = random.randrange(0,number)
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
async def test(interaction: discord.Interaction, *, member: discord.Member, amount: float):
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
@app_commands.describe(amount = "amount of teams")
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

    #create embed
    em = discord.Embed(title = 'Teams')
    for count, team in enumerate(teams):
        message = ''
        for person in team:
            if person != team[-1]:
                message += person + ', '
            else:
                message += person
        em.add_field(name = f'Team {count+1}:', value = message)

    await interaction.response.send_message(embed = em)

#####################
###  PLAYER LIST  ###
#####################

#get player list
@playerListGroup.command(name='view', description="view list of players")
async def view(interaction: discord.Interaction):
    #initialize vars
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')

    #create embed
    count = 0
    em = discord.Embed(title = "Player List")
    for i in range(len(names)-1):
        count += 1
        em.add_field(name = (f'{count}. {names[i]}'), value='', inline=False)
    
    await interaction.response.send_message(embed = em)

#clear list
@playerListGroup.command(name='clear', description="clear list of players")
async def clear(interaction: discord.Interaction):
    functions.check_txt_file(interaction, interaction.guild.id)
    open(f'data//{interaction.guild.id}_names.txt', 'w', encoding='utf8')
    await interaction.response.send_message(f"Player list cleared")

#add player
@playerListGroup.command(name='add', description="add player to list")
async def add(interaction: discord.Interaction, member: discord.Member):
    #initialize vars
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')

    #check if member in list
    if member.name in names:
        await interaction.response.send_message(f"{member.name} already in list")
    else:
        file.close()
        file = open(f'data//{interaction.guild.id}_names.txt', 'a', encoding='utf8')       #reopen file to append
        file.write(f'{member.name}\n')                                                      #append new member
        await interaction.response.send_message(f"{member.name} added")

#remove player
@playerListGroup.command(name='remove', description="remove player from list")
async def remove(interaction: discord.Interaction, member: discord.Member):
    #initalize vars
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')

    #check if member in list
    if member.name in names:
        #rewrite file, but do not include removed member
        with open(f'data//{interaction.guild.id}_names.txt', 'r', encoding='utf8') as f:
            lines = f.readlines()
        with open(f'data//{interaction.guild.id}_names.txt', 'w', encoding='utf8') as f:
            for line in lines:
                if line.strip('\n') != member.name:
                    f.write(line)
        await interaction.response.send_message(f"{member.name} removed")
    else:
        await interaction.response.send_message(f"{member.name} not in list")

bot.run(TOKEN)