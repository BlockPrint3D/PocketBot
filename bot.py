import websocket
import json
import numpy as np
import talib
import time
import random
import datetime
import telebot

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"  # Replace with your chat ID or use bot.get_updates()

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Pocket Option WebSocket URL
POCKET_OPTION_WS_URL = "wss://ws.pocketoption.com"

# Trading Parameters
STOP_LOSS = 50  # Define stop loss amount
BALANCE_PERCENTAGE = 2  # 2% of balance per trade
MARTINGALE_MULTIPLIER = 2
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
TRADE_COOLDOWN = 5
MAX_CONSECUTIVE_LOSSES = 3
TRADING_HOURS = (9, 17)  # Trading between 9 AM and 5 PM

# Initialize Variables
trade_history = []
current_balance = 1000  # Placeholder balance
consecutive_losses = 0

def send_signal(currency, direction, time_frame):
    message = f"\u23F0 זמן: {datetime.datetime.now().strftime('%H:%M:%S')}\n\uD83D\uDCB1 מטבע: {currency}\n📈 עולה / 📉 יורד: {direction}\n⏳ מתי להיכנס: עכשיו\n🕒 תחום זמן: {time_frame} דקות"
    bot.send_message(CHAT_ID, message)

def on_message(ws, message):
    global consecutive_losses
    
    data = json.loads(message)
    price = data.get("price", None)
    currency = data.get("currency", "Unknown")
    
    if not price:
        return
    
    trade_history.append(price)
    if len(trade_history) > 100:
        trade_history.pop(0)
    
    prices = np.array(trade_history, dtype=np.float64)
    rsi = talib.RSI(prices, RSI_PERIOD)[-1]
    macd, signal, _ = talib.MACD(prices, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    
    current_hour = datetime.datetime.now().hour
    if current_hour < TRADING_HOURS[0] or current_hour > TRADING_HOURS[1]:
        return
    
    if consecutive_losses >= MAX_CONSECUTIVE_LOSSES:
        return
    
    if rsi < 30 and macd[-1] > signal[-1]:
        send_signal(currency, "📈 עולה", "5")
    elif rsi > 70 and macd[-1] < signal[-1]:
        send_signal(currency, "📉 יורד", "5")
    
    time.sleep(TRADE_COOLDOWN)

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws):
    print("Connected to Pocket Option")
    ws.send(json.dumps({"action": "subscribe", "channel": "price"}))

ws = websocket.WebSocketApp(
    POCKET_OPTION_WS_URL,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)
ws.on_open = on_open
ws.run_forever()
