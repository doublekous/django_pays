from datetime import datetime
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views import View
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest

from alipays.utils import check_pay
from django_pays import settings


# 此处为支付宝支付demo接口，订单号和金额直接给出，正式环境集合业务逻辑自行设计
class OrderALIPayView(View):
    def get(self, request):
        order_id = request.GET.get('order_id')
        money = request.GET.get('money')
        # 业务逻辑处理
        try:
            # 调用支付宝流程
            alipay_client_config = AlipayClientConfig()  # 创建配置对象
            alipay_client_config.server_url = settings.ALIPAY_URL  # 网关
            alipay_client_config.app_id = settings.ALIPAY_APPID  # APPID
            alipay_client_config.app_private_key = settings.APP_PRIVATE_KEY  # 应用私钥
            client = DefaultAlipayClient(alipay_client_config=alipay_client_config)  # 使用配置创建客户端
            model = AlipayTradePagePayModel()  # 创建网站支付模型
            model.out_trade_no = order_id  # 商户订单号码
            model.total_amount = str(1)  # 支付总额
            model.subject = '订单标题'  # 订单标题
            model.body = '订单描述'  # 订单描述
            model.product_code = 'FAST_INSTANT_TRADE_PAY'  # 与支付宝签约的产品码名称，目前只支持这一种。
            model.timeout_express = '30m'  # 订单过期关闭时长（分钟）
            pay_request = AlipayTradePagePayRequest(biz_model=model)  # 通过模型创建请求对象
            pay_request.notify_url = settings.ALIPAY_NOTIFY_URL  # 设置回调通知地址（POST）
            # pay_request.notify_url = None  # 设置回调通知地址（POST）
            pay_request.return_url = settings.ALIPAY_RETURN_URL # 设置回调通知地址（GET）
            # pay_request.return_url = None  # 设置回调通知地址（GET）

            response = client.page_execute(pay_request, http_method='GET')  # 获取支付链接
            pay_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            return HttpResponseRedirect(response)  # 重定向到支付宝支付页面
        except Exception as e:
            print(e)
            return JsonResponse({'code': 201, 'message': '支付失败，请重新支付'})


class OrderALIPayResultView(View):
    def get(self, request):
        params = request.GET.dict()  # 获取参数字典
        if check_pay(params):  # 调用检查支付结果的函数
            '''
                此处编写支付成功后的业务逻辑
            '''
            print('支付成功')
            print(params.get('out_trade_no'))
            return HttpResponse('支付成功！')
        else:
            '''
                此处编写支付失败后的业务逻辑
            '''
            return HttpResponse('支付失败！')

    def post(self, request):
        params = request.POST.dict()  # 获取参数字典
        if check_pay(params):  # 调用检查支付结果的函数
            '''
                此处编写支付成功后的业务逻辑
            '''
            print('支付成功！')
            return HttpResponse('success')  # 返回成功信息到支付宝服务器
        else:
            '''
                此处编写支付失败后的业务逻辑
            '''
            print('支付失败')
            return HttpResponse('')