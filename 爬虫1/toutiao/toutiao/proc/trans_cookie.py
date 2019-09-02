def trans(*, cookie_in_path):
    with open(cookie_in_path,"r",encoding='utf-8') as f:
        cookie_out =dict()
        for line in f:
            line = line.rstrip("\n")
            k_v = line.split("\t")
            key = k_v[0]
            value = k_v[1]
            cookie_out[key] = value
    return cookie_out


def main():
    path = r"Z:\lisi8\WORKSPACE\renren\cookie\cookie.txt"
    ret = trans(cookie_in_path=path)
    print("ret: \n", ret)


if __name__ == '__main__':
    main()
