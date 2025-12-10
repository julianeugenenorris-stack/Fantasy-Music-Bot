import random


def create_schedule(list: list):
    """ Create a schedule for the teams in the list and return it"""
    s = []

    if len(list) % 2 == 1:
        list = list + ["BYE"]

    for i in range(len(list)-1):

        mid = int(len(list) / 2)
        l1 = list[:mid]
        l2 = list[mid:]
        l2.reverse()

        # Switch sides after each round
        if (i % 2 == 1):
            s = s + [l1, l2]
        else:
            s = s + [l2, l1]

        list.insert(1, list.pop())

    print(s[:])

    return s


def create_schedule(teams: list):
    """Creates a round-robin schedule with proper matchups."""
    n = len(teams)
    if n % 2 == 1:
        teams = teams + ["BYE"]

    teams = teams[:]  # prevent mutating original list
    n = len(teams)

    schedule = []

    for _ in range(n - 1):
        mid = n // 2

        left = teams[:mid]
        right = teams[mid:]
        right = right[::-1]

        week = []
        for a, b in zip(left, right):
            week.append((a, b))  # proper matchup tuple

        schedule.append(week)

        # rotate
        teams = [teams[0]] + teams[-1:] + teams[1:-1]

    return schedule


print(full_sched)
