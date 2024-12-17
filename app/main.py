import pandas as pd
import os
import plotly.express as px


# define tickers and associated path to files
tickers_to_file_paths = {
    'AAPL': './data/AAPL_data.csv',
    'MSFT': './data/MSFT_data.csv',
    'GOOGL': './data/GOOGL_data.csv'
}

# init list of dataframes for each
df_list = []

# create dataframe for each file and load them into df_list
for ticker, file_path in tickers_to_file_paths.items():
    temp_df = pd.read_csv(file_path, skiprows=3, header=None)
    # define columns since we skipheaders with yfinance csv formatting
    temp_df.columns = ['Date', 'Adj Close',
                       'Close', 'High', 'Low', 'Open', 'Volume']
    # set date column to proper datetime format and add ticker column
    temp_df['Date'] = pd.to_datetime(temp_df['Date'])
    temp_df['Ticker'] = ticker
    # add temp df to df_list
    df_list.append(temp_df)


# combine all dataframes from list
df_combined = pd.concat(df_list, axis=0)
# index by date (shared index for each)
df_combined = df_combined.set_index('Date')


'''
Create Meta Data
'''
# daily returns
# groupby Ticker (same stock) on Close. percentage change to previous value
df_combined['Daily_Returns'] = df_combined.groupby('Ticker')[
    'Close'].pct_change()

# rolling averages
# groupyby Ticker on close, transform the data to a rolling average of 7 entries and get mean for each
# note first 6 or 29 will be Null since this calculates with x entries at a time, so backfill will give the first avg calculated with data
df_combined['7D MA'] = df_combined.groupby(
    'Ticker')['Close'].transform(lambda x: x.rolling(7).mean())
df_combined['30D MA'] = df_combined.groupby(
    'Ticker')['Close'].transform(lambda x: x.rolling(30).mean())

# rolling volatility over 30 days
df_combined['Volatility'] = df_combined.groupby(
    'Ticker')['Daily_Returns'].transform(lambda x: x.rolling(30).std())


'''
Analyze Data
'''
# average monthyl returns for
monthly_returns = df_combined.groupby(
    'Ticker')['Daily_Returns'].resample('ME').mean().unstack(level=0)
print("Monthly Returns:\n", monthly_returns)

# highest volatility dates, top 10 sort_by volatiltiy, descending
# TODO -> sortby and groupby at the same time.. soo highest volatility for apple, google, microfot seperately
high_volatility = df_combined.sort_values(
    by='Volatility', ascending=False).head(10)
print("High Volatility Periods:\n", high_volatility)
high_volatility_by_company = (df_combined
                              .groupby('Ticker')['Volatility']
                              .apply(lambda x: x.sort_values(ascending=False))
                              .head(3)
                              )
print("High Volatility By Company:\n", high_volatility_by_company)

# statistcal comparison of returns
print(df_combined.pivot(columns='Ticker', values='Daily_Returns').corr())

'''
CREATE PLOTLY VISUALIZATION
'''
figure = px.line(df_combined, x=df_combined.index, y='Close',
                 color='Ticker', title='Closing Prices Over Time')
figure.show()
