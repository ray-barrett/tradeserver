from flask import Flask, render_template

import booking_system.tradeapi as tradeapi
import booking_system.database as db
import booking_system.fixer as fixer
import booking_system.rateapi as rateapi

app = Flask(__name__)


@app.route("/")
def index():
    def trade_to_json(trade):
        return {
            "trade_id": trade[0],
            "sell_currency": trade[1],
            "sell_amount": trade[2],
            "buy_currency": trade[3],
            "buy_amount": trade[4],
            "rate": trade[5],
            "date_booked": trade[6],
        }

    with db.TradeDB(tradeapi.TRADE_DATABASE) as tradeDB:
        trades = tradeDB.select()
        table_items = [trade_to_json(t) for t in trades]

    return render_template("index.html", table_items=table_items)


@app.route("/trade")
def trade():
    combo_options = fixer.Fixer().symbols
    return render_template("trade.html", combo_options=combo_options)


app.register_blueprint(tradeapi.api)
app.register_blueprint(rateapi.api)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
