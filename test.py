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


players: list = ["Player 1", "Player 2", "Player 3",
                 "Player 4", "Player 5", "Player 6", "Player 7", "Player 8", "Player 9",
                 "Player 10", "Player 11", "Player 12", "Player 13"]
random.shuffle(players)  # suffle
print(players)
count = 0
sched = create_schedule(players)
full_sched = []
for week in range(0, 24):
    try:
        full_sched += sched[week]
        print(sched[week])
        count += 0.5
    except:
        sched += sched
        full_sched += sched[week]
        print(sched[week])
        count += 0.5


print(count)
