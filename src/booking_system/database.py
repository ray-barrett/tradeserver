import sqlite3
import random
import string

_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS trades (
    id TEXT PRIMARY KEY,
    sell_currency VARCHAR(3),
    sell_amount REAL,
    buy_currency VARCHAR(3),
    buy_amount REAL,
    rate REAL,
    booked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Booked_at is set by the DB
_INSERT_TRADE = """INSERT INTO
    trades (
        id, sell_currency, sell_amount, buy_currency, buy_amount, rate
    )
    VALUES (
        ?, ?, ?, ?, ?, ?
    );
"""

_SELECT_ALL = """SELECT
        id, sell_currency, sell_amount, buy_currency, buy_amount, rate, booked_at
    FROM trades
    ORDER BY booked_at ASC;
"""

_SELECT_ONE = """SELECT id, sell_currency, sell_amount, buy_currency, buy_amount, rate
    FROM trades
    WHERE id = ?;
"""

_UPDATE_TRADE = "UPDATE trades SET {} WHERE id = ? LIMIT 1"

_DELETE_TRADE = "DELETE FROM trades WHERE id = ? LIMIT 1"


class TradeDB(object):
    def __init__(self, database_url, init_db=False):
        self.database_url = database_url
        self.conn = None

        if init_db:
            c = self.cursor
            c.execute(_CREATE_TABLE)
            self.close()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    @staticmethod
    def _gen_trade_id():
        # Generate a 7 character string to use as part of the trade ID
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=7))

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.database_url)
            if self.conn is None:
                raise RuntimeError(
                    "Unable to connect to database '{}'".format(self.database_url)
                )
        return self.conn

    @property
    def cursor(self):
        self.conn = self.connect()
        return self.conn.cursor()

    def insert(self, s_curr, s_amnt, b_curr, b_amnt, rate):
        # Not guaranteed to prevent collisions but suits current purpose
        trade_id = "TR{}".format(self._gen_trade_id())

        # Pass the SQL and arguments such that the cursor will prevent injection attacks
        self.cursor.execute(
            _INSERT_TRADE, (trade_id, s_curr, s_amnt, b_curr, b_amnt, rate)
        )
        self.conn.commit()
        # Return the Trade ID so that it can be used if needed
        return trade_id

    def select(self, trade_id=None):
        if trade_id is None:
            items = self.cursor.execute(_SELECT_ALL)
        else:
            items = self.cursor.execute(_SELECT_ONE, (trade_id,))
        # The cursor returns a generator, we'll return it as a list
        return list(items)

    def update(
        self, trade_id, s_curr=None, s_amnt=None, b_curr=None, b_amnt=None, rate=None
    ):
        # If there is no information passed then we don't want to do anything
        if not any(s_curr, s_amnt, b_curr, b_amnt, rate):
            return False

        field_pairs = (
            ("sell_currency", s_curr),
            ("sell_amount", s_amnt),
            ("buy_currency", b_curr),
            ("buy_amount", b_amnt),
            ("rate", rate),
        )
        update_fields = []
        update_values = []
        update_field_template = "{} = ?"

        # Build the query with the fields that have a value provided to update
        for field, value in field_pairs:
            if value is not None:
                update_fields.append(update_field_template.format(field))
                update_values.append(value)

        # Add trade id to list to specify the item to be updated
        update_values.append(trade_id)

        sql = _UPDATE_TRADE.format(",".join(update_fields))
        self.cursor.execute(sql, update_values)
        self.conn.commit()
        return True

    def delete(self, trade_id):
        self.cursor.execute(_DELETE_TRADE, (trade_id,))
        self.conn.commit()


if __name__ == "__main__":
    with TradeDB("trades.db", init_db=True) as db:
        print(db.select())
        print(db.insert("Dollars", 12315.342312, "Euros", 14124, 3))
        print(db.select())
