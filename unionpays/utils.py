import base64
import hashlib
import requests
import OpenSSL

from datetime import datetime
from urllib import parse


# 银联支付参数配置
class UnionPayConfig(object):

    # 银联版本号(固定)
    version = "5.1.0"

    # 商户ID(配置项)
    mer_id = "777290058180759"  # 你的商户id  （正式生产环境需修改）

    # 前台回调地址(支付成功回调成功)(配置项)（正式生产环境需修改）
    front_url = "http://127.0.0.1:8080/pay/uni_back/"  # http://公网IP/back/

    # 后台回调地址(配置项)（正式生产环境需修改）
    back_url = "http://127.0.0.1:8080/pay/uni_notify/"  # http://公网IP/notify/

    # 证书地址(配置项)（正式生产环境需修改）
    cert_path = "C:/project/django_pays/unionpays/acp_test_sign.pfx"

    # 证书解密密码(根据实际去调配)(配置项) （正式生产环境需修改）
    cert_password = "000000"

    # 是否开启测试模式(默认False)(配置项)（正式生产环境为False）
    debug = True


class UnionPay:
    """
    银联支付接口（PC端）
    """
    def __init__(
            self,
            version,
            mer_id,
            front_url,
            back_url,
            backend_url,
            cert_path,
            debug=False
    ):
        self.version = version
        self.mer_id = mer_id
        self.front_url = front_url
        self.back_url = back_url
        self.backend_url = backend_url
        self.cert = {}
        self.cert_id = self.__get_cert_id(cert_path)

        if debug is True:
            # 支付网关
            self.gateway = "https://gateway.test.95516.com/gateway/api/frontTransReq.do"
            # 查询网关
            self.query_gateway = "https://gateway.test.95516.com/gateway/api/queryTrans.do"
        else:
            self.gateway = "https://gateway.95516.com/gateway/api/frontTransReq.do"
            self.query_gateway = "https://gateway.95516.com/gateway/api/queryTrans.do"

    def build_request_data(self, order_id, txn_amt, **kwargs):
        """
        构建请求数据
        :param order_id: 商户订单号
        :param txn_amt: 交易金额(单位: 分)
        :return:
        """
        request_data = {
            "version": self.version,  # 版本
            "encoding": "utf-8",  # 编码
            "txnType": "01",  # 交易类型  01：消费
            "txnSubType": "01",  # 交易子类  01：自助消费
            "bizType": "000201",  # 产品类型  000201：B2C网关支付
            "frontUrl": self.front_url,  # 前台通知地址
            "backUrl": self.back_url,  # 后台通知地址 需外网
            "signMethod": "01",  # 签名方法  01：RSA签名
            "channelType": "07",  # 渠道类型  07：互联网
            "accessType": "0",  # 接入类型  0：普通商户直连接入
            "currencyCode": "156",  # 交易币种  156：人民币
            "merId": self.mer_id,  # 商户代码
            "txnAmt": txn_amt,  # 订单金额(单位: 分)
            "txnTime": datetime.now().strftime("%Y%m%d%H%M%S"),  # 订单发送时间
            "certId": self.cert_id,
            "orderId": order_id,
            "signature": ""
        }
        request_data.update(**kwargs)
        self.get_sign(request_data)
        return request_data

    def pay_url(self, request_data):
        payment_url = "{}?{}".format(self.backend_url, parse.urlencode(request_data))
        return payment_url

    def pay_html(self, request_data):
        result = """<html>
             <head>
                 <meta http-equiv="Content-Type" content="text/html"charset="utf-8"/>
             </head>
             <body onload="pay_form.submit();">
                 <form id="pay_form" name="pay_form" action="{}" method="post">""".format(self.gateway)
        for key, value in request_data.items():
            result += """<input type="hidden" name="{0}" id="{0}" value="{1}"/>""".format(key, value)
        result = result + """<!-- <input type="submit" type="hidden">--></form></body></html>"""
        return result

    def get_sign(self, data):
        """
        获取签名
        :param data:
        :return:
        """
        sha256 = hashlib.sha256(self.build_sign_str(data).encode("utf-8")).hexdigest()
        private = OpenSSL.crypto.sign(self.cert["pkey"], sha256, "sha256")
        data["signature"] = str(base64.b64encode(private), encoding="utf-8")

    def verify_sign(self, data):
        """
        银联回调签名校验
        """
        signature = data.pop('signature')  # 获取签名
        link_string = self.build_sign_str(data)
        digest = hashlib.sha256(bytes(link_string, encoding="utf-8")).hexdigest()
        signature = base64.b64decode(signature)
        sign_pubkey_cert = data.get("signPubKeyCert", None)

        try:
            x509_ert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, sign_pubkey_cert)
            OpenSSL.crypto.verify(x509_ert, signature, digest, 'sha256')
            return True
        except Exception as exc:
            return False

    def verify_query(self, order_num, txn_time):
        '''
        验证查询的交易状态
        :param order_num: 订单号
        :param txn_time: 交易时间
        :return: True or False
        '''
        request_data = {
            "version": self.version,
            "encoding": "utf-8",
            "txnType": "00",  # 00:查询
            "txnSubType": "00",
            "bizType": "000202",
            "signMethod": "01",  # 签名方法  01：RSA签名
            "accessType": "0",
            "merId": self.mer_id,
            "txnTime": txn_time,
            "orderId": order_num,
            "certId": self.cert_id,
        }

        self.get_sign(request_data)
        request_data['signature'] = parse.urlencode({'signature': request_data['signature']})[10:]
        req_string = self.build_sign_str(request_data)

        res = requests.post(
            url=self.query_gateway,
            data=req_string,
            headers={
                'content-type': 'application/x-www-form-urlencoded'
            }
        )
        if res.status_code != requests.codes.ok:
            query_status = False
        else:
            content = self.parse_arguments(res.content.decode('utf-8'))
            if content.get('origRespCode', '') == '00':
                query_status = True
            else:
                query_status = False
        return query_status

    def __get_cert_id(self, cert_path):
        """
        获取证书ID(签名KEY)
        :param cert_path:
        :return:
        """
        with open(cert_path, "rb") as f:
            certs = OpenSSL.crypto.load_pkcs12(f.read(), UnionPayConfig.cert_password)
            x509data = certs.get_certificate()
            self.cert["certid"] = x509data.get_serial_number()
            self.cert["pkey"] = certs.get_privatekey()

        return self.cert["certid"]

    @staticmethod
    def build_sign_str(data):
        """
        排序
        :param data:
        :return:
        """
        req = []
        for key in sorted(data.keys()):
            if data[key] != '':
                req.append("%s=%s" % (key, data[key]))

        return '&'.join(req)

    @staticmethod
    def parse_arguments(raw):
        """
        :param raw: raw data to parse argument
        :return:
        """
        data = {}
        qs_params = parse.parse_qs(str(raw))
        for name in qs_params.keys():
            data[name] = qs_params.get(name)[-1]
        return data

# 获取一个unionpay对象
def get_uni_object():
    uni_pay = UnionPay(
        version=UnionPayConfig.version,
        mer_id=UnionPayConfig.mer_id,
        front_url=UnionPayConfig.front_url + "/",
        back_url=UnionPayConfig.back_url + "/",
        backend_url=UnionPayConfig.back_url,
        cert_path=UnionPayConfig.cert_path,
        debug=UnionPayConfig.debug,
    )
    return uni_pay