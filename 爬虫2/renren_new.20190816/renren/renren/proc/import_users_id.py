import os

from renren.settings import REDIS_HOST, REDIS_PORT
from renren.utils.redis_helper import RedisHelper
from renren.utils.setting import SAVE_PATH


def main():
    redis_helper = RedisHelper(host=REDIS_HOST, port=REDIS_PORT)
    USER_ID_BITS = 'user_id_bits'

    root_dir = SAVE_PATH + "\\id"
    list_in_path = os.listdir(root_dir)
    list_out_path = []
    for i in list_in_path:
        path = os.path.join(root_dir, i)
        if path.endswith(".txt") and os.path.isfile(path):
            list_out_path.append(path)

    counter = 0

    for path in list_out_path:
        with open(path, "r") as f:
            print("proc file: ", path)
            for line in f:
                user_id = line.rstrip("\r\n")
                if len(user_id) == 0:
                    continue
                counter += 1
                redis_helper.bitmap_set(key=USER_ID_BITS, offset=int(user_id))

    print("import user_id TOTAL:    {}".format(counter))


if __name__ == '__main__':
    main()
