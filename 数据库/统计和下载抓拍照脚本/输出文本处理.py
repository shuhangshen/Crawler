# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: shentuxiangrong

f = open(r'E:\新建文本文档.txt', 'r', encoding='utf-8')
f1 = open(r'E:\省抓拍统计.txt', 'w', encoding='utf-8')
f2 = open(r'E:\市抓拍统计.txt', 'w', encoding='utf-8')
f3 = open(r'E:\区抓拍统计.txt', 'w', encoding='utf-8')

lines = f.readline()
while lines:
    positionOf = lines.find(' ')
    if positionOf == 2:
        f1.write(lines)
        print(lines)
    elif positionOf == 4:
        f2.write(lines)
        print(lines)
    elif positionOf == 6:
        f3.write(lines)
    else:
        print(lines + '#################################################')
    lines = f.readline()

f.close()
f1.close()
f2.close()
f3.close()
