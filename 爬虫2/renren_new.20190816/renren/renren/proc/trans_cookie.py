# firefox
def trans(*, cookie_in_path):
    with open(cookie_in_path, "r", encoding='utf-8') as f:
        cookie_out = dict()
        for line in f:
            line = line.rstrip("\n")
            k_v = line.split("\t")
            key = k_v[0]
            value = k_v[1]
            cookie_out[key] = value
    return cookie_out


# chrome
def trans_v2(*, cookie_in_path):
    with open(cookie_in_path, "r", encoding='utf-8') as f:
        cookie_out = dict()
        contents = f.read()
        lines = contents.split(";")
        for line in lines:
            k_v = line.split('=')
            key = k_v[0].strip()
            value = k_v[1].strip()
            cookie_out[key] = value
    return cookie_out
    pass


def main():
#     path = r"Z:\lisi8\WORKSPACE\renren\cookie\cookie.txt"
#     ret = trans(cookie_in_path=path)

    path = r"D:\SVN\spider\renren\cookie_1.txt"

    ret = trans_v2(cookie_in_path=path)

    print("ret: \n", ret)


if __name__ == '__main__':
    main()
