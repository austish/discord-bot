import discord
from functions import rps
import interactions
from discord import app_commands
from discord.ext import commands

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

#hello comannd
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
async def test(interaction: discord.Interaction, member: discord.Member, *, choice: discord.app_commands.Choice[int]):
    if choice.value == 0:
        await interaction.response.send_message(f'You awarded {member.mention} a player point!')    
    else:
        await interaction.response.send_message(f'You removed a player point from {member.mention}')     



# @bot.event
# async def on_message(message):
#     #if message author is the bot, do nothing
#     if message.author == bot.user:
#         return

#     username = str(message.author).split('#')[0]    #splits username at '#', [0] returns first part of split
#     user_message = str(message.content)
#     channel = str(message.channel.name)

#     #embeded message
#     if user_message[1:] == 'help':
#         em = discord.Embed(title = 'commands')
#         em.add_field(name = '!hello', value = 'hello')
#         em.add_field(name = '!roll', value = 'dice roll')
#         em.add_field(name = '!rps (choice)', value = 'play rock, paper, scissors with the bot')
#         await message.channel.send(embed = em)
#     else: 
#         await send_message(message, username, user_message[1:])

bot.run(TOKEN)