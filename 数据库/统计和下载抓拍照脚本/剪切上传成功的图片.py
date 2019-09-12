# !/usr/bin/env python
# -*- coding:utf-8 -*-
# Author: shentuxiangrong

import cx_Oracle
import os.path
import shutil

output = r'E:\输出文件夹'

if not os.path.exists(output):
    os.mkdir(output)

conn = cx_Oracle.connect('frs/hikfrs@10.108.81.65/hikfacedb')
curs = conn.cursor()

sql = 'SELECT PIC_DATA FROM SNAP_FACE_407'
rr = curs.execute(sql)
row = curs.fetchall()

print('开始执行，请稍等')

for blob in row:
    blobDir = blob[0].read()
    Dir = blobDir.decode('utf-8')
    realDir = (r'\\pc-pubyjysf23\E' + Dir[Dir.find(':') + 1:]).replace('/', '\\')
    picName = Dir[Dir.rfind('\\') + 1:]
    newDir = os.path.join(output, picName)
    #print(realDir, newDir)

    try:
        shutil.copyfile(realDir, newDir)
    except Exception as error:
        print(realDir + '拷贝失败')
        print(error)
        continue
    try:
        os.remove(realDir)
    except Exception as error:
        print(realDir + '删除失败')
        print(error)
        continue

curs.close()
conn.close()

print('执行完成')
#\\pc-pubyjysf23\E\东营中学_测试_屠春来\抓拍照
