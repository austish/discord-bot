import discord
import random
from discord import app_commands
from discord.ext import commands

import functions
import tokens

bot = commands.Bot(command_prefix = '!', intents = discord.Intents.all(), help_command=commands.DefaultHelpCommand())
TOKEN = tokens.token

@bot.event
async def on_ready():           #on startup
    print(f'{bot.user} is now running')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(e)

#hello command
@bot.tree.command(name='hello', description='Say hello to the bot')                                 #define bot command
async def hello(interaction: discord.Interaction):                                                  #define python command
    await interaction.response.send_message(f'hello {interaction.user.mention}', ephemeral=True)    #return python function

@bot.tree.command(name='help', description='get help')               
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title = "```Commands```", description=" Player points and team generator", color=0x3aa1e8)
    embed.add_field(name="```Player Points:```", value="", inline=False)
    embed.add_field(name="/playerpoint", value="give player points", inline=True)
    embed.add_field(name="/checkpoints", value="check your points", inline=True)
    embed.add_field(name="/leaderboard", value="displays leaderboard", inline=True)
    embed.add_field(name="```Team Generator:```", value="", inline=False)
    embed.add_field(name="/add_player", value="add player to list", inline=True)
    embed.add_field(name="/remove_player", value="remove player from list", inline=True)
    embed.add_field(name="/list", value="check player list", inline=True)
    embed.add_field(name="/clear_list", value="clears player list", inline=True)
    embed.add_field(name="/generate", value="generates teams", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)

                                       
########################
###  PLAYER POINTS  ###
########################

#award/remove player points
@bot.tree.command(name='playerpoint', description='Give player points')
async def test(interaction: discord.Interaction, *, member: discord.Member, amount: float):
    functions.store_user_data(interaction.guild.id, member.id, amount)
    await interaction.response.send_message(f'{interaction.user.mention} gave {member.mention} {amount} player point(s)! They now have {functions.get_user_data(interaction.guild.id, member.id)} player points.')    
    
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
@app_commands.describe(amount = 'amount of teams')
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
        message = ""
        for person in team:
            if person != team[-1]:
                message += person + ", "
            else:
                message += person
        em.add_field(name = f'Team {count+1}:', value = message)

    await interaction.response.send_message(embed = em)

#get player list
@bot.tree.command(name="list", description='get list of players')
async def list(interaction: discord.Interaction):
    #initialize vars
    file = functions.check_txt_file(interaction, interaction.guild.id)
    names = file.read().split('\n')

    #create embed
    count = 0
    em = discord.Embed(title = 'Player List')
    for i in range(len(names)-1):
        count += 1
        em.add_field(name = (f'{count}. {names[i]}'), value="", inline=False)
    
    await interaction.response.send_message(embed = em)

#clear list
@bot.tree.command(name="clear_list", description='clear list of players')
async def clear(interaction: discord.Interaction):
    functions.check_txt_file(interaction, interaction.guild.id)
    open(f'data//{interaction.guild.id}_names.txt', 'w', encoding="utf8")
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
        file = open(f'data//{interaction.guild.id}_names.txt', 'a', encoding="utf8")       #reopen file to append
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
        with open(f"data//{interaction.guild.id}_names.txt", "r", encoding="utf8") as f:
            lines = f.readlines()
        with open(f"data//{interaction.guild.id}_names.txt", "w", encoding="utf8") as f:
            for line in lines:
                if line.strip("\n") != member.name:
                    f.write(line)
        await interaction.response.send_message(f"{member.name} removed")
    else:
        await interaction.response.send_message(f"{member.name} not in list")

bot.run(TOKEN)