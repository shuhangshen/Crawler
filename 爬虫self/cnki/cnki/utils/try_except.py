import logging
import sys, traceback

logger = logging.getLogger()

# 异常装饰器

def try_except(functor):
    """
    装饰器 做 try-except 封装
    :param functor:
    :return:
    """
    def handle_problems(*args, **kwargs):
        try:
            return functor(*args, **kwargs)
        except Exception as e:
            exc_type, exc_instance, exc_traceback = sys.exc_info()
            formatted_traceback = ''.join(traceback.format_tb(exc_traceback))
            message = 'trace:\t{0}type:\t{1}instance:\t{2}'.format(
                formatted_traceback,
                exc_type.__name__,
                exc_instance
            )
            print(exc_type(message))
            logger.error("## failure message:  {}   trace_back:    {}".format(e, message))
            # 其他你喜欢的操作
        finally:
            pass

    return handle_problems


@try_except
def test(a, b):
    return a / b


if __name__ == '__main__':
    print(test(3, 0))
    print("ends      ...")
