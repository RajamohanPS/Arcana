from django.shortcuts import render
from django.http import JsonResponse
import yfinance as yf
import json
import pandas as pd
from .portfolio_analytics import *
# Create your views here.

def index(request):
    return render(request, "main2.html")



def get_fundamentals(request, symbol):
    info = yf.Ticker(symbol).get_info()
    return JsonResponse(info)


def portfolio_analyzer(request):
    if request.method == "POST":
        funds = float(request.POST.get('funds'))
        return_value = float(request.POST.get('return'))
        tickers = request.POST.getlist('tickers[]')

        df = Portfol_data('2017-01-01','2023-01-01',tickers)

        # df = cleaning(df)
        
        try:
            hrp = portfol_weights_Hrp(df, funds)
           
        except Exception as e:
            hrp = dict({'status':'failure', 'error':str(e)})
        
        try:
            ideal = ideal_pf(df, funds)
           
        except Exception as e:
            ideal = dict({'status':'failure', 'error':str(e)})

        try:
            min_vol = min_vol_new(df, funds)
        except Exception as e:
            min_vol = dict({'status':'failure', 'error':str(e)})

        try:
            eff_funds = efficient_return(df, funds, return_value/100)
            print(eff_funds)
        except Exception as e:
            eff_funds = dict({'status':'failure', 'error':str(e)})
        
        print(hrp)
        print(ideal)
        print(min_vol)
        
        # new_hrp = dict({
        #     'weights':dict(hrp['weights']),
        #     'qty':str(hrp['qty']),
        # })
        # print(new_hrp)

        # body_unicode = request.POST['data']
        # body = json.loads(body_unicode)
        # # content = body['content']
        # print(body)
    return JsonResponse({'hrp':hrp,'ideal':ideal,'min_vol':min_vol,'eff':eff_funds})