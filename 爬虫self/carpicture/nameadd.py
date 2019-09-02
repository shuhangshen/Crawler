import os


def Nameadd(path, topath):
    with open(path, 'r', encoding="utf-8") as f:
        line = f.readline()
        print(line)
        contains = line.split()
        for contain in contains:
            print(contain)
            line1 = ''.join([contain, '_后座'])
            line2 = ''.join([contain, '_副驾驶'])
            line3 = ''.join([contain, '_座椅'])
            # print(line1)
            # print(line2)
            # print(line3)

            name = ''.join([topath, '/', 'keywords3.txt'])
            if not os.path.exists(topath):
                os.makedirs(topath)
            with open(name, 'a', encoding="utf-8") as f:
                f.write(line1 + '\r\n')
                f.write(line2 + '\r\n')
                f.write(line3 + '\r\n')



path1 = r'C:/Users/YJY/Desktop/workspace/carpicture/keywords2.txt'
topath1 = r'C:/Users/YJY/Desktop/workspace/carpicture'


Nameadd(path1, topath1)
