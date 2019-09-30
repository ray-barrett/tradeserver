import enum
import queue

from flask import Blueprint, jsonify, request
from flask.views import MethodView

import fixer

TRADE_QUEUE = queue.Queue(maxsize=0)

api = Blueprint("rateapi", __name__, url_prefix="/rateapi")


class Code(enum.Enum):
    OK = 0
    NOOP = 1  # Request payload is No-op


class RateApi(MethodView):
    def get(self):
        fxr = fixer.Fixer()
        base = request.args.get("base")
        symbol = request.args.get("symbol")

        data = fxr.get_current_rates(base, symbol)

        return jsonify({"success": True, "get_response": data})


rateapi_view = RateApi.as_view("rateapi")
api.add_url_rule("/rate", methods=["GET"], view_func=rateapi_view)
