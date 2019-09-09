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

lines = sys.stdin.readlines()
firstPerson = lines[0].strip()
groupNum = int(lines[1].strip())
groupList = []
getList = [firstPerson]


class Solution(object):
    def findall(self, groupList, firstPerson):
        # 截止条件
        if groupList == []:
            return

        target = 0
        flag = 0

        for ind, menList in enumerate(groupList):
            if firstPerson in menList:
                target = ind
                flag = 1
                break
        if flag == 1:
            for person in groupList[target]:
                # global getList
                if person not in getList:
                    getList.append(person)
        else:
            return

        perlist = groupList.pop(target)
        for per in perlist:
            self.findall(groupList, per)


class Solution2(object):
    def findall(self, groupList):
        for know in getList:
            for perList in groupList:
                if know in perList:
                    for person in perList:
                        if person not in getList:
                            getList.append(person)


for ind, line in enumerate(lines[2:]):
    if not line.strip():
        continue
    menList = line.strip().split(',')
    groupList.append(menList)
# s = Solution()
# s.findall(groupList, firstPerson)
s = Solution2()
s.findall(groupList)
print(len(getList))


'''
# 按 ctrl + d 结束输入
'''
