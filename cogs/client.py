import discord
from discord.ext import commands, tasks
from discord import app_commands

GUILD_ID = None


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

        if GUILD_ID is None:
            print(f"Syncing without guild, no ID")
            await self.tree.sync()

        try:
            synced = await self.tree.sync(guild=GUILD_ID)
            print(f"Synced {len(synced)} command to guild {GUILD_ID.id}")

        except Exception as e:
            print(f'Error syncing command {e}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # if message.content.startswith("hello"):
        #    await message.channel.send(f"Hi There {message.author}")


def start_client(guild_id: any = None, owner=None):
    global GUILD_ID

    GUILD_ID = guild_id

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.messages = True

    botDescription: str = f"This bot runs a server wide draft. There can only be a single active draft per league. For help, type ""/help""."

    client: Client = Client(
        command_prefix="!",
        intents=intents,
        owner_id=owner,
        description=str(botDescription),
    )

    return client
