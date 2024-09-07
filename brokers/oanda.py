import datetime
from oandapyV20 import API
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.accounts as accounts


def sort_by_date(dic):
    return dic["date"]


def oanda_import(api_key, account_ID):
    return_value = []
    params = {"beforeID": 500000, "state": "ALL", "count": 500}
    try:
        r = accounts.AccountList()
        Client = API(environment='live', access_token=api_key)
        Client.request(r)
        for i in r.response['accounts']:
            resp = trades.TradesList(i['id'], params=params)
            tradesList = Client.request(resp)
            j = 0
            while j < len(tradesList['trades']):
                j += 1
                trade = tradesList["trades"][j * -1]
                found = False
                if float(trade["realizedPL"]) == 0:
                    continue
                else:
                    if float(trade["realizedPL"]) > 0:
                        status = "WIN"
                    else:
                        status = "LOSS"
                instrument = '$' + trade['instrument'].replace('_', '')
                if not 'averageClosePrice' in trade:
                    continue
                if float(trade['realizedPL']) > 0:
                    if float(trade['price']) > float(trade['averageClosePrice']):
                        side = "SHORT"
                    else:
                        side = "LONG"
                else:
                    if float(trade['price']) < float(trade['averageClosePrice']):
                        side = "SHORT"
                    else:
                        side = "LONG"
                if side == 'LONG':
                    action = 'Buy'
                    action_2 = 'Sell'
                else:
                    action = 'Sell'
                    action_2 = 'Buy'
                pips = (float(trade['averageClosePrice']) -
                        float(trade['price'])) * float(trade['initialUnits']) * 100
                if action == 'Buy':
                    return_percent = abs(float(
                        trade["realizedPL"]) * 500 / float(trade["price"]) / (float(trade["realizedPL"]) / pips) / float(trade["initialUnits"]))
                else:
                    return_percent = abs(float(
                        trade["realizedPL"]) * 500 / float(trade["averageClosePrice"]) / (float(trade["realizedPL"]) / pips) / float(trade["initialUnits"]))
                if (float(trade["realizedPL"]) < 0):
                    return_percent = 0 - return_percent
                for appended in return_value:
                    sub_F = appended["subs"][0]
                    sub_L = appended['subs'][-1]
                    if appended['symbol'] == instrument and datetime.datetime.fromisoformat(trade['openTime'][0:26]) < datetime.datetime.fromisoformat(sub_L['date'][0:26]) and datetime.datetime.fromisoformat(trade['openTime'][0:26]) > datetime.datetime.fromisoformat(sub_F['date'][0:26]):
                        appended['ret'] = str(
                            float(appended['ret']) + float(trade['realizedPL']))
                        appended['ret_net'] = str(
                            float(appended['ret_net']) + float(trade['realizedPL']))
                        appended['size'] = str(
                            float(appended['size']) + float(trade["initialUnits"]))
                        appended['pips'] = str(
                            format(float(appended['pips']) + pips, '.2f'))
                        appended["ret_pips"] = str(
                            format(float(appended['ret']) / abs(float(appended['pips'])), '.10f'))
                        if float(appended['ret']) > 0:
                            appended['status'] = "WIN"
                        else:
                            appended['status'] = "LOSS"
                        new_subs = [{"action": action, "spread": "SINGLE", "type": "FOREX", "date": trade["openTime"], "size": str(abs(float(trade["initialUnits"]))), "position": "", "price": trade["price"]}, {
                            "action": action_2, "spread": "SINGLE", "type": "FOREX", "date": trade["closeTime"], "size": str(abs(float(trade["initialUnits"]))), "position": "", "price": trade["averageClosePrice"]}]
                        appended['subs'].extend(new_subs)
                        appended['subs'].sort(key=sort_by_date)
                        temp = 0
                        for fixing in appended['subs']:
                            if temp == 0:
                                openPrice = fixing['price']
                            if fixing['action'] == 'Buy':
                                temp += float(fixing['size'])
                            else:
                                temp -= float(fixing['size'])
                            fixing['position'] = str(format(temp, '.2f'))
                        appended['exit'] = appended['subs'][-1]['price']
                        found = True
                        appended["ret_percent"] = str(format(abs(float(appended["ret"]) * 500 / float(openPrice) / (
                            float(appended["ret"]) / float(appended['pips'])) / float(appended["size"])), '.5f'))
                        if float(appended['ret']) < 0:
                            appended['ret_percent'] = "-" + \
                                appended['ret_percent']
                        break
                if found == True:
                    continue
                return_value.append(
                    {"account_id": account_ID, "broker": "Oanda", "trade_id": trade["id"], "status": status, "open_date": trade["openTime"], "symbol": instrument, "entry": trade["price"], "exit": trade["averageClosePrice"], "size": trade["initialUnits"], "pips": str(format(pips, '.5f')), "ret_pips": str(format(float(trade["realizedPL"]) / abs(pips), '.10f')), "ret": trade["realizedPL"], "ret_percent": str(format(return_percent, '.5f')), "ret_net": trade["realizedPL"], "side": side, "setups": "", "mistakes": "", "subs": [{"action": action, "spread": "SINGLE", "type": "FOREX", "date": trade["openTime"], "size": str(abs(float(trade["initialUnits"]))), "position": trade["initialUnits"], "price": trade["price"]}, {"action": action_2, "spread": "SINGLE", "type": "FOREX", "date": trade["closeTime"], "size": str(abs(float(trade["initialUnits"]))), "position": "0", "price": trade["averageClosePrice"]}]})
        return {'trades': return_value}
    except Exception as e:
        print(e)
        return {'errors': "Error Occured"}
