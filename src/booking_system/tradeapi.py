import enum
import queue

from flask import Blueprint, jsonify, Response, request
from flask.views import MethodView

import database

# Trade Queue For transferring the
TRADE_QUEUE = queue.Queue(maxsize=0)

# Blueprint to be provided to the Service as a REST Endpoint
api = Blueprint("tradeapi", __name__, url_prefix="/tradeapi")

# Database name could also be provided as a command line argument at start up
TRADE_DATABASE = "trades.db"


# Status codes Enum for future Enumerations to be added (such as in error cases)
class Code(enum.Enum):
    OK = 0
    NOOP = 1  # Request payload is No-op


# REST Endpoint Class
class TradeApi(MethodView):
    def get(self, trade_id):
        with database.TradeDB(TRADE_DATABASE) as db:
            data = db.select(trade_id=trade_id)
        return jsonify({"success": True, "get_response": data})

    def post(self):
        with database.TradeDB(TRADE_DATABASE) as db:
            req = request.json
            data = db.insert(
                req["sell_currency"],
                req["sell_amount"],
                req["buy_currency"],
                req["buy_amount"],
                req["rate"],
            )

            trade_data = db.select(trade_id=data)[0]

            # Marshal data to be passed to the SSE stream
            trade = {
                "trade_id": trade_data[0],
                "sell_currency": trade_data[1],
                "sell_amount": trade_data[2],
                "buy_currency": trade_data[3],
                "buy_amount": trade_data[4],
                "rate": trade_data[5],
            }
            # Put trade in SSE Stream
            TRADE_QUEUE.put(trade)

        return jsonify({"success": True, "post_response": {"id": data}})

    def put(self, trade_id):
        with database.TradeDB(TRADE_DATABASE) as db:
            req = request.json
            success = db.insert(
                trade_id,
                req.get("sell_currency"),
                req.get("sell_amount"),
                req.get("buy_currency"),
                req.get("buy_amount"),
                req.get("rate"),
            )

        return jsonify(
            {
                "success": success,
                "put_response": {"code": Code.OK if success is True else Code.NOOP},
            }
        )

    def delete(self, trade_id):
        with database.TradeDB(TRADE_DATABASE) as db:
            db.delete(trade_id)
        return jsonify({"success": True, "delete_response": ""})


tradeapi_view = TradeApi.as_view("tradeapi")
# Register POST endpoint as URL
api.add_url_rule("/trade", methods=["POST"], view_func=tradeapi_view)
# Register GET Endpoint as URL. Default allows for overlap with /trade/<trade_id>
api.add_url_rule(
    "/trade", methods=["GET"], defaults={"trade_id": None}, view_func=tradeapi_view
)
# Register Endpoint for working in specific trade
api.add_url_rule(
    "/trade/<trade_id>", methods=["GET", "PUT", "DELETE"], view_func=tradeapi_view
)
