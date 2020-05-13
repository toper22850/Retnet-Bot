import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl
import os

client = commands.Bot( command_prefix = '!' )
client.remove_command( 'help' )

@client.event

#Сообщение о подключении бота на сервер

async def on_ready ():
	print (' BOT connected ')

	await client.change_presence( status = discord.Status.online, activity = discord.Game( '!help' ) )

#!hello

@client.command( pass_context = True )

async def hello ( ctx ):
	author = ctx.message.author

	await ctx.send(f' { author.mention } Привееет! Чтобы ты быстрее освоился на нашем уютном сервере - рекомендую перейти на канал <#694563431767867422>')

#!clear

@client.command ( pass_context = True )
@commands.has_permissions ( administrator = True )

async def clear ( ctx, amount : int ):
	await ctx.channel.purge ( limit = amount )


#!kick(embed)

@client.command ( pass_context = True )
@commands.has_permissions ( administrator = True )

async def kick ( ctx, member: discord.Member , *, reason = None):
    await ctx.channel.purge( limit = 1 )

    await member.kick ( reason = reason )

    emb = discord.Embed( title = 'Кик', colour = discord.Color.red() )

    emb.set_author ( name = member.name, icon_url = member.avatar_url )
    emb.set_footer( text = 'Был кикнут администратором {}'.format ( ctx.author.name ), icon_url = ctx.author.avatar_url )

    await ctx.send( embed = emb )




#!ban(embed)

@client.command( pass_context = True )
@commands.has_permissions ( administrator = True )

async def ban ( ctx, member: discord.Member, *, reason  = None ):
	emb = discord.Embed( title = 'Бан', colour = discord.Color.red() )

	await ctx.channel.purge ( limit = 1 )

	await member.ban( reason = reason )

	emb.set_author ( name = member.name, icon_url = member.avatar_url )
	emb.set_footer( text = 'Был забанен администратором {}'.format ( ctx.author.name ), icon_url = ctx.author.avatar_url )

	await ctx.send( embed = emb )

	await ctx.send ( f' { member.mention } был забанен на нашем сервере. ' )

#!unban(embed)

@client.command( pass_context = True )
@commands.has_permissions ( administrator = True )

async def unban ( ctx, *, member ):
	emb = discord.Embed( title = 'Разбан', colour = discord.Color.green() )
	await ctx.channel.purge( limit = 1 )

	emb.set_author ( name = member.name, icon_url = member.avatar_url )
	emb.set_footer( text = 'Был разбанен администратором {}'.format ( ctx.author.name ), icon_url = ctx.author.avatar_url )

	await ctx.send( embed = emb )

	banned_users = await ctx.guild.bans ()

	for ban_entry in banned_users:
		user = ban_entry.user

		await ctx.guild.unban ( user )
		await ctx.send ( f'{ user.mention } был разбанен на нашем сервере.' )

		return

#!help(embed)

@client.command()

async def help ( ctx ):
	emb = discord.Embed( title = 'Все мои команды ты сможешь найти в канале с командами :3', colour = discord.Color.purple() )

	emb.set_footer( text = 'Я многое могу :3')

	await ctx.send( embed = emb )


#!mute(embed)

@client.command()
@commands.has_permissions ( administrator = True )

async def mute ( ctx, member:discord.Member ):
	await ctx.channel.purge( limit = 1 )

	mute_role = discord.utils.get( ctx.message.guild.roles, name = 'R-Muted' )

	await member.add_roles ( mute_role )

	emb = discord.Embed( title = 'Мьют', colour = discord.Color.red() )

	emb.set_author ( name = member.name, icon_url = member.avatar_url )
	emb.set_footer( text = 'Был замьючен администратором {}'.format ( ctx.author.name ), icon_url = ctx.author.avatar_url )

	await ctx.send( embed = emb )


#Ошибки консоли

@client.event 
async def on_command_error( ctx, error ):
	pass
@clear.error
async def clear_error ( ctx, error ):
    if isinstance ( error, commands.MissingRequiredArgument ):
	    await ctx.send ( f'{ ctx.author.name }, укажите значение.' )

    if isinstance ( error, commands.MissingPermissions ):
	    await ctx.send (f'{ ctx.author.name }, у Вас недостаточно прав.')

#!join

@client.command()
async def join ( ctx ):
	global voice 
	channel = ctx.message.author.voice.channel
	voice = get( client.voice_clients, guild = ctx.guild )

	if voice and voice.is_connected():
		await voice.move_to( channel )
	else:
		voice = await channel.connect()
		await ctx.send(f'Бот присоединился к каналу : {channel.mention}') 

#!leave

@client.command()
async def leave ( ctx ):
	channel = ctx.message.author.voice.channel
	voice = get( client.voice_clients, guild = ctx.guild )

	if voice and voice.is_connected():
		await voice.disconnect()
	else:
		voice = await channel.connect()
		await ctx.send(f'Бот отключился от канала : {channel.mention}') 


#!play

@client.command()
async def play ( ctx, url : str ):
	song_there = os.path.isfile('song.mp3')

	try:
		if song_there:
			os.remove('song.mp3')
			print ( '[log] Старый файл удалён.' )
	except PermissionError:
		print( '[log] Не удалось удалить файл' )

	await ctx.send( 'Пожалуйста ожидайте..' )

	voice = get(client.voice_clients, guild = ctx.guild)

	ydl_opts = {
        ' format ' : ' bestaudio/best ',
        ' postprocessors ' : [{
        	'key' : 'FFmpegExtractAudio',
        	'preferredcodec' : 'mp3',
        	'preferredquality' : '192'
        }],	   
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl :
		print(' [log] Загружаю музыку.. ')
		ydl.download([url])

	for file in os.listdir('./'):
		if file.endswith('.mp3'):
			name = file
			print( f'[log] Переименовываю файл : {file}' )
			os.rename(file, 'song.mp3')

	voice.play(discord.FFmpegPCMAudio('song.mp3'), after = lambda e: print(f'[log] {name}, музыка закончила своё проигрывание.'))
	voice.source = discord.PCMVolumeTransformer(voice.source)
	voice.source.volume = 0.07

	song_name = name.rsplit('-', 2)
	await ctx.send (f'Сейчас проигрывается песня : {song_name[0]} ')






#Connect

token = open ('token.txt', 'r').readline()

client.run ( token )
