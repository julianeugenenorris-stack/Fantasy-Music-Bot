from cogs.client import start_client

from dotenv import load_dotenv, dotenv_values

from cogs.scraper import *
from cogs.embedtemplates import *
from cogs.scoring import *

from cogs.draft import Draft

load_dotenv()
config = dotenv_values()
GUILD_ID = discord.Object(id=config.get("GUILD_ID"))
DISCORD_TOKEN = config.get("DISCORD_TOKEN")
OWNER_ID = config.get("OWNER_ID")

client = start_client(GUILD_ID, OWNER_ID)
draft = None


@client.event
async def on_guild_join(guild):
    print(f"joined: {guild}")


@client.tree.command(name="createdraft", description="Start Music Draft", guild=GUILD_ID)
async def createDraft(interaction: discord.Interaction, draftname: str, rounds: int, pointsPerListener: int, ):
    global draft

    if int(rounds) > 100:
        await interaction.response.send_message("Please enter a number below 100.", delete_after=10, ephemeral=True)
        return

    if draft is None:
        await interaction.response.send_message(f"Draft {draftname} is open. Type /join to join.")
        draft = Draft(draftname, int(rounds))
        draft.
        return

    await interaction.response.send_message(f"Draft {draft.getName()} was already created in the guild.\nOnly one draft per guild id.", delete_after=10, ephemeral=True)


@client.tree.command(name="startdraft", description="Start Music Draft", guild=GUILD_ID)
async def startDraft(interaction: discord.Interaction):
    global draft

    if draft is None:
        await interaction.response.send_message("No draft class is open.\n/createdraft to make one", delete_after=10, ephemeral=True)
        return

    try:
        if draft.is_stage():
            await interaction.response.send_message("Draft is already over.", delete_after=10, ephemeral=True)
            return
        if draft.isDraftStarted():
            await interaction.response.send_message("already started draft", delete_after=10, ephemeral=True)
            return
    except:
        await interaction.response.send_message("No draft class is open.\n/createdraft to make one", delete_after=10, ephemeral=True)
        return

    if draft.getSize() < 1:
        await interaction.response.send_message("Not enough players in draft", delete_after=10, ephemeral=True)
        return

    await interaction.response.send_message("Starting draft...")

    if not cache_is_current():
        await interaction.followup.send("Downloading artists and listeners.")
        download_pages()
        update_timestamp()

    websiteArrays = parse_all_pages()
    draft.setArtists(websiteArrays[0])
    draft.setStartListeners(websiteArrays[1])

    draftName = f"draft{draft.getName()}"
    save_object(draft, draftName)

    for p in draft.getPlayers():
        save_object(p, f"player{p.getID()}.txt")

    await interaction.followup.send("Draft ready! Starting Draft Lobby.")

    draft.startDraft()

    firstPlayer = draft.getPlayers()[0]
    user = await client.fetch_user(firstPlayer.getID())
    await interaction.followup.send(f"{user.mention} You Are On The Board.\nUse /draft to select a player using their name exactly as written on spotify.\n(must have more than half a million monthly listeners.)")


@client.tree.command(name="join", description="Join fantasy draft as a player.", guild=GUILD_ID)
async def joinDraft(interaction: discord.Interaction):
    global draft

    if draft.isDraftStarted():
        await interaction.response.send_message("Draft already started", delete_after=10, ephemeral=True)
        return

    user = interaction.user
    if draft is not None:
        for p in draft.getPlayers():
            if p.getID() == user.id:
                await interaction.response.send_message("You're already in the draft!", delete_after=10, ephemeral=True)
                return

    draft.add_new_player(user.id, user.name)

    draftName = f"draft{draft.getName()}"
    save_object(draft, draftName)

    await interaction.response.send_message(f"{interaction.user.name} joined the draft.")


@client.tree.command(name="startseason", description="This will begin the fantasy season, set the update schedual (0=monday, 6=sunday) (24 hour format).", guild=GUILD_ID)
async def draftArtist(interaction: discord.Interaction, day: int, hour: int, minute: int):
    if draft.isSeasonStarted() is True:
        await interaction.response.send_message(f"{draft.getName()}'s fantasy season is already started.")
        return
    await interaction.response.send_message(f"Starting {draft.getName()}'s fantasy season.")

    draft.setUpdateTimer(day, hour, minute)
    draft.startSeason()

    draftName = f"draft{draft.getName()}"
    save_object(draft, draftName)

    client.loop.create_task(weeklyUpdate(
        draft, day, hour, minute, interaction))


@client.tree.command(name="draft", description="Draft artists to fantasy team.", guild=GUILD_ID)
async def draftArtist(interaction: discord.Interaction, message: str):

    try:
        if not draft.isDraftStarted() or draft.isDone():
            await interaction.response.send_message("Need to start draft before drafting players", delete_after=10, ephemeral=True)
            return
    except:
        await interaction.response.send_message("Need to create or import a draft room.", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    if draft.isDraftCompleted():
        await interaction.response.send_message(
            "Draft is already over.", delete_after=10, ephemeral=True)
        return

    if draft.getPlayers()[draft.getTurn()].getID() == user.id:
        for a in draft.getAllArtists():
            if a == message:
                player = draft.getPlayers()[draft.getTurn()]

                if a in player.getArtists():
                    await interaction.response.send_message(f"You have already drafted {a}. \nDraft someone else.", delete_after=10, ephemeral=True)
                    return

                await interaction.response.send_message(f"{user.name} has drafted {a}!")
                player.addArtist(a)

                draft.nextTurn()

                if not draft.isDraftCompleted():
                    nextPlayer = draft.getPlayers()[draft.getTurn()]
                    user = await client.fetch_user(nextPlayer.getID())

                    draftName = f"draft{draft.getName()}"
                    save_object(draft, draftName)

                    await interaction.followup.send(f"{user.mention} You Are On The Board.\nUse /draft to select a player using their name exactly as written on spotify.\n(must have more than half a million monthly listeners.)")
                    return
                else:
                    draftName = f"draft{draft.getName()}"
                    save_object(draft, draftName)

                    await interaction.followup.send("Draft Completed.")
                    return
        await interaction.response.send_message(f"The artist {message} is not in the draft pool.", delete_after=10, ephemeral=True)
        return
    else:
        await interaction.response.send_message("It is not your turn.", delete_after=10, ephemeral=True)
        return


@client.tree.command(name="reloaddraft", description="Join fantasy draft as a player.", guild=GUILD_ID)
async def reloadDraft(interaction: discord.Interaction, message: str):
    global draft

    if draft is None:
        try:
            draft = load_object(f"draft{message}")
            await interaction.response.send_message(f"{message} has been reloaded.")
            if draft.isSeasonStarted():
                await interaction.followup.send(f"Restarting {draft.getName()}'s fantasy season.")
                client.loop.create_task(weeklyUpdate(draft, draft.getUpdateTime()[
                                        0], draft.getUpdateTime()[1], draft.getUpdateTime()[2], interaction))
                return
            if draft.isDraftCompleted():
                await interaction.followup.send(f"Start the fantasy season with /startseason.")
                return
            if draft.isDraftStarted():
                nextPlayer = draft.getPlayers()[draft.getTurn()]
                user = await client.fetch_user(nextPlayer.getID())
                await interaction.followup.send(f"{user.mention} You Are On The Board.\nUse /draft to select a player using their name exactly as written on spotify.\n(must have more than half a million monthly listeners.)")
            return
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", delete_after=10, ephemeral=True)
            return
    try:
        await interaction.response.send_message(f"{draft.getName()} has already been created.", delete_after=10, ephemeral=True)
        return
    except FileNotFoundError:
        await interaction.response.send_message(f"{message} is not found.", delete_after=10, ephemeral=True)
        return


@client.tree.command(name="team", description="Show a players team.", guild=GUILD_ID)
async def showTeam(interaction: discord.Interaction):
    global draft

    if draft.isDone() is True:
        await interaction.response.send_message("Use /weeklyscores, /monthlyscores, and /totalscores to check the team after the draft.", delete_after=10, ephemeral=True)
        return

    if draft.isDraftStarted() is False:
        await interaction.response.send_message("Need to start draft before checking team.", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    player = None
    for p in draft.getPlayers():
        if p.getID() == user.id:
            player = p
            break

    if player is None:
        await interaction.response.send_message("You are not in this draft.", delete_after=10, ephemeral=True)
        return

    embed = basicTemplate(user, player, draft)

    if type(embed) is str:
        await interaction.response.send_message(embed, delete_after=10, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)


@client.tree.command(name="weeklyscores", description="Show a teams scoring in the previous week.", guild=GUILD_ID)
async def showWeelyScores(interaction: discord.Interaction):
    if draft.isDone() is False:
        await interaction.response.send_message("Need to finish draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    player = None
    for p in draft.getPlayers():
        if p.getID() == user.id:
            player = p
            break

    if player is None:
        await interaction.response.send_message("You are not in this draft.", delete_after=10, ephemeral=True)
        return

    embed = weeklyTemplate(user, player, draft)

    if type(embed) is str:
        await interaction.response.send_message(embed, delete_after=10, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)


@client.tree.command(name="monthlyscore", description="Show a players monthly scores.", guild=GUILD_ID)
async def showYearlyScores(interaction: discord.Interaction):
    if draft.isDone() is False:
        await interaction.response.send_message("Need to finish draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user

    player = None
    for p in draft.getPlayers():
        if p.getID() == user.id:
            player = p
            break

    if player is None:
        await interaction.response.send_message("You are not in this draft.", delete_after=10, ephemeral=True)
        return

    embed = monthlyTemplate(user, player, draft)

    if type(embed) is str:
        await interaction.response.send_message(embed, delete_after=10, ephemeral=True)
        return

    await interaction.response.send_message(embed=embed)


@client.tree.command(name="testupdate", description="Draft artists to fantasy team.", guild=GUILD_ID)
async def draftArtist(interaction: discord.Interaction):
    await interaction.response.send_message("Starting weekly artist score update...")
    try:
        if draft is None:
            await interaction.followup.send("No draft loaded, skipping update.")
            return

        await interaction.followup.send("Downloading latest artists and listeners...")
        download_pages()

        websiteArrays = parse_all_pages()
        draft.setArtists(websiteArrays[0])

        draftName = f"draft{draft.getName()}"
        save_object(draft, draftName)

        draft.updateWeeklyListeners(websiteArrays[1])
        draft.updateMonthlyScores()
        draft.updateTotalScores()

        for p in draft.getPlayers():
            save_object(p, f"player{p.getID()}.txt")

        await interaction.followup.send("Weekly update completed!")
    except Exception as e:
        await interaction.followup.send(f"Error during weekly update: {e}")


@client.tree.command(name="leagueoverview", description="Shows overview of all players in league and their scoring totals.", guild=GUILD_ID)
async def showYearlyScores(interaction: discord.Interaction):
    if draft.isDone() is False:
        await interaction.response.send_message("Need to start draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user


@client.tree.command(name="leaders", description="Shows the top scoring artists.", guild=GUILD_ID)
async def showYearlyScores(interaction: discord.Interaction):
    if draft.isDone() is False:
        await interaction.response.send_message("Need to start draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user


@client.tree.command(name="trade", description="Send a trade offer to player.", guild=GUILD_ID)
async def showYearlyScores(interaction: discord.Interaction):
    if draft.isDone() is False:
        await interaction.response.send_message("Need to start draft before checking scores", delete_after=10, ephemeral=True)
        return

    user = interaction.user


client.run(DISCORD_TOKEN)
