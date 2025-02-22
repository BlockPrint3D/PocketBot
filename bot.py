import telebot
import time
import datetime
import numpy as np
import talib
from tvDatafeed import TvDatafeed, Interval

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# TradingView Data Configuration
tv = TvDatafeed()
SYMBOL = "EURUSD"  # Change to your desired currency pair
EXCHANGE = "FXCM"  # Example: FXCM for Forex
TIMEFRAME = Interval.in_5_minute  # Change to your preferred timeframe

# Technical Indicator Settings
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9

# Function to Get Market Data and Generate Signals
def get_signal():
    data = tv.get_hist(symbol=SYMBOL, exchange=EXCHANGE, interval=TIMEFRAME, n_bars=100)
    if data is None or data.empty:
        return None
    
    close_prices = np.array(data['close'], dtype=np.float64)
    
    # Calculate RSI and MACD
    rsi = talib.RSI(close_prices, RSI_PERIOD)[-1]
    macd, signal, _ = talib.MACD(close_prices, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    
    direction = None
    if rsi < 30 and macd[-1] > signal[-1]:
        direction = "BUY"
    elif rsi > 70 and macd[-1] < signal[-1]:
        direction = "SELL"
    
    if direction:
        return {
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "currency": SYMBOL,
            "signal": direction,
            "trade_timeframe": "5 minutes"
        }
    return None

# Function to Send Signal to Telegram
def send_signal(signal):
    message = f"\n📅 Time: {signal['time']}\n💰 Currency Pair: {signal['currency']}\n📈 Signal: {signal['signal']}\n⏳ Trade Duration: {signal['trade_timeframe']}"
    bot.send_message(CHAT_ID, message)

# Main Loop
while True:
    signal = get_signal()
    if signal:
        send_signal(signal)
    time.sleep(300)  # Check every 5 minutes
