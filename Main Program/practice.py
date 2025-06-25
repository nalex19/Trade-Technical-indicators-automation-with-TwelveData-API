from twelvedata import TDClient

# Initialize client - apikey parameter is required
td = TDClient(apikey = '8c7af536f3834558b50750ff363aa578')

# Construct the necessary time series
ts = td.time_series(
    symbol="NVDA",
    interval="1min",
    outputsize=5
)

ema_test = ts.with_macd().with_ema(time_period=20).with_ema(time_period=1).as_csv()

# Returns pandas.DataFrame
df = ts.as_pandas()

#print(df)
print(ema_test)