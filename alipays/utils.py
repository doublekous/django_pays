from alipay.aop.api.util.SignatureUtils import verify_with_rsa
from django_pays import settings
# 支付宝检查支付结果函数和


def check_pay(params):  # 定义检查支付结果的函数
    sign = params.pop('sign', None)  # 取出签名
    params.pop('sign_type')  # 取出签名类型
    params = sorted(params.items(), key=lambda e: e[0], reverse=False)  # 取出字典元素按key的字母升序排序形成列表
    message = "&".join(u"{}={}".format(k, v) for k, v in params).encode()  # 将列表转为二进制参数字符串
    # with open(settings.ALIPAY_PUBLIC_KEY_PATH, 'rb') as public_key: # 打开公钥文件
    try:
        #     status =verify_with_rsa(public_key.read().decode(),message,sign) # 验证签名并获取结果
        status = verify_with_rsa(settings.ALIPAY_PUBLIC_KEY.encode('utf-8').decode('utf-8'), message,
                                 sign)  # 验证签名并获取结果
        print(status)
        return status  # 返回验证结果
    except:  # 如果验证失败，返回假值。
        return False