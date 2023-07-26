import discord
from discord.ext import commands
import youtube_dl

# Configuración de las intenciones para el bot
intents = discord.Intents.all()

# Creación del bot con el prefijo de comandos y las intenciones
bot = commands.Bot(command_prefix='!', intents=intents)

# Configuración del módulo de youtube_dl
ytdl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
ytdl = youtube_dl.YoutubeDL(ytdl_opts)

# Diccionario para mantener las colas de reproducción en cada servidor
queues = {}

# Función para unirse a un canal de voz
async def join_voice(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("Debes estar en un canal de voz para usar este comando.")
        return

    channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if voice_client is not None:
        await voice_client.move_to(channel)
    else:
        await channel.connect()

# Función para reproducir música
async def play_song(ctx, url):
    voice_channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if voice_channel is None:
        await ctx.send("Debes estar en un canal de voz para usar este comando.")
        return

    if voice_client is None or not voice_client.is_connected():
        await join_voice(ctx)

    with ytdl as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        voice_client.play(discord.FFmpegPCMAudio(url2), after=lambda e: bot.loop.create_task(check_queue(ctx)))

    await ctx.send(f"Reproduciendo: {info['title']}")

# Comando para reproducir música desde YouTube
@bot.command()
async def play(ctx, *, url):
    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []

    await join_voice(ctx)

    queues[ctx.guild.id].append(url)
    await play_song(ctx, url)  # Llamada a la función corregida

# Función para verificar y reproducir la siguiente canción en la cola
async def check_queue(ctx):
    voice_client = ctx.voice_client

    if len(queues[ctx.guild.id]) > 0:
        url = queues[ctx.guild.id].pop(0)
        with ytdl as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['formats'][0]['url']
            voice_client.play(discord.FFmpegPCMAudio(url2), after=lambda e: bot.loop.create_task(check_queue(ctx)))
        await ctx.send(f"Reproduciendo siguiente en la cola: {info['title']}")
    else:
        await voice_client.disconnect()

# Comando para saltar a la siguiente canción en la cola
@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client is not None and voice_client.is_playing():
        voice_client.stop()

# Comando para detener la reproducción y limpiar la cola
@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client is not None:
        voice_client.stop()
        queues[ctx.guild.id] = []

# Comando para desconectar el bot del canal de voz
@bot.command()
async def disconnect(ctx):
    voice_client = ctx.voice_client
    if voice_client is not None:
        await voice_client.disconnect()

# Evento que se ejecuta cuando el bot está listo
@bot.event
async def on_ready():
    print(f'{bot.user} está listo para reproducir música.')

# Ejecución del bot con tu token
bot.run('MTEzMzgyOTg5MjE1MzI5OTA2Ng.GIZ2Yz.bOal-1TYqx7RcVF5bi9UVyRHJSFkkAD6SqPyLg')
