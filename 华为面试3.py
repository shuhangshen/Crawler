import sys
'''
在通讯软件中，在群里面转发消息可以使得一条消息扩散到很多人那里。假设已知有m个群，其中一个人把一条消息发
到他自己所在的所有群里面，这些群里面的每个人又把消息再次转发到他所有的群里面，请问所有群的所有人都转发过一次后，
最后几个人收到该消息（包括发消息的人）？输出收到消息的人数（以十进制整数输出，不需要加换行符）。

输入描述：
发第一条消息的人名
群组个数m
群组1成员人名
群组2成员人名
。。。
群组m成员人名

人名是英文字符串，包含英文字母和空格，最大长度不超过100字符

群组个数m是十进制， 最大不超过100

群主成员人名列表包含1至多个人名， 两个人名之间以逗号隔开


输出描述
以十进制输出最后能收到消息的人数
包括第一个发消息的人也统计进去，重复接收到消息只统计一次

示例：
输入
Jack
3
Jack,Tom,Anny,Lucy
Tom,Danny
Jack,Lily
输出
6
'''
'''
lines = sys.stdin.readlines()
firstPerson = lines[0].strip()
groupNum = int(lines[1].strip())
groupList = []
getList = [firstPerson]


def findall(groupList, firstPerson):
    if groupList == []:
        return
    target = 0
    for ind, menList in enumerate(groupList):
        if firstPerson in menList:
            target = ind
            break
    for person in groupList[target]:
        global getList
        if person not in getList:
            getList.append(person)
    perlist = groupList.pop(target)
    for per in perlist:
        findall(groupList, per)


for ind, line in enumerate(lines[2:]):
    if not line.strip():
        continue
    menList = line.strip().split(',')
    groupList.append(menList)
findall(groupList, firstPerson)
print(len(getList))
'''


lines = sys.stdin.readlines()
firstPerson = lines[0].strip()
groupNum = int(lines[1].strip())
groupList = []
getList = [firstPerson]


def findall(groupList, firstPerson):
    # 截至条件
    if groupList == []:
        return
    target = 0
    for ind, menList in enumerate(groupList):
        if firstPerson in menList:
            target = ind
            break
    for person in groupList[target]:
        global getList
        if person not in getList:
            getList.append(person)
    perlist = groupList.pop(target)
    for per in perlist:
        findall(groupList, per)


for ind, line in enumerate(lines[2:]):
    if not line.strip():
        continue
    menList = line.strip().split(',')
    groupList.append(menList)
findall(groupList, firstPerson)
print(len(getList))
