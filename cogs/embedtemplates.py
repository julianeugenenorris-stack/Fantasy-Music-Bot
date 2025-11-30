import discord


def basicTemplate(user, player, draftClass):
    embed = discord.Embed(
        title=f"{user.name}'s Team",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is current monthly listeners for artists.")
    count = 1
    for artist_name in player.getArtists():
        i = draftClass.getArtists().index(artist_name)

        listeners = draftClass.getLeagueStartListeners()[i]

        embed.add_field(name=f"{count}:\t{artist_name}",
                        value=f"{listeners:,}", inline=False)

        count += 1

    return embed


def weeklyTemplate(user, player, draftClass):
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Week",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners per month.")
    count = 1
    for artist_name in player.getArtists():
        try:
            i = player.getArtists().index(artist_name)
            listeners = player.getPrevWeekArtistScores()[i]
        except (ValueError, IndexError) as e:
            if artist_name in draftClass.getArtists():
                return "Need more information to perform this command."
            listeners = 0
        embed.add_field(name=f"{count}:\t{artist_name}",
                        value=f"{listeners:,}", inline=False)
        count += 1

    return embed


def monthlyTemplate(user, player, draftClass):
    embed = discord.Embed(
        title=f"{user.name}'s Team Last Month",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is listeners per month.")
    count = 1
    for artist_name in player.getArtists():
        try:
            i = player.getArtists().index(artist_name)
            listeners = player.getMonthlyArtistScores()[i]
        except (ValueError, IndexError) as e:
            if artist_name in draftClass.getArtists():
                return "Need more information to perform this command."
            listeners = 0
        embed.add_field(name=f"{count}:\t{artist_name}",
                        value=f"{listeners:,}", inline=False)
        count += 1

    return embed
