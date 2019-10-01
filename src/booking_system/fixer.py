import requests

# Usually wouldn't be kept in the Repo but it's fine for demo
API_KEY = "63ede3ee0cd877e887d26eb8ec3664a2"
ENDPOINT_TEMPLATE = "http://data.fixer.io/api/{}?access_key=" + API_KEY


class Fixer(object):
    def __init__(self):
        self._symbols = None

    @staticmethod
    def _get_success_json(url):
        """
        Method to handle the response from Fixer
        """
        payload = requests.get(url)
        if not payload.status_code == 200:
            raise RuntimeError(
                "Server failed to return payload with status {}".format(
                    payload.status_code
                )
            )

        data = payload.json()
        if data["success"] is False:
            raise RuntimeError("Request failed: {}".format(data["error"]))

        return data

    @property
    def symbols(self):
        # Cache symbols
        if self._symbols is None:
            url = ENDPOINT_TEMPLATE.format("symbols")
            data = self._get_success_json(url)
            self._symbols = list(data["symbols"].keys())

        return self._symbols

    def get_current_rates(self, base, *symbols):
        url = ENDPOINT_TEMPLATE.format(
            "latest"
        ) + "&base={base}&symbols={symbols}".format(
            base=base, symbols=",".join(symbols)
        )
        data = self._get_success_json(url)

        return data["rates"]


if __name__ == "__main__":
    f = Fixer()
    print(f.symbols)
    print(f.get_current_rates("eur", "gbp"))
