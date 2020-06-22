import qrcode

from datetime import datetime

from django.http import JsonResponse, HttpResponse
from django.views import View
from wxpays.utils import wxpay, trans_xml_to_dict, get_sign, API_KEY, trans_dict_to_xml


# 微信支付模式二native
# 此处为测试代码，订单参数直接给出，正式环境根据项目业务自行设计
# 微信支付接口
class OrderWXPayView(View):
    def get(self, request):
        # order_id = request.GET.get('order_id')
        money = request.GET.get('money')
        order_id = '2020062215071'
        # 业务逻辑处理
        # 调用微信支付模式二接口
        order_name = '订单名字'
        order_price_detail = '订单描述'
        order_total_price = money
        data_dict = wxpay(order_id, order_name, order_price_detail, order_total_price)

        # 如果请求成功
        if data_dict.get('return_code') == 'SUCCESS':
            # 业务处理
            # 二维码名字
            qrcode_name = order_id + '.png'
            # 创建二维码
            img = qrcode.make(data_dict.get('code_url'))
            img.save(r'static' + '/' + qrcode_name)
            # 这里最好再把二维码放在云存储器上面
            return JsonResponse({'code': 200})
        return JsonResponse({'code': 201, 'message': '获取二维码支付失败'})


# 微信支付回调接口
class WXPayResultView(View):
    """
       微信支付结果回调通知路由
       """
    def post(self, request, *args, **kwargs):
        """
        微信支付成功后会自动回调
        返回参数为：
        {'mch_id': '',
        'time_end': '',
        'nonce_str': '',
        'out_trade_no': '',
        'trade_type': '',
        'openid': '',
         'return_code': '',
         'sign': '',
         'bank_type': '',
         'appid': '',
         'transaction_id': '',
          'cash_fee': '',
          'total_fee': '',
          'fee_type': '', '
          is_subscribe': '',
          'result_code': 'SUCCESS'}

        :param request:
        :param args:
        :param kwargs:
        :return:
        {'appid': 'wx671cf8e9e558311d', 'bank_type': 'OTHERS', 'cash_fee': '1', 'fee_type': 'CNY', 'is_subscribe': 'N', 'mch_id': '1563321261', 'nonce_str': 'JyUTswsN', 'openid': 'o6c-m5MjAKXs0NnEiZFvstp8ldDE', 'out_trade_no': '202004141746562', 'result_code': 'SUCCESS', 'return_code': 'SUCCESS', 'sign': '8223A317C11A3623591A821155E17E14', 'time_end': '20200416142245', 'total_fee': '1', 'trade_type': 'NATIVE', 'transaction_id': '4200000567202004164348898872'}

        """
        data_dict = trans_xml_to_dict(request.body)  # 回调数据转字典
        print('支付回调结果', data_dict)
        sign = data_dict.pop('sign')  # 取出签名
        back_sign = get_sign(data_dict, API_KEY)  # 计算签名
        # 验证签名是否与回调签名相同
        if sign == back_sign and data_dict['return_code'] == 'SUCCESS':
            '''
            检查对应业务数据的状态，判断该通知是否已经处理过，如果没有处理过再进行处理，如果处理过直接返回结果成功。
            '''
            print('微信支付成功会回调！')
            # 处理支付成功逻辑
            # 返回接收结果给微信，否则微信会每隔8分钟发送post请求
            return HttpResponse(trans_dict_to_xml({'return_code': 'SUCCESS', 'return_msg': 'OK'}))
        return HttpResponse(trans_dict_to_xml({'return_code': 'FAIL', 'return_msg': 'SIGNERROR'}))