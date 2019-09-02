import demjson


def main():
    json_path = r'C:\Users\YJY\PycharmProjects\Spider233\koubei\doc\name.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        dat = f.read()
        print(dat)
        json = demjson.decode(dat)

        trade_info = json['tradeinfo']
        for info in trade_info:
            tid = info['tid']
            children = info['child']
            for child in children:
                cid = child['cid']
                cname = child['cname']
                print("{} {} {}".format(tid, cid, cname))

        # trade_tag_info = json['tradetaginfo']
        # for info in trade_tag_info:
        #     cid = info['cid']
        #     cname = info['cname']
        #     print('tag {} {}'.format(cid, cname))

        pass


if __name__ == '__main__':
    main()
