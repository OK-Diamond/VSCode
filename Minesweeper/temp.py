def perm_iterate(list, head, tail=''):
    if len(head) == 0:
        return([tail])
    else:
        for i in range(len(head)):
            list.append(perm_iterate(list, head[:i] + head[i+1:], tail + str(head[i])))
        return list

def perm(inp):
    perm_list, yuk = [], perm_iterate([], inp)
    for i in yuk:
        if len(i) == 1:
            perm_list.append([])
            for j in i[0]:
                perm_list[-1].append(int(j))
    return perm_list


print(perm([0,1,2]))