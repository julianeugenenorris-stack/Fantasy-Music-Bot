import discord
from cogs.player import Player
from cogs.draft import Draft

WEEK_MONTH_CONVER = 4.34524


def team_template(user, player: Player, draft: Draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    count = 1
    for artist_name in player.get_all_artists():
        top_ranking = draft.get_all_artists().index(artist_name) + 1

        embed.add_field(name=f"{count}:\t{artist_name}",
                        value=f"Picked at #{player.get_all_artists().index(artist_name) + 1}. Ranked {top_ranking} in league ranking"
                        if player.get_artist(artist_name)["picked"] else
                        f"Artist was picked up. Ranked {top_ranking} in league ranking", inline=False)

        count += 1

    return embed


def artists_albums_template(user, player: Player, draft: Draft):
    print(player.get_artists_information())
    embed = discord.Embed(
        title=f"{user.name}'s Team Artsits Albums",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)

    artist_info = player.get_artists_information()

    for count, (name, data) in enumerate(artist_info.items(), start=1):

        albums = ", ".join(data.get("albums_on_record", []))

        embed.add_field(
            name=f"{count}: {name}",
            value=f"{albums}",
            inline=False
        )

    return embed


def weekly_listeners_template(user, player: Player, draft: Draft):
    print(player.get_artists_information())
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Week",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(
        text=f"# is listeners counted this in week {draft.week_in_season}.")

    artist_info = player.get_artists_information()  # dict: {artist: {...}}

    for count, (artist_name, data) in enumerate(artist_info.items(), start=1):

        # safely get weekly score
        weekly = data.get("weekly")

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{weekly[len(weekly)-1]:,}",
            inline=False
        )

    embed.add_field(
        name=f"Total Weekly Listeners:",
        value=f"{player.weekly_listeners:,}",
        inline=False
    )

    return embed


def monthly_listeners_template(user, player: Player, draft):
    print(player.get_artists_information())
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Month",
        color=discord.Color.gold(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners for each week added together.")

    artist_info = player.get_artists_information()  # dict: {artist: {...}}

    monthly_listeners = 0

    for count, (artist_name, data) in enumerate(artist_info.items(), start=1):

        # safely get weemonthlykly score
        monthly = data.get("monthly")
        monthly_listeners += monthly[len(monthly)-1]
        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{monthly[len(monthly)-1]:,}",
            inline=False
        )

    embed.add_field(
        name=f"Total Monthly Listeners:",
        value=f"{monthly_listeners:,}",
        inline=False
    )

    return embed


def total_listeners_template(user, player: Player, draft):
    print(player.get_artists_information())
    embed = discord.Embed(
        title=f"{user.name}'s Team Total Listeners",
        color=discord.Color.purple(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners.")

    artist_info = player.get_artists_information()  # dict: {artist: {...}}

    for count, (artist_name, data) in enumerate(artist_info.items(), start=1):

        # safely get weekly score
        yearly = data.get("yearly_total")

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{yearly:,}",
            inline=False
        )

    embed.add_field(
        name=f"Total Listeners:",
        value=f"{player.total_listeners:,}",
        inline=False
    )

    return embed


def weekly_scores_template(user, player: Player, draft: Draft):
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Week",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners per month.")

    artist_scores = player.get_artists_information()  # dict: {artist: {...}}

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


def monthly_scores_template(user, player, draft):
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
            if artist_name in draft.get_all_artists():
                return "Need more information to perform this command."
            listeners = 0

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{listeners:,}",
            inline=False,
        )
        count += 1

    return embed


def total_scores_template(user, player, draft):
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
            if artist_name in draft.get_all_artists():
                return "Need more information to perform this command."
            listeners = 0

        embed.add_field(
            name=f"{count}: {artist_name}",
            value=f"{listeners:,}",
            inline=False,
        )
        count += 1

    return embed
