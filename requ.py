#!/usr/bin/env python
# -*- coding: utf-8 -*-

#  @author: WuBingBing

import requests
import re
import config
import time
import urllib3
import HuobiServices
import json
# import requests.packages.urllib3.util.ssl_
# import ssl
# requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
# ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Requ:

    def get_data(self, exCoin, period, size):
        try:
            List_data = []
            for i in range(3):
                try:
                    rq_data = HuobiServices.get_kline(exCoin, period, size)
                except:
                    continue
                if rq_data.find('"status":"ok"') != -1:
                    market = json.loads(rq_data)['data']
                    break
                else:
                    print("data,data,data")
                    print(rq_data)
                    time.sleep(5)
            for i in market:
                List_data.append(float(i['close']))
            return list(reversed(List_data))
        except Exception as ex:
            print(Exception, ":", ex)
            return

    def get_jingdu(self,coin,precision_type):
        try:
            for i in range(3):
                try:
                    rq_jingdu = HuobiServices.get_symbols()
                except:
                    continue
                if rq_jingdu.find('"status":"ok"') != -1:
                    jingdu = json.loads(rq_jingdu)['data']
                    break
                else:
                    print("jingdu,jingdu,jingdu")
                    time.sleep(5)
            for i in jingdu:
                if i['base-currency'] == coin and i['quote-currency'] == 'usdt':
                    amount = i[precision_type]
                    return int(amount)
                    break
        except Exception as ex:
            print(Exception, ":", ex)
            return

    def account(self,coin):
        try:
            for i in range(3):
                try:
                    rq_acc = HuobiServices.get_balance('443597')
                except:
                    continue
                if rq_acc.find('"status":"ok"') != -1:
                    l = re.search('"currency":"' + coin + '","type":"trade","balance":"(.+?)"', rq_acc).group(1)
                    break
                else:
                    print("accout,accout")
                    time.sleep(5)
            return l
        except Exception as ex:
            print(Exception, ":", ex)
            return

    def get_coin_amount(self,coin,exCoin):
        try:
            l = self.account(coin)
            if coin == 'usdt':
                for i in range(5, 0, -1):
                    ls = float(l)/i
                    if ls > 320:
                        break
                priceList = self.get_data(exCoin, '1min', '1')
                num = str(ls/priceList[len(priceList)-1])
                if self.get_jingdu(exCoin[:-4],'amount-precision') == 0:
                    coin_amount = num.split('.')[0]
                else:
                    coin_amount = num.split('.')[0] + '.' + num.split('.')[1][0:self.get_jingdu(exCoin[:-4], 'amount-precision')]
            else:
                if self.get_jingdu(coin,'amount-precision') == 0:
                    coin_amount = l.split('.')[0]
                else:
                    coin_amount = l.split('.')[0] + '.' + l.split('.')[1][0:self.get_jingdu(coin, 'amount-precision')]
            return coin_amount
        except Exception as ex:
            print(Exception, ":", ex)
            return

    def get_curr_order(self,exCoin,tradetype):
        try:
            for i in range(3):
                try:
                    rq_ord_curr = HuobiServices.orders_list(exCoin, 'submitted,partial-filled', None, '2018-07-01', None, None, 'next', None)
                except Exception as ex:
                    print(Exception, ":", ex)
                    continue
                if rq_ord_curr.find('"status":"ok"') != -1:
                    break
                else:
                    print("order_curr,order_curr")
                    time.sleep(5)
            if rq_ord_curr.find(tradetype) != -1:
                orders = json.loads(rq_ord_curr)['data']
                for i in orders:
                    if str(i).find("'type': '"+tradetype+"'") != -1:
                        order_id = i['id']
                        creat_time = i['created-at']
                        set_price = i['price']
                        break
                return [str(order_id),str(creat_time),str(set_price)]
            else:
                return []
        except Exception as ex:
            print(Exception, ":", ex)
            return

    def get_filled_buy_order(self,exCoin,coin):
        try:
            buy_time = []
            buy_price = []
            for i in range(3):
                try:
                    rq_ord_filled = HuobiServices.orders_matchresults(exCoin, None, '2018-07-01', None, None, 'next', None)
                except Exception as ex:
                    print(Exception, ":", ex)
                    continue
                if rq_ord_filled.find('"status":"ok"') != -1:
                    orders = json.loads(rq_ord_filled)['data']
                    break
                else:
                    print("order_fill,order_fill")
                    print(rq_ord_filled)
                    time.sleep(5)
            for i in orders:
                if str(i).find("'type': 'sell-limit'") != -1:
                    if orders.index(i) == 0 and float(self.account(coin)) > 1:
                        continue
                    else:
                        break
                elif str(i).find("'type': 'buy-limit'") != -1:
                    creat_time = i['created-at']
                    buy_time.append(str(creat_time))
                    set_price = i['price']
                    buy_price.append(str(set_price))
            return [list(reversed(buy_time)),list(reversed(buy_price))]
        except Exception as ex:
            print(Exception, ":", ex)
            return

    def cancel_order(self,exCoin,tradetype):
        try:
            for i in range(3):
                try:
                    rq_ord_cancel = HuobiServices.cancel_order(self.get_curr_order(exCoin,tradetype)[0])
                except Exception as ex:
                    print(Exception, ":", ex)
                    continue
                if rq_ord_cancel.find('"status":"ok"') != -1:
                    break
                else:
                    print("cancel_order,cancel_order")
                    time.sleep(5)
        except Exception as ex:
            print(Exception, ":", ex)
            return

    def trade(self, coin, exCoin, tradeType, tradePrice):
        try:
            for i in range(3):
                try:
                    rq_tra = HuobiServices.send_order(self.get_coin_amount(coin,exCoin), 'spot-app', exCoin, tradeType, tradePrice)
                except Exception as ex:
                    print(Exception, ":", ex)
                    continue
                if rq_tra.find('"status":"ok"') != -1:
                    print(rq_tra)
                    break
                else:
                    print("trade,trade 11")
                    time.sleep(5)
        except Exception as ex:
            print(Exception, ":", ex)
            return

