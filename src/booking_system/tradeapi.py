import enum
import queue

from flask import Blueprint, jsonify, Response, request
from flask.views import MethodView

import database

TRADE_QUEUE = queue.Queue(maxsize=0)

api = Blueprint("tradeapi", __name__, url_prefix="/tradeapi")

TRADE_DATABASE = "trades.db"


class Code(enum.Enum):
    OK = 0
    NOOP = 1  # Request payload is No-op


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
api.add_url_rule("/trade", methods=["POST"], view_func=tradeapi_view)
api.add_url_rule(
    "/trade", methods=["GET"], defaults={"trade_id": None}, view_func=tradeapi_view
)
api.add_url_rule(
    "/trade/<trade_id>", methods=["GET", "PUT", "DELETE"], view_func=tradeapi_view
)


@api.route("/trade_stream")
def trade_stream():
    def event_stream():
        while True:
            item = TRADE_QUEUE.get()
            yield "data: {}\n\n".format(jsonify(item))

        return Response(event_stream(), mimetype="text/event-stream")
