import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

import yfinance as yf
import cvxpy

from pypfopt import expected_returns
from pypfopt import HRPOpt

from pypfopt import EfficientFrontier
from pypfopt import risk_models


def Portfol_data(sd,ed,stock_symbol_list):
    d=yf.download(stock_symbol_list,sd,ed)['Adj Close']
    return d

def cleaning(d):
    nrows=d.shape[0]
    ncols=d.shape[1]
    d.dropna(axis=1,thresh=0.95*nrows,inplace=True)
    d.dropna(axis=0,how='any',inplace=True)
    return d

# Hierarchical Risk Parity

def portfol_weights_Hrp(d,funds):
    
    dicti = {'weights':None, 'qty':None}
    
    returns = expected_returns.returns_from_prices(d)
    hrp = HRPOpt(returns)
    hrp.optimize()
    hrp_weights = hrp.clean_weights()
    # print('hrp_obj',hrp_weights)
    
    dicti['weights']=dict(hrp.clean_weights())
    
    dicti['perf']=hrp.portfolio_performance(verbose=True)
    
    funds=str(funds)
    funds=float(funds)
    stock_symbol_list=list(d.columns)
    
    dicti['qty']=purchasing(d,hrp_weights,funds,stock_symbol_list)
    dicti['status'] = 'success'
    
    return dicti
    
#max Sharpe
    
def ideal_pf(df,funds):
    
    dicti = {'weights':None,'qty':None}
    
    mu = expected_returns.mean_historical_return(df)
    s = risk_models.sample_cov(df)
    
    s=risk_models.fix_nonpositive_semidefinite(s, fix_method='spectral')
    
    ef=EfficientFrontier(mu,s,solver='ECOS')
    
    max_sharpe_r_weights = ef.max_sharpe()
    sharpe_cleaned_weights= ef.clean_weights() 
    
    # print('max_sharpe_obj',sharpe_cleaned_weights)
    
    dicti["weights"]=dict(sharpe_cleaned_weights)
    dicti['perf']=ef.portfolio_performance(verbose=True)
    
    funds=str(funds)
    funds=float(funds)
    stock_symbol_list=list(df.columns)
    
    dicti['qty']=purchasing(df,sharpe_cleaned_weights,funds,stock_symbol_list)
    dicti['status'] = 'success'
    
    return dicti
    
# Min Volatility


def min_vol_new(df,funds):
    
    dicti = {'weights':None,'qty':None}
   
    mu = expected_returns.mean_historical_return(df)
    s = risk_models.sample_cov(df)
    
    s=risk_models.fix_nonpositive_semidefinite(s, fix_method='spectral')
    
    ef=EfficientFrontier(mu,s,solver='ECOS')
    
    min_vol_wts = ef.min_volatility()
    
    # print('min_vola_wts',min_vol_wts)
    
    dicti["weights"]=dict(min_vol_wts)
    dicti['perf']=ef.portfolio_performance(verbose=True)
    
    funds=str(funds)
    funds=float(funds)
    stock_symbol_list=list(df.columns)
    
    dicti['qty']=purchasing(df,min_vol_wts,funds,stock_symbol_list)
    dicti['status'] = 'success'
    
    return dicti


#Min vol for a given expected return 

def efficient_return(df, funds, rate):
    
    dicti = {'weights':None,'qty':None}
    
    mu = expected_returns.mean_historical_return(df)
    s = risk_models.sample_cov(df)
    
    s=risk_models.fix_nonpositive_semidefinite(s, fix_method='spectral')
    
    ef=EfficientFrontier(mu,s,solver='ECOS')
    
    # print("What is your Expcted Return ? ( in % )")
    er=str(rate)
    er=float(er)
    
    eff_return = ef.efficient_return(er)
     
    # print('eff_return_wts',eff_return)
    
    dicti["weights"]=dict(eff_return)
    dicti['perf']=ef.portfolio_performance(verbose=True)
    
    funds=str(funds)
    funds=float(funds)
    stock_symbol_list=list(df.columns)
    
    dicti['qty']=purchasing(df,eff_return,funds,stock_symbol_list)
    dicti['status'] = 'success'
    return dicti
    
    
    
def purchasing(d,wts,funds,stock_symbol_list):
    
    df_currentprice=pd.DataFrame(columns=["previousClose","weights",'Max_Buy',"Deviations"])
    
    original_funds=funds
    
    for x in stock_symbol_list:
        
        z=yf.Ticker(x).info['previousClose']

        df_currentprice.loc[str(x)] = [z,
                                       wts[str(x)],
                                       (wts[str(x)]*original_funds)//z,
                                       wts[str(x)]-(z/original_funds)]
        
        funds-=z*(wts[str(x)]*original_funds//z)
                                       
    
    df_currentprice.sort_values(by=["Deviations"],ascending=False,axis=0,inplace=True)
    
    while funds>min(df_currentprice["previousClose"]):
    
        
        for items in df_currentprice.index:
            
            if funds>0:
                
                if df_currentprice["previousClose"][items]<funds:
                    
                    no_of_buys=funds//df_currentprice["previousClose"][items]
                    
                    funds-=df_currentprice["previousClose"][items]*no_of_buys
                    
                    df_currentprice["Max_Buy"][items]+=no_of_buys
                
    return (df_currentprice['Max_Buy'].to_dict())
                