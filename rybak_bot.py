import discord
from discord.ext import commands
import random
import json
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)

DATA_FILE = 'data.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_user_data(user_id):
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {'robux': 0, 'bank': 0, 'exp': 0, 'level': 0}
        save_data(data)
    return data[user_id]

def update_user_data(user_id, user_data):
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)

def get_level_from_exp(exp):
    return exp // 100

async def assign_level_role(member, level):
    guild = member.guild
    old_roles = [role for role in member.roles if role.name.startswith("Rybak lvl")]
    for role in old_roles:
        await member.remove_roles(role)
    role_name = f"Rybak lvl {level}"
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        role = await guild.create_role(name=role_name)
    await member.add_roles(role)

@bot.event
async def on_ready():
    print(f'Zalogowano jako {bot.user}')

@bot.command()
async def bal(ctx):
    user_data = get_user_data(ctx.author.id)
    await ctx.send(f"{ctx.author.mention}, masz {user_data['robux']} Robuxów w portfelu i {user_data['bank']} w banku.")

@bot.command()
async def bank(ctx, operacja: str, kwota: int):
    user_data = get_user_data(ctx.author.id)
    if operacja == "wplac":
        if user_data['robux'] >= kwota:
            user_data['robux'] -= kwota
            user_data['bank'] += kwota
            await ctx.send(f"Wpłacono {kwota} Robuxów do banku.")
        else:
            await ctx.send("Nie masz tyle Robuxów.")
    elif operacja == "wyplac":
        if user_data['bank'] >= kwota:
            user_data['bank'] -= kwota
            user_data['robux'] += kwota
            await ctx.send(f"Wypłacono {kwota} Robuxów z banku.")
        else:
            await ctx.send("Nie masz tyle w banku.")
    update_user_data(ctx.author.id, user_data)

@bot.command()
@commands.cooldown(1, 20, commands.BucketType.user)
async def lowienie(ctx):
    ryby = [
        ("Płotka", 0.5, (10, 30)),
        ("Szczupak", 0.3, (30, 60)),
        ("Łosoś", 0.15, (60, 100)),
        ("Rekin", 0.04, (100, 250)),
        ("Megalodon", 0.01, (500, 1000)),
    ]
    r = random.random()
    suma = 0
    for nazwa, szansa, (min_r, max_r) in ryby:
        suma += szansa
        if r <= suma:
            nagroda = random.randint(min_r, max_r)
            user_data = get_user_data(ctx.author.id)
            user_data['robux'] += nagroda
            user_data['exp'] += 5
            new_level = get_level_from_exp(user_data['exp'])
            if new_level > user_data['level']:
                user_data['level'] = new_level
                await assign_level_role(ctx.author, new_level)
                await ctx.send(f"{ctx.author.mention} awansował na poziom {new_level}!")
            update_user_data(ctx.author.id, user_data)
            await ctx.send(f"{ctx.author.mention} złowił: **{nazwa}** i zarobił {nagroda} Robuxów!")
            return
    await ctx.send(f"{ctx.author.mention} nic nie złowił!")

@bot.command()
async def lvl(ctx):
    user_data = get_user_data(ctx.author.id)
    await ctx.send(f"{ctx.author.mention}, masz {user_data['exp']} EXP i jesteś na poziomie {user_data['level']}.")

import os
bot.run(os.getenv("DISCORD_TOKEN"))
