import discord
import random
from discord import app_commands
from discord.ext import commands

import functions
import tokens

bot = commands.Bot(command_prefix = '!', intents = discord.Intents.all())
# TOKEN = tokens.token
TOKEN = tokens.test_token

@bot.event
async def on_ready():           #on startup
    print(f'{bot.user} is now running')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

#hello command
@bot.tree.command(name='hello', description='Say hello to the bot')                             #define bot command
async def hello(interaction: discord.Interaction):                                              #define python command
    await interaction.response.send_message(f'hello {interaction.user.mention}')                #return python function

#rps command
# @bot.tree.command(name='rps', description='Play rock, paper, scissors with the bot')
# @app_commands.describe(choice = 'rock, paper, or scissors')
# @app_commands.choices(choice = [
#     discord.app_commands.Choice(name = 'Rock', value = 1),
#     discord.app_commands.Choice(name = 'Paper', value = 2),
#     discord.app_commands.Choice(name = 'Scissors', value = 3),
# ])
# async def r_p_s(interaction: discord.Interaction, choice: discord.app_commands.Choice[int]):    
#     result = f'You selected: `{choice.name}` \n{functions.rps(choice.name.lower())}'
#     await interaction.response.send_message(result)                                             

########################
###  PLAYER POINTS  ###
########################

#award/remove player points
@bot.tree.command(name='playerpoint', description='Award/remove player points')
@app_commands.describe(choice = 'reward or penalize')
@app_commands.choices(choice = [
    discord.app_commands.Choice(name = 'Award', value = 0),
    discord.app_commands.Choice(name = 'Remove', value = 1)
])
async def test(interaction: discord.Interaction, *, choice: discord.app_commands.Choice[int], member: discord.Member, amount: int):
    value = abs(amount)
    if choice.value == 0:
        functions.store_user_data(interaction.guild.id, member.id, value)
        await interaction.response.send_message(f'{interaction.user.mention} awarded {member.mention} {value} player point(s)! They now have {functions.get_user_data(interaction.guild.id, member.id)} player points.')    
    else:
        functions.store_user_data(interaction.guild.id, member.id, -value)
        await interaction.response.send_message(f'{interaction.user.mention} removed {value} player point(s) from {member.mention}. They now have {functions.get_user_data(interaction.guild.id, member.id)} player points.')     

#check player points
@bot.tree.command(name='check_points', description='check player points')
async def check_points(interaction: discord.Interaction):
    points = functions.get_user_data(interaction.guild.id, interaction.user.id)
    await interaction.response.send_message(f'You have {points} player points.', ephemeral=True)

#player point leaderboard
@bot.tree.command(name='leaderboard', description='display playerpoint leaderboard')
async def leaderboard(interaction: discord.Interaction):
    em = discord.Embed(title = 'Player Point Leaderboard')
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
@bot.tree.command(name="generate", description='generate teams')
async def teams(interaction: discord.Interaction):
    #get names
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')
    names.pop()

    #create teams
    random.shuffle(names)
    team1 = names[:len(names)//2]
    team2 = names[len(names)//2:]
    await interaction.response.send_message(f"Team 1: {', '.join(team1)}\nTeam 2: {', '.join(team2)}")

#get player list
@bot.tree.command(name="playerlist", description='get list of players')
async def list(interaction: discord.Interaction):
    #initialize vars
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')

    #create embed
    count = 0
    em = discord.Embed(title = 'Player List')
    for i in range(len(names)-1):
        count += 1
        em.add_field(name = (f'{count}. {names[i]}'), value=(f"Rating: "), inline=False)
    
    await interaction.response.send_message(embed = em)

#clear list
@bot.tree.command(name="clear_list", description='clear list of players')
async def clear(interaction: discord.Interaction):
    functions.check_txt_file(interaction, interaction.guild.id)
    open(f'data\\{interaction.guild.id}_names.txt', 'w', encoding="utf8")
    await interaction.response.send_message(f"Player list cleared")

#add player
@bot.tree.command(name="add_player", description='generate teams')
async def add(interaction: discord.Interaction, member: discord.Member):
    #initialize vars
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')

    #check if member in list
    if member.name in names:
        await interaction.response.send_message(f"{member.name} already in list")
    else:
        file.close()
        file = open(f'data\\{interaction.guild.id}_names.txt', 'a', encoding="utf8")       #reopen file to append
        file.write(f'{member.name}\n')                                                      #append new member
        await interaction.response.send_message(f"{member.name} added")

#remove player
@bot.tree.command(name="remove_player", description='generate teams')
async def remove(interaction: discord.Interaction, member: discord.Member):
    #initalize vars
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')

    #check if member in list
    if member.name in names:
        #rewrite file, but do not include removed member
        with open(f"data\\{interaction.guild.id}_names.txt", "r", encoding="utf8") as f:
            lines = f.readlines()
        with open(f"data\\{interaction.guild.id}_names.txt", "w", encoding="utf8") as f:
            for line in lines:
                if line.strip("\n") != member.name:
                    f.write(line)
        await interaction.response.send_message(f"{member.name} removed")
    else:
        await interaction.response.send_message(f"{member.name} not in list")

bot.run(TOKEN)