import time
import pandas as pd
import schedule                           
from twelvedata import TDClient           # pip install twelvedata[pandas]
from requests.exceptions import RequestException
from notificationEmail import EmailSender
from display import *

# ─── USER SETTINGS ──────────────────────────────────────────────────────────────
SYMBOL     = "NVDA"
INTERVAL   = "30min"    # any valid TD interval: 1min, 5min, 15min, 1h
FAST_EMA   = 10
SLOW_EMA   = 50
POLL_EVERY = 400        # minutes between API hits; will check the last 20 minutes of bars
# ────────────────────────────────────────────────────────────────────────────────

API_KEY = '8c7af536f3834558b50750ff363aa578'
td = TDClient(apikey=API_KEY)


def latest_bars(rows: int = 300) -> pd.DataFrame:
    """
    Download the most recent <rows> bars in UTC and return a UTC-indexed DataFrame.
    """
    ts = td.time_series(
        symbol=SYMBOL,
        interval=INTERVAL,
        outputsize=rows,
        timezone="UTC" 
    )
    df = ts.as_pandas()                   
    df.index = pd.to_datetime(df.index, utc=True)  # parse as UTC directly
    df = df.astype(float).sort_index()             # ascending chronological
    return df

def check_cross() -> None:
    """
    Fetch recent bars (UTC), compute EMAs, then look for any crossovers
    that occurred in the last POLL_EVERY minutes (based on the last bar time in UTC).
    If none, print a “no crosses” message. Network errors are caught and reported. thanks gpt
    """
    try:
        # Fetch enough bars so EMAs are accurate (5× the larger span)
        df = latest_bars(max(FAST_EMA, SLOW_EMA) * 5)
    except RequestException as e:
        # If the HTTP request fails, report in local U.K. time
        now_london = pd.Timestamp.now(tz="Europe/London")
        now_str    = now_london.strftime("%Y-%m-%d %H:%M %Z")
        print(f"⚠️  Failed to fetch data (@ {now_str}): {e}")
        return
    
    close     = df["close"]
    ema_fast  = close.ewm(span=FAST_EMA).mean()
    ema_slow  = close.ewm(span=SLOW_EMA).mean()

    # Boolean series marking where a cross occurred on each bar
    crossed_up   = (ema_fast.shift(1) < ema_slow.shift(1)) & (ema_fast > ema_slow)
    crossed_down = (ema_fast.shift(1) > ema_slow.shift(1)) & (ema_fast < ema_slow)

    last_bar_utc = df.index[-1]                                   # e.g. 2025-06-03 14:19:00+00:00
    cutoff_utc   = last_bar_utc - pd.Timedelta(minutes=POLL_EVERY) # e.g. 14:19 – 20 min = 13:59 UTC

    # Filter for crosses that happened at or after cutoff_utc, thanks chatgpt
    recent_up   = crossed_up[cutoff_utc:]
    recent_down = crossed_down[cutoff_utc:]

    if recent_up.any() or recent_down.any():
        # For each cross, convert its UTC index to Europe/London for printing
        for ts_utc in recent_up[recent_up].index:
            ts_london = ts_utc.tz_convert("Europe/London")
            time_str  = ts_london.strftime("%Y-%m-%d %H:%M %Z")
            message_Bullish = [f"🔔 {SYMBOL} **bullish** EMA{FAST_EMA}/{SLOW_EMA} crossover @ {time_str}"]
            print(message_Bullish)
            EmailSender('noelalex449@gmail.com').send_gmail('noelalex449@gmai.com',f'Bullish: {SYMBOL}, Interval: {INTERVAL}', message_Bullish)

        for ts_utc in recent_down[recent_down].index:
            ts_london = ts_utc.tz_convert("Europe/London")
            time_str  = ts_london.strftime("%Y-%m-%d %H:%M %Z")
            message_Bearish = print(f"🔔 {SYMBOL} **bearish** EMA{FAST_EMA}/{SLOW_EMA} crossover @ {time_str}")
            print(message_Bearish)
            #EmailSender('noelalex449@gmail.com').send_gmail('noelalex449@gmai.com',f'Bearish: {SYMBOL}, Interval: {INTERVAL}', message_Bearish)
            # Dont really care about bearish right now ibr



    else: # No crosses in that time area thing
        last_london = last_bar_utc.tz_convert("Europe/London")
        now_str     = last_london.strftime("%Y-%m-%d %H:%M %Z")
        print(f"No crosses in the last {POLL_EVERY} minutes (as of {now_str})")

    print('-'*50)

if __name__ == "__main__":
    check_cross()     # Run once at startup so you get immediate feedback

    # Schedule the check every POLL_EVERY minutes
    schedule.every(POLL_EVERY).minutes.do(check_cross)

    while True:
        schedule.run_pending()
        time.sleep(1)


