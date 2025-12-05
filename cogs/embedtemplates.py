import discord
from cogs.player import Player
from cogs.draft import Draft


def team_template(user, player: Player, draftClass: Draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    count = 1
    for artist_name in player.get_all_artists():
        top_ranking = draftClass.get_all_artists().index(artist_name) + 1

        embed.add_field(name=f"{count}:\t{artist_name}",
                        value=f"Picked at #{player.get_all_artists().index(artist_name) + 1}. Ranked {top_ranking} in league ranking"
                        if player.get_artist(artist_name)["picked"] else
                        f"Artist was picked up. Ranked {top_ranking} in league ranking", inline=False)

        count += 1

    return embed


def weekly_template(user, player, draftClass):
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Week",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners per month.")

    artist_scores = player.get_artists_scores()  # dict: {artist: {...}}

    if not artist_scores:
        embed.add_field(
            name="No Scores Found",
            value="This player has no artist data yet.",
            inline=False
        )
        return embed

    for count, (artist_name, data) in enumerate(artist_scores.items(), start=1):

        # safely get weekly score
        weekly = data.get("weekly", 0)

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{weekly:,}",
            inline=False
        )

    return embed


def monthly_template(user, player, draftClass):
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Month",
        color=discord.Color.gold(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners per month.")

    monthly_scores = player.getMonthlyArtistScores()
    count = 1

    for artist_name in enumerate(player.get_all_artists()):
        # Get score from dict safely
        listeners = monthly_scores.get(artist_name)

        if listeners is None:
            if artist_name in draftClass.get_all_artists():
                return "Need more information to perform this command."
            listeners = 0

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{listeners:,}",
            inline=False,
        )
        count += 1

    return embed


def total_template(user, player, draftClass):
    embed = discord.Embed(
        title=f"{user.name}'s Team Total Listeners",
        color=discord.Color.purple(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners.")

    total_scores = player.get_total_score()
    count = 1

    for artist_name in player.get_all_artists():
        listeners = total_scores.get(artist_name)

        if listeners is None:
            if artist_name in draftClass.get_all_artists():
                return "Need more information to perform this command."
            listeners = 0

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{listeners:,}",
            inline=False,
        )
        count += 1

    return embed
