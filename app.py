print("🔥 VERSION 2026-01-13 VOLUME-PRICE")

from flask import Flask, render_template, request, jsonify
import yfinance as yf

def get_stock_data(stock_id):
    symbol = f"{stock_id}.TW"
    data = yf.download(symbol, period="5d", interval="1d")

    if data.empty:
        return None

    close_today = float(data["Close"].iloc[-1])
    close_yesterday = float(data["Close"].iloc[-2])

    volume_today = int(data["Volume"].iloc[-1])
    volume_yesterday = int(data["Volume"].iloc[-2])

    volume_change_pct = round(
        (volume_today - volume_yesterday) / volume_yesterday * 100, 2
    )

    # 量價判斷（簡單但很實用）
    if close_today > close_yesterday and volume_today > volume_yesterday:
        power = "📈 價漲量增（偏多）"
    elif close_today < close_yesterday and volume_today > volume_yesterday:
        power = "⚠️ 價跌量增（偏空）"
    else:
        power = "➡️ 量價無明顯方向"

    return {
        "code": stock_id,
        "price": close_today,
        "volume_today": volume_today,
        "volume_yesterday": volume_yesterday,
        "volume_change_pct": volume_change_pct,
        "power": power,
    }
