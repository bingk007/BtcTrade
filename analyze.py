#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  @author: WuBingBing

import requ
import common
import time
import heapq
import datetime

class Analyze:

    def time_change(self,BuyTime):
        timestamp = float(BuyTime) / 1000
        creat = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        creatTime = datetime.datetime.strptime(creat, '%Y-%m-%d %H:%M:%S')
        return creatTime

    def cancel_order(self,exCoin,tradetype,tradeTime,time_seconds):
        if (common.Common().get_time() - self.time_change(tradeTime)).total_seconds() > time_seconds:
            requ.Requ().cancel_order(exCoin,tradetype)

    def sell_times(self,BuyTime):
        sell_times = (common.Common().get_time() - self.time_change(BuyTime)).total_seconds() / 86400
        if sell_times > 10:
            return 0.1
        else:
            return int(sell_times) * 0.01

    def average_prcie(self, price_list):
        Lagest = heapq.nlargest(5, price_list)
        Smallest = heapq.nsmallest(5, price_list)
        LS = Lagest + Smallest
        newList = list(set(price_list) ^ set(LS))
        Average = sum(newList) / len(newList)
        return Average

    def analyze_data(self,exCoin,coin):
        tradeType = None
        ListTimes = []
        UpListTimes = []
        TurnTimes = []
        # LatestTimes = []
        OneHour = []
        TenChange = []
        BtcMonthChange = []

        while True:
            try:
                time.sleep(10)
                print('')
                print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))

                curr = requ.Requ().get_curr_order(exCoin,"buy-limit")
                filled = requ.Requ().get_filled_buy_order(exCoin,coin)
                if (curr != []) and (filled != [[],[]]):
                    filled[1].append(curr[2])
                    BuyPrice = filled[1]
                    filled[0].append(curr[1])
                    BuyTime = filled[0]
                    self.cancel_order(exCoin,"buy-limit",BuyTime[len(BuyTime)-1],1800)
                elif curr != []:
                    BuyPrice = [curr[2]]
                    BuyTime = [curr[1]]
                    self.cancel_order(exCoin,"buy-limit",BuyTime[len(BuyTime)-1],1800)
                elif filled != [[],[]]:
                    BuyPrice = filled[1]
                    BuyTime = filled[0]
                else:
                    BuyPrice = []
                    BuyTime = []

                curr_sell = requ.Requ().get_curr_order(exCoin,"sell-limit")
                if curr_sell != []:
                    self.cancel_order(exCoin,"sell-limit",curr_sell[1],3600)

                if BuyPrice != []:
                    MaxBuyPrice = max(list(map(float, BuyPrice)))
                else:
                    MaxBuyPrice = []

                ListPrice = requ.Requ().get_data(exCoin, '5min', '300')
                print("LastPrice:" + str(ListPrice[len(ListPrice)-1]))

                BtcPriceOneMonth = requ.Requ().get_data('btcusdt', '60min', '730')
                BtcOneMonthAverage = self.average_prcie(BtcPriceOneMonth)
                print("BtcOneMonthAverage:" + str(BtcOneMonthAverage))
                if BtcPriceOneMonth[len(BtcPriceOneMonth) - 1] <= BtcOneMonthAverage:
                    BtcMonthChange.append('1')
                else:
                    BtcMonthChange.append('0')

                if len(BtcMonthChange) > 1:
                    del BtcMonthChange[0]

                ListPriceTenDay = requ.Requ().get_data(exCoin, '60min', '250')
                tenDayAverage = self.average_prcie(ListPriceTenDay)
                print("TenDayAverage:" + str(tenDayAverage))
                if ListPriceTenDay[len(ListPriceTenDay)-1] <= tenDayAverage:
                    TenChange.append('1')
                else:
                    TenChange.append('0')

                if len(TenChange) > 1:
                    del TenChange[0]

                turnChange = ListPrice[len(ListPrice)-1] - ListPrice[len(ListPrice)-2]
                if turnChange > 0:
                    TurnTimes.append('1')
                elif turnChange < 0:
                    TurnTimes.append('-1')
                else:
                    TurnTimes.append('0')
                print("TurnPoint:" + str(turnChange))

                if len(TurnTimes) > 1:
                    del TurnTimes[0]

                ListPriceOneHour = requ.Requ().get_data(exCoin, '1min', '70')
                hourAverage = self.average_prcie(ListPriceOneHour)
                print("OneHourAverage:" + str(hourAverage))
                oneHourChangeRate = round((ListPriceOneHour[len(ListPriceOneHour)-1] - hourAverage) / hourAverage,4)
                if oneHourChangeRate >= 0.03:
                    OneHour.append('-1')
                else:
                    OneHour.append('0')
                print("OneHourRate:" + str(oneHourChangeRate))

                if len(OneHour) >1:
                    del OneHour[0]

                day_average = self.average_prcie(ListPrice)
                print("DayAverage:" + str(day_average))
                rateChange = (ListPrice[len(ListPrice)-1] - day_average) / day_average
                print("UpAndDwonRate:"+str(rateChange))

                if BuyPrice != []:
                    buyChange = (ListPrice[len(ListPrice)-1] - MaxBuyPrice) / MaxBuyPrice
                    print("WinBi:" + str(buyChange))
                    if (buyChange > (0.06 + self.sell_times(BuyTime[0]))) and (rateChange > -0.05):
                        UpListTimes.append('1')
                    else:
                        UpListTimes.append('0')
                if len(UpListTimes) > 1:
                    del UpListTimes[0]

                if UpListTimes.count('1') >= 1:
                    if TurnTimes.count('-1') >= 1 or OneHour.count('-1') >=1:
                        tradeType = '-1'
                        break

                if rateChange < -0.05 and ListPrice.index(max(ListPrice)) < ListPrice.index(min(ListPrice)):
                    if len(BuyTime) >=2:
                        ListTimes.append('0')
                    elif BuyTime == []:
                        ListTimes.append('-1')
                    elif (ListPrice[len(ListPrice)-1] - float(BuyPrice[len(BuyPrice)-1])) / float(BuyPrice[len(BuyPrice)-1]) < -0.10:
                        ListTimes.append('-1')
                    else:
                        ListTimes.append('0')
                else:
                    ListTimes.append('0')

                if len(ListTimes) > 1:
                    del ListTimes[0]

                if ListTimes.count('-1') >= 1 and TurnTimes.count('1') >= 1 and TenChange.count('1') >=1 and BtcMonthChange.count('1') >= 1:
                    tradeType = '1'
                    break

            except Exception as ex:
                print(Exception,":",ex )
                continue

        if tradeType == '1':
            print("Meet the buy requirements!")
            tradePriceBuy = str(round(ListPrice[len(ListPrice) - 1], requ.Requ().get_jingdu(coin, 'price-precision')))
            if float(requ.Requ().account('usdt')) >= 1:
                requ.Requ().trade('usdt',exCoin,'buy-limit', tradePriceBuy)
                print("buy:"+coin)

        elif tradeType == '-1':
            print("Meet the sell requirements!")
            tradePriceSell = str(round(ListPrice[len(ListPrice) - 1], requ.Requ().get_jingdu(coin, 'price-precision')))
            n = requ.Requ().get_jingdu(coin,'amount-precision')
            if float(requ.Requ().account(coin)) >= 10**-n:
                requ.Requ().trade(coin,exCoin,'sell-limit', tradePriceSell)
                print("sell:"+coin)
        else:
            print("exception,exception!")






