

if __name__ == '__main__':

    file = open("/tmp/log-game-training-squads.txt", "r")
    lines = file.readlines()
    train_lines = []
    for line in lines:
        if line.startswith("train squad action"):
            train_lines.append(line)

    squads_ids = [
        "7marines_3marauders",
        "5marines_5marauders",
        "3marines_7marauders",
        "10marines"
    ]

    zerg_squads_counts = {
        squads_ids[0]: 0,
        squads_ids[1]: 0,
        squads_ids[2]: 0,
        squads_ids[3]: 0,
    }
    protoss_squads_counts = {
        squads_ids[0]: 0,
        squads_ids[1]: 0,
        squads_ids[2]: 0,
        squads_ids[3]: 0,
    }
    terran_squads_counts = {
        squads_ids[0]: 0,
        squads_ids[1]: 0,
        squads_ids[2]: 0,
        squads_ids[3]: 0,
    }

    for train_line in train_lines:
        tokens = train_line.replace('\n', '').split(',')
        race = tokens[3]
        squad = squads_ids[int(tokens[2])]
        if race == 'zerg':
            zerg_squads_counts[squad] = zerg_squads_counts[squad] + 1
        elif race == 'protoss':
            protoss_squads_counts[squad] = protoss_squads_counts[squad] + 1
        elif race == 'terran':
            terran_squads_counts[squad] = terran_squads_counts[squad] + 1

    print("race\t"+"total\t"+squads_ids[0]+"\t"+squads_ids[1]+"\t"+squads_ids[2]+"\t"+squads_ids[3])
    lines = [
        ['zerg', zerg_squads_counts],
        ['protoss', protoss_squads_counts],
        ['terran', terran_squads_counts]
    ]
    for line in lines:
        squad1 = line[1][squads_ids[0]]
        squad2 = line[1][squads_ids[1]]
        squad3 = line[1][squads_ids[2]]
        squad4 = line[1][squads_ids[3]]
        total = squad1 + squad2 + squad3 + squad4
        squad1_per = '{0:.0f} %'.format((float(squad1) / float(total) * 100))
        squad2_per = '{0:.0f} %'.format((float(squad2) / float(total) * 100))
        squad3_per = '{0:.0f} %'.format((float(squad3) / float(total) * 100))
        squad4_per = '{0:.0f} %'.format((float(squad4) / float(total) * 100))
        print(line[0]+"\t"+str(total)+"\t"+str(squad1)+"\t("+str(squad1_per)+")\t\t"+str(squad2)+"\t("+str(squad2_per)+")\t\t"+str(squad3)+"\t("+str(squad3_per)+")\t\t"+str(squad4)+"\t("+str(squad4_per)+")")
