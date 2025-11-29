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
        # index in master artist list
        i = draftClass.getArtists().index(artist_name)

        # listener count using same index
        listeners = draftClass.getListeners()[i]

        embed.add_field(name=f"{count}:\t{artist_name}",
                        value=f"{listeners:,}", inline=False)

        count += 1

    return embed


def weeklyTemplate(user, player, draftClass):
    embed = discord.Embed(
        title=f"{user.name}'s Team",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is current monthly listeners for artists.")
    count = 1
    for artist_name in player.getArtists():
        # index in master artist list
        i = draftClass.getArtists().index(artist_name)

        # listener count using same index
        listeners = draftClass.getListeners()[i]

        embed.add_field(name=f"{count}:\t{artist_name}",
                        value=f"{listeners:,}", inline=False)

        count += 1

    return embed


def monthlyTemplate(user, player, draftClass):
    embed = discord.Embed(
        title=f"{user.name}'s Team",
        color=discord.Color.blue(),
    )

    embed.set_thumbnail(url=user.display_avatar.url)
    embed.set_footer(text="# is current monthly listeners for artists.")
    count = 1
    for artist_name in player.getArtists():
        # index in master artist list
        i = draftClass.getArtists().index(artist_name)

        # listener count using same index
        listeners = draftClass.getListeners()[i]

        embed.add_field(name=f"{count}:\t{artist_name}",
                        value=f"{listeners:,}", inline=False)

        count += 1

    return embed
