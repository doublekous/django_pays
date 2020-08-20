from django.http import HttpResponse
from django.views import View
from unionpays.utils import get_uni_object

# 银联支付(pc端)
# 这里测试直接写支付金额和订单号，正式环境根据真实业务环境修改


# 银联充值接口
# 银联充值接口
class UnionpaysView(View):

    def get(self, request):
        money = float(request.GET.get('money'))
        order_id = request.GET.get('order_id')
        unipay = get_uni_object()

        query_params = unipay.build_request_data(
            order_id='202006221429001', # 用户购买的商品订单号，根据自己业务环境自己设定
            txn_amt=int(float(money) * 100) # 交易金额 单位是分
        )
        pay_html = unipay.pay_html(query_params)
        rsp = HttpResponse()
        rsp.content = pay_html
        return rsp


# 充值成功前台回调（银联）
class UniBackView(View):
    def post(self, request):
        params = request.POST.dict()
        unipay = get_uni_object()
        res = unipay.verify_sign(params)
        if res:
            if unipay.verify_query(params['orderId'], params['txnTime']):  # 再次查询状态
                print('====1=======')
                return HttpResponse('充值成功')

        else:
            return HttpResponse('充值失败')


# 充值成功后后台回调（银联）

class UniNotifyView(View):
    def post(self, request):
        params = request.POST.dict()
        unipay = get_uni_object()
        res = unipay.verify_sign(params)
        print(res)
        if res:
            status = unipay.verify_query(params['orderId'], params['txnTime'])  # 再次查询状态

            if status:
                try:
                    print('===============')
                    return HttpResponse('ok')
                except Exception as e:
                    raise e
        else:
            return HttpResponse('')

    def get(self, request):
        params = request.GET.dict()
        for k, v in params.items():
            print(k, v, '\n')
        return HttpResponse('failed')