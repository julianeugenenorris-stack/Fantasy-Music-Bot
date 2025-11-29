import discord
from discord.ext import commands, tasks
from discord import app_commands

from dotenv import load_dotenv

from cogs.scraper import *
from cogs.embedtemplates import *

from cogs.draftroom import Draft, Player

load_dotenv()


class Client(commands.Bot):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

        try:
            guild = discord.Object(id=1444005027541815429)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} command to guild {guild.id}")

        except Exception as e:
            print(f'Error syncing command {e}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        # if message.content.startswith("hello"):
        #    await message.channel.send(f"Hi There {message.author}")


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=os.getenv("GUILD_ID"))

draftClass = None


@client.tree.command(name="createdraft", description="Start Music Draft", guild=GUILD_ID)
async def createDraft(interaction: discord.Interaction, draftname: str, rounds: str):
    global draftClass

    if int(rounds) > 100:
        await interaction.response.send_message("Please enter a number below 100.", delete_after=10, ephemeral=True)
        return

    if draftClass is None:
        await interaction.response.send_message(f"Draft {draftname} is open. Type /join to join.")
        draftClass = Draft(draftname, int(rounds))
        return

    await interaction.response.send_message(f"Draft {draftClass.getName()} was already created in the guild.\nOnly one draft per guild id.", delete_after=10, ephemeral=True)


@client.tree.command(name="startdraft", description="Start Music Draft", guild=GUILD_ID)
async def startDraft(interaction: discord.Interaction):
    global draftClass

    if draftClass is None:
        try:
            if draftClass.isStarted():
                await interaction.response.send_message("already started draft")
                return
        except:
            await interaction.response.send_message("No draft class is open.\n/createdraft to make one", delete_after=10, ephemeral=True)
            return

    if draftClass.getSize() < 1:
        await interaction.response.send_message("Not enough players in draft", delete_after=10, ephemeral=True)
        return

    await interaction.response.send_message("Starting draft...")

    if not cache_is_current():
        await interaction.followup.send("Downloading artists and listeners.")
        download_pages()
        update_timestamp()

    websiteArrays = parse_all_pages()
    draftClass.setArtists(websiteArrays[0])
    draftClass.setListeners(websiteArrays[1])

    draftName = f"draft{draftClass.getName()}"
    save_object(draftClass, draftName)

    for p in draftClass.getPlayers():
        save_object(p, f"player{p.getID()}.txt")

    await interaction.followup.send("Draft ready! Starting Draft Lobby.")

    draftClass.startDraft()

    firstPlayer = draftClass.getPlayers()[0]
    user = await client.fetch_user(firstPlayer.getID())
    await interaction.followup.send(f"{user.mention} You Are On The Board.\nUse /draft to select a player using their name exactly as written on spotify.\n(must have more than half a million monthly listeners.)")


@client.tree.command(name="join", description="Join fantasy draft as a player.", guild=GUILD_ID)
async def joinDraft(interaction: discord.Interaction):
    global draftClass

    if draftClass.isStarted():
        await interaction.response.send_message("Draft already started", delete_after=10, ephemeral=True)
        return

    user = interaction.user
    if draftClass is not None:
        for p in draftClass.getPlayers():
            if p.getID() == user.id:
                await interaction.response.send_message("You're already in the draft!", delete_after=10, ephemeral=True)
                return

    draftClass.addPlayer(user.id)

    draftName = f"draft{draftClass.getName()}"
    save_object(draftClass, draftName)

    await interaction.response.send_message(f"{interaction.user.name} joined the draft.")


@client.tree.command(name="draft", description="Draft artists to fantasy team.", guild=GUILD_ID)
async def draftArtist(interaction: discord.Interaction, message: str):

    try:
        if not draftClass.isStarted() or draftClass.isDone():
            await interaction.response.send_message("Need to start draft before drafting players", delete_after=10, ephemeral=True)
            return
    except:
        await interaction.response.send_message("Need to create or import a draft room.", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    if draftClass.isDraftCompleted():
        await interaction.response.send_message(
            "Draft is already over.", delete_after=10, ephemeral=True)
        return

    if draftClass.getPlayers()[draftClass.getTurn()].getID() == user.id:
        for a in draftClass.getArtists():
            if a == message:
                draftUser = draftClass.getPlayers()[draftClass.getTurn()]

                if a in draftUser.getArtists():
                    await interaction.response.send_message(f"You have already drafted {a}. \nDraft someone else.", delete_after=10, ephemeral=True)
                    return

                await interaction.response.send_message(f"{user.name} has drafted {a}!")
                draftUser.setArtist(a)

                draftClass.nextTurn()

                if not draftClass.isDraftCompleted():
                    nextPlayer = draftClass.getPlayers()[draftClass.getTurn()]
                    user = await client.fetch_user(nextPlayer.getID())

                    draftName = f"draft{draftClass.getName()}"
                    save_object(draftClass, draftName)

                    await interaction.followup.send(f"{user.mention} You Are On The Board.\nUse /draft to select a player using their name exactly as written on spotify.\n(must have more than half a million monthly listeners.)")
                    return
                else:
                    draftName = f"draft{draftClass.getName()}"
                    save_object(draftClass, draftName)

                    await interaction.followup.send("Draft Completed.")
                    return
        await interaction.response.send_message(f"The artist {message} is not in the draft pool.", delete_after=10, ephemeral=True)
        return
    else:
        await interaction.response.send_message("It is not your turn.", delete_after=10, ephemeral=True)
        return


@client.tree.command(name="reloaddraft", description="Join fantasy draft as a player.", guild=GUILD_ID)
async def reloadDraft(interaction: discord.Interaction, message: str):
    global draftClass

    if draftClass is None:
        try:
            draftClass = load_object(f"draft{message}")
            await interaction.response.send_message(f"{message} has been reloaded.")

            if draftClass.isStarted():
                nextPlayer = draftClass.getPlayers()[draftClass.getTurn()]
                user = await client.fetch_user(nextPlayer.getID())
                await interaction.followup.send(f"{user.mention} You Are On The Board.\nUse /draft to select a player using their name exactly as written on spotify.\n(must have more than half a million monthly listeners.)")

            return
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", delete_after=10, ephemeral=True)
    try:
        await interaction.response.send_message(f"{draftClass.getName()} has already been created.")
    except FileNotFoundError:
        await interaction.response.send_message(f"{message} is not found.", delete_after=10, ephemeral=True)


@client.tree.command(name="team", description="Show a players team.", guild=GUILD_ID)
async def showTeam(interaction: discord.Interaction):
    global draftClass

    if draftClass.isDone() is True:
        await interaction.response.send_message("Use /weeklyscores, /monthlyscores, and /totalscores to check the team after the draft.", delete_after=10, ephemeral=True)
        return

    if draftClass.isStarted() is False:
        await interaction.response.send_message("Need to start draft before checking team.", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    player = None
    for p in draftClass.getPlayers():
        if p.getID() == user.id:
            player = p
            break

    if player is None:
        await interaction.response.send_message("You are not in this draft.", delete_after=10, ephemeral=True)
        return

    embed = basicTemplate(user, player, draftClass)

    await interaction.response.send_message(embed=embed)


@client.tree.command(name="weeklyscores", description="Show a players weekly scores.", guild=GUILD_ID)
async def showWeelyScores(interaction: discord.Interaction):
    if draftClass.isDone() is False:
        await interaction.response.send_message("Need to start draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user


@client.tree.command(name="monthlyscores", description="Show a players monthly scores.", guild=GUILD_ID)
async def showMonthlyScores(interaction: discord.Interaction):
    if draftClass.isDone() is False:
        await interaction.response.send_message("Need to start draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user


@client.tree.command(name="yearlyscores", description="Show a players yearly scores.", guild=GUILD_ID)
async def showYearlyScores(interaction: discord.Interaction):
    if draftClass.isDone() is False:
        await interaction.response.send_message("Need to start draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user


client.run(os.getenv("DISCORD_TOKEN"))
