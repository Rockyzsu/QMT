# -*- coding: utf-8 -*-
# author公众号：可转债量化分析
import requests

TOKEN = "123456789"


class QMTClient:
    def __init__(self, base_url="http://127.0.0.1:10086"):
        self.base = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json; charset=utf-8"})
        self.session.headers.update({"X-Token": TOKEN})

    def _req(self, method, path, **kwargs):
        url = f"{self.base}{path}"
        try:
            resp = self.session.request(method, url, timeout=10, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', 500)}

    def get_holding(self, account='stock'):
        return self._req('GET', f'/api/holding?account={account}')

    def get_total_money(self, account='stock'):
        return self._req('POST', f'/api/money/total', json={"account": account})

    def get_available_money(self, account='stock'):
        return self._req('POST', f'/api/money/available', json={"account": account})

    def buy_stock(self, stock, price, volume, pr_type=11):
        """
        prType(下单选价类型):（特别的对于套利：这个prType只对篮子起作用,期货的采用默认的方式）
        -1:无效(只对于algo_passorder起作用)
        0:卖5价
        1:卖4价
        2:卖3价
        3:卖2价
        4:卖1价
        5:最新价
        6:买1价
        7:买2价(组合不支持)
        8:买3价(组合不支持)
        9:买4价(组合不支持)
        10:买5价(组合不支持)
        11:（指定价）模型价（只对单股情况支持,对组合交易不支持）
        12:涨跌停价
        13:挂单价
        14:对手价
        18:市价最优价[郑商所][期货]
        19:市价即成剩撤[大商所][期货]
        20:市价全额成交或撤[大商所][期货]
        21:市价最优一档即成剩撤[中金所][期货]
        22:市价最优五档即成剩撤[中金所][期货]
        23:市价最优一档即成剩转[中金所][期货]
        24:市价最优五档即成剩转[中金所][期货]
        26:限价即时全部成交否则撤单[上交所|深交所][期权]
        27:市价即成剩撤[上交所][期权]
        28:市价即全成否则撤[上交所][期权]
        29:市价剩转限价[上交所][期权]
        42:最优五档即时成交剩余撤销申报[上交所][股票]
        43:最优五档即时成交剩转限价申报[上交所][股票]
        44:对手方最优价格委托[上交所[股票]][深交所[股票][期权]]
        45:本方最优价格委托[上交所[股票]][深交所[股票][期权]]
        46:即时成交剩余撤销委托[深交所][股票][期权]
        47:最优五档即时成交剩余撤销委托[深交所][股票][期权]
        48:全额成交或撤销委托[深交所][股票][期权]
        49:盘后定价
        :param stock:
        :param price:
        :param volume:
        :param pr_type:
        :return:
        """
        return self._req('POST', '/api/order/buy', json={
            "stock": stock, "price": price, "volume": volume, "prType": pr_type
        })

    def sell_stock(self, stock, price, volume, pr_type=11):
        return self._req('POST', '/api/order/sell', json={
            "stock": stock, "price": price, "volume": volume, "prType": pr_type
        })

    def get_sector(self, sector):
        return self._req('POST', '/api/data/sector', json={
            "sector": sector,
        })

    def get_industry(self, industry):
        return self._req('POST', '/api/data/industry', json={
            "industry": industry,
        })

    def get_full_tick(self, stocks):
        return self._req('POST', f'/api/data/full_tick', json={
            "stocks": stocks})

    def get_market_data_ex(self, stocks: list[str]):
        return self._req('POST', f'/api/data/market_data_ex', json={
            "stocks": stocks})

    def get_order_status(self, account='stock'):
        """
        EEntrustStatus //委托状态
        ENTRUST_STATUS_WAIT_END: 0 //委托状态已经在 ENTRUST_STATUS_CANCELED 或以上，但是成交数额还不够，等成交回报来
        ENTRUST_STATUS_UNREPORTED: 48 //未报
        ENTRUST_STATUS_WAIT_REPORTING: 49 //待报
        ENTRUST_STATUS_REPORTED: 50 //已报
        ENTRUST_STATUS_REPORTED_CANCEL: 51 //已报待撤
        ENTRUST_STATUS_PARTSUCC_CANCEL: 52 //部成待撤
        ENTRUST_STATUS_PART_CANCEL: 53 //部撤
        ENTRUST_STATUS_CANCELED: 54 //已撤
        ENTRUST_STATUS_PART_SUCC: 55 //部成
        ENTRUST_STATUS_SUCCEEDED: 56 //已成
        ENTRUST_STATUS_JUNK: 57 //废单
        ENTRUST_STATUS_DETERMINED: 86 //已确认
        ENTRUST_STATUS_UNKNOWN: 255 //未知
        :return:
        """
        params = {"account": account}
        query = "&".join([f"{k}={v}"for k, v in params.items()])
        return self._req('GET', f'/api/order/status?{query}')

    def cancel_all_orders(self, account='stock'):
        """
        危险操作：一键撤销所有活跃状态的订单
        """
        return self._req('POST', f'/api/order/cancel_all', json={"account": account})

    def cancel_order(self, stock, volume, account='stock'):
        """
        根据股票代码和未成交数量撤单。
        请注意：如果该股票有多笔未成交数量相同的订单，会被全部撤销！
        """
        return self._req('POST', '/api/order/cancel_order', json={
            "stock": stock,
            "volume": volume,
            "account": account
        })

    def python_version(self):
        """
        获取 Python 版本信息
        """
        return self._req('GET', '/api/sys/python_version')

    def close(self):
        """
        关闭整个 QMT HTTP 服务
        """
        return self._req('POST', '/api/sys/shutdown')


# ============= 测试示例 =============
def unit_test():
    client = QMTClient()
    account_type = "stock"  # 根据实际账户调整

    # # 1. 查询资金
    # print("[1] 总资金:", client.get_total_money(account_type))
    # print("[2] 可用资金:", client.get_available_money(account_type))

    # # 2. 查询持仓
    # print("[3] 持仓信息:", json.dumps(client.get_holding(account_type), indent=2, ensure_ascii=False))

    # orders = client.get_order_status()
    # print(orders)

    # print(client.python_version()) # 返回qmt python 版本信息

    # client.close()

    # print(client.get_sector('000300.SH'))
    # print(client.get_industry('CSRC餐饮业'))
    # print(client.get_market_data_ex(['600000.SH', '000001.SZ']))
    print(client.get_full_tick('600000.SH'))
    # client.buy_stock("600000.SZ", 6.80, 100)


if __name__ == "__main__":

    unit_test()
