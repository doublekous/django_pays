## 这个demo集成了在django框架开发中调用pc端调用支付宝官方sdk接口，微信native模式支付接口，中国银联网关支付接口

## 提前说明，避免踩坑
 - 如果是windows系统接入支付宝提供的官方sdk库alipay-sdk-python 会报错
 ```
 请先去https://pan.baidu.com/s/1Bz8zB2et71xxyTaCUuU36A 下载之后，选择我们需要的组件进行安装 坑二：这里需要设置用户变量（不是系统变量） 变量名称：VCINSTALLDIR 变量值：C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC 坑三：按照此操作执行pip install pycrypto 任然会报错，请在项目环境变量执行set CL=/FI"C:\Program Files (x86)\Microsoft Visual Studio 14.0\VC\\INCLUDE\stdint.h" %CL% 完成上述步骤之后，重新安装pycrypto命令，就应该不会有问题了 安装官方SDK：pip install alipay-sdk-python
 ```
 - 三种支付方式参数申请，这里不做详细说明，请自行到对应开放平台申请

## 使用说明：
```python
    git clone https://github.com/doublekous/django_pays.git
    填写各种支付平台申请到的支付参数
    python manage.py runserver 0.0.0.0:8000
```

## 具体各支付文档
- django接入微信小程序支付请点[我](http://123.56.7.28/article/2020/3/24/4.html)
- django接入微信native支付请点[我](http://123.56.7.28/article/2020/3/24/3.html)
- django接入支付宝支付请点[我](http://123.56.7.28/article/2020/3/24/4.html)