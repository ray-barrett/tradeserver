from flask import Flask, Response, jsonify, render_template

import booking_system.database as db
import booking_system.fixer as fixer
import booking_system.rateapi as rateapi
import booking_system.tradeapi as tradeapi
import booking_system.database as database

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

    # Load the page with initial trade data to be further supplemented with SSE
    # Stream.
    with db.TradeDB(tradeapi.TRADE_DATABASE) as tradeDB:
        trades = tradeDB.select()
        # Convert the trades to JSON
        table_items = [trade_to_json(t) for t in trades]

    return render_template("index.html", table_items=table_items)


@app.route("/trade")
def trade():
    # Gather the symbols to have them present as part of page load
    combo_options = fixer.Fixer().symbols
    return render_template("trade.html", combo_options=combo_options)


@app.route("/trade_stream")
def trade_stream():
    # SSE Stream: This should allow for the Trades table to be updated
    # automatically in the user's view
    def event_stream():
        with app.app_context():
            while True:
                item = tradeapi.TRADE_QUEUE.get()
                print(item)
                yield "data: {}\n\n".format(jsonify(item))

    return Response(event_stream(), mimetype="text/event-stream")


app.register_blueprint(tradeapi.api)
app.register_blueprint(rateapi.api)

if __name__ == "__main__":
    # Ensure the Trade Database is initialised
    database.TradeDB(tradeapi.TRADE_DATABASE, init_db=True)
    app.run(debug=True, threaded=True)
