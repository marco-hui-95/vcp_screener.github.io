#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# imports
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import date as dt
from pandas_datareader import data as pdr
import time
import finviz
from finviz.screener import Screener
from finvizfinance.quote import finvizfinance
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema


# In[ ]:


# determine whether MA200 is uptrend or not
def trend_value(nums:list):
    summed_nums = sum(nums)
    multiplied_data = 0
    summed_index = 0 
    squared_index = 0

    for index, num in enumerate(nums):
        index += 1
        multiplied_data += index * num
        summed_index += index
        squared_index += index**2

    numerator = (len(nums) * multiplied_data) - (summed_nums * summed_index)
    denominator = (len(nums) * squared_index) - summed_index**2
    if denominator != 0:
        return numerator/denominator
    else:
        return 0
    
# determine whether the ticker fulfills trend template
def trend_template(df):
    # calculate moving averages
    df['MA_50'] = round(df['Close'].rolling(window=50).mean(),2)
    df['MA_150'] = round(df['Close'].rolling(window=150).mean(),2)
    df['MA_200'] = round(df['Close'].rolling(window=200).mean(),2)
    
    if len(df.index) > 5*52:
        df['52_week_low'] = df['Low'].rolling(window = 5*52).min()
        df['52_week_high'] = df['High'].rolling(window = 5*52).max()
    else:
        df['52_week_low'] = df['Low'].rolling(window = len(df.index)).min()
        df['52_week_high'] = df['High'].rolling(window = len(df.index)).max()
    
    # condition 1&5: Price is above both 150MA and 200MA & above 50MA
    df['condition_1'] = (df['Close'] > df['MA_150']) & (df['Close'] > df['MA_200']) & (df['Close'] > df['MA_50'])
    
    # condition 2&4: 150MA is above 200MA & 50MA is above both
    df['condition_2'] = (df['MA_150'] > df['MA_200']) & (df['MA_50'] > df['MA_150'])
    
    # condition 3: 200MA is trending up for at least 1 month
    slope = df['MA_200'].rolling(window = 20).apply(trend_value)
    df['condition_3'] = slope > 0.0
    
    # condition 6: Price is at least 30% above 52 week low
    df['condition_6'] = df['Low'] > (df['52_week_low']*1.3)
    
    # condition 7: Price is at least 25% of 52 week high
    df['condition_7'] = df['High'] > (df['52_week_high']*0.75)
    
    # condition 9 (additional): The relative strength line, which compares a stock's price performance to that of the S&P 500.
    # An upward trending RS line tells you the stock is outperforming the general market.
    df['RS'] = df['Close']/df_spx['Close']
    slope_rs = df['RS'].rolling(window = 20).apply(trend_value)
    df['condition_8'] = slope > 0.0
    
    df['Pass'] = df[['condition_1','condition_2','condition_3','condition_6','condition_7','condition_8']].all(axis='columns')
    
    return df

# determine local maxima and minima
def local_high_low(df):
    local_high = argrelextrema(df['High'].to_numpy(),np.greater,order=10)[0]
    local_low = argrelextrema(df['Low'].to_numpy(),np.less,order=10)[0]
    
    # eliminate for consecutive highs or lows
    # create adjusted local highs and lows
    i = 0
    j = 0
    local_high_low = []
    adjusted_local_high = []
    adjusted_local_low = []
    
    while i < len(local_high) and j < len(local_low):
        if local_high[i] < local_low[j]:
            while i < len(local_high):
                if local_high[i] < local_low[j]:
                    i+=1
                else:
                    adjusted_local_high.append(local_high[i-1])
                    break
        elif local_high[i] > local_low[j]:
            while j < len(local_low):
                if local_high[i] > local_low[j]:
                    j+=1
                else:
                    adjusted_local_low.append(local_low[j-1])
                    break
        else:
            i+=1
            j+=1
    
    # add any remaining elements from local_high or local_low
    if i < len(local_high):
        adjusted_local_high.pop(-1)
        while i < len(local_high):
            if local_high[i] > local_low[j-1]:
                i+=1
            else:
                adjusted_local_high.append(local_high[i-1])
                break
        adjusted_local_high.append(local_high[-1])
        adjusted_local_low.append(local_low[j-1])
    
    if j < len(local_low):
        adjusted_local_low.pop(-1)
        while j < len(local_low):
            if local_high[i-1] > local_low[j]:
                j+=1
            else:
                adjusted_local_low.append(local_low[j-1])
                break
        adjusted_local_low.append(local_low[-1])
        adjusted_local_high.append(local_high[i-1])
    return adjusted_local_high, adjusted_local_low

# measure the depth of contractions
def contractions(df,local_high,local_low):
    local_high = local_high[::-1]
    local_low = local_low[::-1]
    
    i = 0
    j = 0
    contraction = []
    
    while i < len(local_low) and j < len(local_high):
        if local_low[i] > local_high[j]:
            contraction.append(round((df['High'][local_high][j] - df['Low'][local_low][i]) / df['High'][local_high][j] * 100,2))
            i+=1
            j+=1
        else:
            j+=1
    return contraction

# measure number of contractions
def num_of_contractions(contraction):
    new_c = 0
    num_of_contraction = 0
    for c in contraction:
        if c > new_c:
            num_of_contraction+=1
            new_c = c
        else:
            break
    return num_of_contraction

# measure depth of maximum and minimum contraction
def max_min_contraction(contraction,num_of_contractions):
    max_contraction = contraction[num_of_contractions-1]
    min_contraction = contraction[0]
    return max_contraction, min_contraction

# measure days of contraction
def weeks_of_contraction(df,local_high,num_of_contractions):
    week_of_contraction = (len(df.index) - local_high[::-1][num_of_contractions-1]) / 5
    return week_of_contraction

# determine whether the ticker has VCP
def vcp(df):
    # prepare data for contractions measurement
    [local_high, local_low] = local_high_low(df)

    contraction = contractions(df,local_high,local_low)
    
    # calculate no. of contractions
    num_of_contraction = num_of_contractions(contraction)
    if 2 <= num_of_contraction <= 4:
        flag_num = 1
    else:
        flag_num = 0
    
    # calculate depth of contractions
    [max_c, min_c] = max_min_contraction(contraction,num_of_contraction)
    if max_c > 50:
        flag_max = 0
    else:
        flag_max = 1
    if min_c <= 15:
        flag_min = 1
    else:
        flag_min = 0
    
    # calculate weeks of contractions
    week_of_contraction = weeks_of_contraction(df,local_high,num_of_contraction)
    if week_of_contraction >= 2:
        flag_week = 1
    else:
        flag_week = 0
    
    df['30_day_avg_volume'] = round(df['Volume'].rolling(window = 30).mean(),2)
    df['5_day_avg_volume'] = round(df['Volume'].rolling(window = 5).mean(),2)
    # criteria_2: Volume contraction
    df['vol_contraction'] = df['5_day_avg_volume'] < df['30_day_avg_volume']
    if df['vol_contraction'][-1] == 1:
        flag_vol = 1
    else:
        flag_vol = 0
        
    # criteria 3: Not break out yet
    if df['High'][-1] < df['High'][local_high][-1]:
        flag_consolidation = 1
    else:
        flag_consolidation = 0
    
    if flag_num == 1 & flag_max == 1 & flag_min == 1 & flag_week == 1 & flag_vol == 1 & flag_consolidation == 1:
        flag_final = 1
    else:
        flag_final = 0
    
    return num_of_contraction,max_c,min_c,week_of_contraction,flag_final

# calculate RS rating
def rs_rating(ticker,rs_list):
    ticker_index = rs_list.index(ticker)
    rs = round(ticker_index / len(rs_list) * 100,0)
    return rs


# In[ ]:


# Screen stocks from Finviz.com with filters
filters = ['cap_smallover','sh_avgvol_o100','sh_price_o2','ta_sma200_sb50','ta_sma50_pa']
stock_list = Screener(filters = filters, table = 'Performance' , order = 'asc')
ticker_table = pd.DataFrame(stock_list.data)
ticker_list = ticker_table['Ticker'].to_list()
# print(ticker_list)


# In[ ]:


# for condition_8, RS rating should be greater than 70
# The RS Rating tracks a stock's share price performance over the last 52 weeks, 
# and then compares the result to that of all other stocks.
performance_table = Screener(table='Performance', order='perf52w')
rs_table = pd.DataFrame(performance_table.data)
rs_list = rs_table['Ticker'].to_list()

# for condition_9 of trend_template_screener, it has to compare with S&P500 index
df_spx = yf.download(tickers = '^GSPC', period = '2y')


# In[ ]:


# ticker.info is not used because processing time is too long

yf.pdr_override()

# Create a dataframe to store results later
radar = pd.DataFrame({
    'Ticker': [],
    'Num_of_contraction': [],
    'Max_contraction': [],
    'Min_contraction': [],
    'Weeks_of_contraction': [],
    'RS_rating': []
})

fail = 0

for ticker_string in ticker_list:
    try:
        ticker_history = pdr.get_data_yahoo(tickers = ticker_string, period = '2y') # Get the data of stocks
        trend_template_screener = trend_template(ticker_history) # Determine whether the stocks is in Stage 2
        if trend_template_screener['Pass'][-1] == 1:
            print(f'{ticker_string} is in Stage 2')  
            vcp_screener = list(vcp(ticker_history)) # Determine whether the stocks is in Stage 2
            rs = rs_rating(ticker_string,rs_list) # Calculate RS rating
            if (vcp_screener[-1] == 1) & (rs >= 70):
                vcp_screener.insert(0,ticker_string)
                vcp_screener.insert(-1,rs)
                radar.loc[len(radar)] = vcp_screener[0:6] # Store the results to the dataframe
                print(f'{ticker_string} has a VCP')
            else:
                print(f'{ticker_string} does not have a VCP')
        else:
            print(f'{ticker_string} is not in Stage 2')
    except:
        fail+=1
        
print('Finished!!!')
print(f'{fail} stocks fail to analyze')


# In[ ]:


print(f'{len(radar)} stocks pass')
# print(radar)


# In[ ]:


for ticker in radar['Ticker']:
    ticker_history = pdr.get_data_yahoo(tickers = ticker, period = '2y')
    [local_high, local_low] = local_high_low(ticker_history)
    contraction = contractions(ticker_history,local_high,local_low)
    num_of_contraction = num_of_contractions(contraction)
    local_high = local_high[::-1][0:num_of_contraction]
    local_low = local_low[::-1][0:num_of_contraction]
    
    plt.plot(range(len(ticker_history.index)),ticker_history['Close'])
    plt.plot(local_high,ticker_history['High'][local_high],'o')
    plt.plot(local_low,ticker_history['Low'][local_low],'x')
    
    plt.title(ticker)
    plt.xlabel('Days')
    plt.ylabel('Close Price')
    plt.show()


# In[ ]:


# Define the filename for your Excel file
filename = 'C:/Users/marco/Desktop/Trade Resources/Watchlist/vcp_screener.xlsx'

# Get today's date
today = dt.today().strftime("%Y_%m_%d")

# Try to read in the existing file (if it exists)
try:
    database = pd.read_excel(filename, sheet_name=None)
except FileNotFoundError:
    database = {}

# Add today's data to the existing data (if any)
database[today] = radar

# Write the updated data to the Excel file
with pd.ExcelWriter(filename) as writer:
    for sheet_name, df in database.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

