from flask import Flask, render_template, request, jsonify
import yfinance as yf

app = Flask(__name__)

# 雷達掃描清單
WATCH_LIST = {
    "2330": "台積電",
    "2317": "鴻海",
    "2454": "聯發科",
    "2603": "長榮",
    "2615": "萬海"
}


def analyze_main_force(df):
    if len(df) < 20:
        return "資料不足"

    close = df["Close"]
    volume = df["Volume"]

    today_close = float(close.iloc[-1])
    yesterday_close = float(close.iloc[-2])

    today_volume = float(volume.iloc[-1])
    avg_volume_5 = float(volume.iloc[-6:-1].mean())

    ma5 = close.rolling(5).mean()
    ma20 = close.rolling(20).mean()

    score = 0
    reasons = []

    if today_volume >= avg_volume_5 * 2:
        score += 1
        reasons.append("爆量")

    if today_close > yesterday_close:
        score += 1
        reasons.append("價漲")

    if ma5.iloc[-1] > ma20.iloc[-1]:
        score += 1
        reasons.append("趨勢向上")

    if volume.iloc[-3] < volume.iloc[-2] < volume.iloc[-1]:
        score += 1
        reasons.append("量連增")

    if score >= 3:
        return f"🟢 主力進場（{score}/4：{'、'.join(reasons)}）"
    elif score == 2:
        return f"🟡 主力觀察（{score}/4）"
    else:
        return "⚪ 無主力"


@app.route("/", methods=["GET", "POST"])
def index():
    stock = None
    error = None

    if request.method == "POST":
        stock_id = request.form.get("stock_id")

        if stock_id:
            try:
                df = yf.Ticker(f"{stock_id}.TW").history(period="60d")

                if df.empty:
                    error = f"❌ 查不到股票代碼 {stock_id}"
                else:
                    today_vol = float(df["Volume"].iloc[-1])
                    avg_vol_5 = float(df["Volume"].iloc[-6:-1].mean())
                    volume_ratio = round(today_vol / avg_vol_5, 2) if avg_vol_5 > 0 else 0

                    stock = {
                        "code": stock_id,
                        "price": round(float(df["Close"].iloc[-1]), 2),
                        "status": analyze_main_force(df),
                        "volume_ratio": volume_ratio
                    }

            except Exception as e:
                error = f"錯誤：{e}"

    return render_template("index.html", stock=stock, error=error)


@app.route("/api/radar")
def radar():
    results = []

    for code, name in WATCH_LIST.items():
        try:
            df = yf.Ticker(f"{code}.TW").history(period="60d")
            if df.empty:
                continue

            today_vol = float(df["Volume"].iloc[-1])
            avg_vol_5 = float(df["Volume"].iloc[-6:-1].mean())
            volume_ratio = round(today_vol / avg_vol_5, 2) if avg_vol_5 > 0 else 0

            results.append({
                "code": code,
                "name": name,
                "price": round(float(df["Close"].iloc[-1]), 2),
                "status": analyze_main_force(df),
                "volume_ratio": volume_ratio
            })

        except:
            continue

    return jsonify(results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)