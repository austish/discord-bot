import discord
import json
from discord import app_commands
from discord.ext import commands

from functions import rps
from functions import store_user_data
from functions import get_user_data
from functions import get_leaderboard

bot = commands.Bot(command_prefix = '!', intents = discord.Intents.all())
TOKEN = 'MTA0MDg3NzA0MDM1OTk4MTA5Ng.GPmMVh.9C_oN9zDzAxGN9TiqyEnSfXdjOgi3Fnw8PcbpI'

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
@bot.tree.command(name='rps', description='Play rock, paper, scissors with the bot')
@app_commands.describe(choice = 'rock, paper, or scissors')
@app_commands.choices(choice = [
    discord.app_commands.Choice(name = 'Rock', value = 1),
    discord.app_commands.Choice(name = 'Paper', value = 2),
    discord.app_commands.Choice(name = 'Scissors', value = 3),
])
async def r_p_s(interaction: discord.Interaction, choice: discord.app_commands.Choice[int]):    
    result = f'You selected: `{choice.name}` \n{rps(choice.name.lower())}'
    await interaction.response.send_message(result)                                             


#player points command
@bot.tree.command(name='playerpoint', description='Award/remove player points')
@app_commands.describe(choice = 'reward or penalize')
@app_commands.choices(choice = [
    discord.app_commands.Choice(name = 'Award', value = 0),
    discord.app_commands.Choice(name = 'Remove', value = 1),
])
async def test(interaction: discord.Interaction, *, choice: discord.app_commands.Choice[int], member: discord.Member, amount: int):
    value = abs(amount)
    if choice.value == 0:
        store_user_data(interaction.guild.id, member.id, value)
        await interaction.response.send_message(f'{interaction.user.mention} awarded {member.mention} {value} player point(s)! They now have {get_user_data(interaction.guild.id, member.id)} player points.')    
    else:
        store_user_data(interaction.guild.id, member.id, -value)
        await interaction.response.send_message(f'{interaction.user.mention} removed {value} player point(s) from {member.mention}. They now have {get_user_data(interaction.guild.id, member.id)} player points.')     


#check player points
@bot.tree.command(name='check_points', description='check player points')
async def check_points(interaction: discord.Interaction):
    points = get_user_data(interaction.guild.id, interaction.user.id)
    await interaction.response.send_message(f'You have {points} player points.')


#player point leaderboard
@bot.tree.command(name='leaderboard', description='display playerpoint leaderboard')
async def leaderboard(interaction: discord.Interaction):
    em = discord.Embed(title = 'Player Point Leaderboard')
    count = 0
    board = get_leaderboard(interaction.guild.id)
    for i in board:
        count += 1
        user = await bot.fetch_user(i)
        em.add_field(name = (f'{count}. {user.name}'), value = (f'Points: {board[i]}'), inline=False)
    await interaction.response.send_message(embed = em)

bot.run(TOKEN)