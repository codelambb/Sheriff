import discord
from discord.ext import commands, tasks
import os
from random import choice
import aiohttp
from random import randint
import time
import datetime
import asyncio
import random
import typing
import PIL

from PIL import Image
from io import BytesIO

intents = discord.Intents.all()
prefixes = ["!"]
client = commands.Bot(command_prefix=prefixes, intents=intents)

status = ['Listening to !help', 'Make sure to read the rules!']

client.remove_command("help")

filter_words = ["fuck","bitch","pussy","chutiya","sala","arse","dick"]

#start
@client.event
async def on_ready():
	change_status.start()
	print('Bot is ready.')

#status change
@tasks.loop(seconds=20)
async def change_status():
	await client.change_presence(activity=discord.Game(choice(status)))

#ping command
@client.command()
async def ping(ctx):
	await ctx.send(f'Pong! {round(client.latency * 1000)}ms')

#8ball command
@client.command(aliases=['8ball'])
async def _8ball(ctx, question):
	import random
	responses = ["It is certain.",
				"It is decidedly so.",
				"Without a doubt.",
				"Yes - definitely.",
				"You may rely on it.",
				"As I see it, yes.",
				"Most likely.",
				"Outlook good.",
				"Yes.",
				"Signs point to yes.",
				"Reply hazy, try again.",
				"Ask again later.",
				"Better not tell you now.",
				"Cannot predict now.",
				"Concentrate and ask again.",
				"Don't count on it.",
				"My reply is no.",
				"My sources say no.",
				"Outlook not so good.",
				"Very doubtful."]
	await ctx.send(f'{random.choice(responses)}')

#help command
@client.command(aliases=['h'])
async def help(ctx):
	helpEmbed = discord.Embed(tittle="Help Menu", color=ctx.author.color)
	helpEmbed.set_author(name="Help Menu:\nPrefix = '!'")
	helpEmbed.add_field(name="Moderation Command Menu", value="```Type !modhelp to open that```", inline=True)
	helpEmbed.add_field(name="Miscellaneous Command Menu", value="```Type !mischelp to open that```", inline=True)

	await ctx.send(embed=helpEmbed)

#modHelp
@client.command()
async def modhelp(ctx):
	mod = discord.Embed(tittle="mod", color=ctx.author.color)
	mod.add_field(name="Moderation Command Menu", value="```!clear (ammount) : Deletes the specified ammount of messages from the channel```\n```!ban (user) (reasion) : Bans the specified user from the server```\n```!kick (user) (reason) : Kicks the specified user from the server```\n```!mute (user) (time) (reason) : Mutes the specified user from the server```\n```!unmute (user) : Unmutes the specified user```\n```!announce (message) : Makes an announcemnt with sylish embed style```\n```!addrole (user) (role) : Adds the specifieed role to specified user```\n```!removerole : Removes the specified role from the specified user```\n")
	mod.set_footer(text="More moderation commands will be added soon")
	await ctx.send(embed=mod)

#miscHelp
@client.command()
async def mischelp(ctx):
	misc = discord.Embed(tittle="misc", color=ctx.author.color)
	misc.add_field(name="Miscellaneous Command Menu", value="```!ping : Tells the bot's latency```\n```!8ball (question) : Tells the answer of the asked question in a random yes/no answer```\n```!meme : Send a hot meme from reddit```\n```!serverinfo : Send info about server```\n```!userinfo (user) : Send info about specified user```\n```!eval : For doing fast calculations!```\n")
	misc.set_footer(text="More miscellaneous commands will be added soon")
	await ctx.send(embed=misc)

#ban command
@client.command(aliases=['b'])
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
	await ctx.send(f'Banned {member} from the server. BOOM!')
	await member.ban(reason=reason)

#kick command
@client.command(aliases=['k'])
@commands.has_permissions(kick_members=True, administrator=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
	await ctx.send(f'Kicked {member} from the server.')
	await member.kick(reason=reason)


#clear command
@client.command(aliases=["cls", "purge"])
@commands.has_permissions(manage_messages=True, administrator=True)
async def clear(ctx, ammount: int = None):
	if ammount == None:
		em = discord.Embed(
			title=":negative_squared_cross_mark: Please specify the amount of message to be cleared!",
			color=discord.Color.red())
		await ctx.send(embed=em)
		return

	if ammount == 0:
		em = discord.Embed(
			title=":negative_squared_cross_mark: You can't clear 0 messages?! Please specify the amount of messages above 0 and below or equal to 100",
			color=discord.Color.red())
		await ctx.send(embed=em)

	if ammount > 100:
		em = discord.Embed(title=":negative_squared_cross_mark: 100 is the limit of clearing messages at one time",
						   color=discord.Color.red())
		await ctx.send(embed=em)
		return

	await ctx.channel.purge(limit=ammount + 1)
	em = discord.Embed(title=f":white_check_mark: Successfully purged {ammount} messages\n\n\n",
					   color=discord.Color.green())
	await ctx.send(embed=em, delete_after=5)
	return


#tieup command
@client.command()
@commands.has_permissions(manage_roles=True, administrator=True)
async def tieup(ctx, member: discord.Member = None, mute_time=None, *, reason="No reason provided"):
	if member == None:
		em = discord.Embed(
			title=":negative_squared_cross_mark: Who do you want me to tieup?! Please mention someone next time",
			color=discord.Color.red())
		await ctx.send(embed=em)
		return

	if member == ctx.author:
		em = discord.Embed(title=":negative_squared_cross_mark: You can't tieup yourself!",
						   color=discord.Color.red())
		await ctx.send(embed=em)
		return

	if member.top_role >= ctx.author.top_role:
		em = discord.Embed(
			title=":negative_squared_cross_mark: You can't tieup that user cause that user is same or higher than you!",
			color=discord.Color.red())
		await ctx.send(embed=em)
		return

	if mute_time == None:
		mute_time = "permenantely"

	if mute_time[-1] != 's' and mute_time[-1] != 'm' and mute_time[-1] != 'h' and mute_time[
		-1] != 'd' and mute_time != "permenantely":
		em = discord.Embed(
			title=":negative_squared_cross_mark: You need to have your last digit as `s/m/h/d` for example 5h",
			color=discord.Color.red())
		await ctx.send(embed=em)
		return

	role = discord.utils.get(ctx.guild.roles, name="Muted")

	if not role:
		await ctx.guild.create_role(name='Muted')

		for channel in ctx.guild.channels:
			await channel.set_permissions(role, speak=False, send_messages=False, read_message_history=True,
										  read_messages=True)

	if role in member.roles:
		em = discord.Embed(title=":negative_squared_cross_mark: That user is already muted!",
						   color=discord.Color.red())
		await ctx.send(embed=em)
		return

	if member.bot == True:
		await member.add_roles(role)
		em = discord.Embed(title=":white_check_mark: Successfully done!\n\n\n",
						   description=f"Tied up <@!{member.id}>\n\nTieup Time : `{mute_time}`\n\nReason : `{reason}`\n\tTied up By : <@!{ctx.author.id}>",
						   color=discord.Color.green())
		em.set_image(url="https://media4.giphy.com/media/d8toQWZ6oDgTR9AQ3P/giphy.gif")
		await ctx.send(embed=em)

		if mute_time != "permenantely":
			if mute_time[-1] == 's':
				x = int(mute_time[:-1])

			if mute_time == 'm':
				x = int(mute_time[:-1]) * 60

			if mute_time == 'h':
				x = int(mute_time[:-1]) * 3600

			if mute_time == 'd':
				x = int(mute_time[:-1]) * 86400

			await asyncio.sleep(x)
			await member.remove_roles(role)
			await ctx.send(f"Unmuted {member.mention} because time is up")

	else:
		await member.add_roles(role)
		em = discord.Embed(title=":white_check_mark: Successfully done!\n\n\n",
						   description=f"Tied up  <@!{member.id}>\n\nTieup Time : `{mute_time}`\n\nReason : `{reason}`\n\nTied up by : <@!{ctx.author.id}>",
						   color=discord.Color.green())
		em.set_image(url="https://media4.giphy.com/media/d8toQWZ6oDgTR9AQ3P/giphy.gif")
		await ctx.send(embed=em)
		await member.send(f"You have been muted in {ctx.author.guild.name}\n\nMuted by : <@!{ctx.author.id}>\n\nMute Time : {mute_time}\n\nReason : {reason}")

		if mute_time != "permenantely":
			if mute_time[-1] == 's':
				x = int(mute_time[:-1])

			if mute_time == 'm':
				x = int(mute_time[:-1]) * 60

			if mute_time == 'h':
				x = int(mute_time[:-1]) * 3600

			if mute_time == 'd':
				x = int(mute_time[:-1]) * 86400

			await asyncio.sleep(x)
			await member.remove_roles(role)
			await ctx.send(f"Unmuted {member.mention} because time is up")

#untie command
@client.command()
@commands.has_permissions(manage_roles=True, administrator=True)
async def untie(ctx, *, user: discord.Member = None):

    if user == None:
        em = discord.Embed(title=":negative_squared_cross_mark: Who do you want to unmute!? Please mention someone next time", color=discord.Color.red())
        await ctx.send(embed=em)
        return

    rolename = discord.utils.get(ctx.guild.roles, name="Muted")

    if rolename not in user.roles:
        em = discord.Embed(title=":negative_squared_cross_mark: That user is not muted!", color=discord.Color.red())
        await ctx.send(embed=em)
        return

    else:
        await user.remove_roles(rolename)
        em = discord.Embed(title=":white_check_mark: Successfully done!", color=discord.Color.green())
        await ctx.send(embed=em)



#meme command
@client.command()
async def meme(ctx):
    async with aiohttp.ClientSession() as cs:
        async with cs.get ('https://www.reddit.com/r/dankmemes/new.json?sort=hot') as r:
            res = await r.json()
            embed = discord.Embed(title = "Memes", color = discord.Color.orange())
            embed.set_image(url=res['data']['children'] [random.randint(0, 25)]['data']['url'])
            await ctx.send(embed=embed)

#kill command
@client.command()
async def kill(ctx, user):
	k = random.randint(0,5)
	if k == 0:
		await ctx.send(f'You challenged {user} to a fist fight to the death. You won.')
	if k == 2:
		await ctx.send(f'{user} had a mid air collision with nyan-cat')
	if k == 3:
		await ctx.send(f'{user} fell down a cliff while playing Pokemon Go. Good job on keeping your nose in that puny phone. :iphone:')
	if k == 4:
		await ctx.send(f"{user} presses a random button and is teleported to the height of 100m, allowing them to fall to their inevitable death.\nMoral of the story: Don't go around pressing random buttons.")
	if k == 5:
		await ctx.send(f'{user} is sucked into Minecraft. {user}, being a noob at the so called Real-Life Minecraft faces the Game Over screen.')



#announcemnt command
@client.command(aliases=["ann"])
@commands.has_permissions(administrator=True, manage_messages=True, manage_roles=True, ban_members=True, kick_members=True)
async def announce(ctx,*,message):
	anno = discord.Embed(tittle="ann", color=ctx.author.color)
	anno.add_field(name="Announcement", value=message)
	anno.set_footer(text=f"Announcement by {ctx.author.name}")
	await ctx.channel.purge(limit=1)
	await ctx.send(embed=anno)
	await ctx.send("@Announcements", delete_after=3)

#on_message events
@client.event
async def on_message(msg):
  for word in filter_words:
    if word in msg.content:
      await msg.delete()
      await msg.channel.send(f"{msg.author.mention}, Swearing is not allowed in this server")

  await client.process_commands(msg)

#server info command
@client.command(aliases=['si'])
async def serverinfo(ctx):
  guild=ctx.guild

  em=discord.Embed(title=f"{guild.name} info", color=ctx.author.color)
  em.set_footer(text=f'Requested by {ctx.author.name}')
  em.add_field(name='Total members', value=f"{guild.member_count}")
  em.add_field(name="Owner", value=f"<@!{guild.owner.id}>")
  em.add_field(name="Server created on:", value=guild.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

  await ctx.send(embed=em)

#userinfo command
@client.command(aliases=["ui"])
async def userinfo(ctx, member: discord.Member):

  em=discord.Embed(color=member.color)

  em.set_author(name=f"{member.name}'s info")
  em.set_thumbnail(url=member.avatar_url)
  em.set_footer(text=f"Requested by {ctx.author.name}")

  em.add_field(name='Member Name', value=member.name)
  em.add_field(name="Member name in guild", value=member.display_name)

  em.add_field(name="Joined at:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"))

  await ctx.send(embed=em)

#suggest command
@client.command()
async def suggest(ctx, *, message):
  em=discord.Embed(title="Suggestion", description=message,color=ctx.author.color)
  em.set_footer(text=f"Suggestion by {ctx.author.name}")
  channel = client.get_channel(807285866689986580)
  message_ = await channel.send(embed=em)
  await message_.add_reaction("✅")
  await message_.add_reaction("❎")
  await ctx.send(f"Successfully sent your suggestion to the staff!")

#addrole command
@client.command(aliases=["a"])
@commands.has_permissions(manage_roles=True, administrator=True)
async def addrole(ctx, role: discord.Role, user: discord.Member):
	Role = discord.utils.get(ctx.guild.roles, name=role)
	await user.add_roles(Role)
	await ctx.send(f'Successfully Done')

#removerole command
@client.command(aliases=["r"])
@commands.has_permissions(manage_roles=True, administrator=True)
async def removerole(ctx, role: discord.Role, user: discord.Member):
	Role = discord.utils.get(ctx.guild.roles, name=role)
	await user.remove_roles(Role)
	await ctx.send(f'Successfully Done')

#member join log
@client.event
async def on_member_join(member):
	channel = client.get_channel(807287331388129320)
	await channel.send(f'{member.mention} has joined the server')

#avatar command
@client.command()
async def avatar(ctx, member: discord.Member):
	await ctx.send(member.avatar_url)


#wanted command
@client.command()
async def wanted(ctx, *, user: discord.Member = None):
	if user == None:
		user = ctx.author

	wanted = Image.open("wanted.jpg")

	asset = user.avatar_url_as(size=128)
	data = BytesIO(await asset.read())
	pfp = Image.open(data)

	pfp = pfp.resize((357, 280))

	wanted.paste(pfp, (58, 232))
	wanted.save("wan.jpg")

	await ctx.send(file=discord.File("wan.jpg"))

#all the errors

#userinfo error
@userinfo.error
async def userinfo_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):

        em = discord.Embed(title = "Error", description = "Please pass all required arguments", color = discord.Color.red())

        await ctx.send(embed=em, delete_after=5)

#suggest error
@suggest.error
async def suggest_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        em=discord.Embed(title="Error", description="Please specify a suggestion message you want to use", color=discord.Color.red())
        await ctx.send(embed=em, delete_after=5)


client.run(os.environ['Token'])