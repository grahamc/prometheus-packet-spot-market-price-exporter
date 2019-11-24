from prometheus_client.utils import INF
from prometheus_client import Counter, Histogram, Gauge, start_http_server
from pprint import pprint
import requests
import json
import sys
import time


FAILED_SPOT_QUERIES = Counter(
    "packet_spot_market_price_query_failures",
    "Total number of failures to fetch spot market prices",
)
SUCCESSFUL_SPOT_SCRAPES = Counter(
    "packet_spot_market_price_scrapes_total",
    "Total number of spot market price scrapes",
)
SPOT_REQUEST_TIME = Histogram(
    "packet_spot_market_price_query_duration",
    "Time spent requesting spot market prices",
    buckets=(
        0.5,
        0.75,
        1.0,
        2.5,
        5.0,
        7.5,
        10.0,
        12.5,
        15.0,
        17.5,
        20.0,
        25.0,
        30.0,
        45.0,
        60.0,
        90.0,
        120.0,
        INF,
    ),
)

PRICE = Gauge(
    "packet_spot_market_price",
    "The current price in dollars by plan and facility.",
    ["plan", "facility"],
)


def collect():
    try:
        for rec in spot_data():
            PRICE.labels(plan=rec["plan"], facility=rec["facility"]).set(rec["price"])
        SUCCESSFUL_SPOT_SCRAPES.inc()
    except Exception as e:
        pprint(e)
        FAILED_SPOT_QUERIES.inc()

def spot_data():
    with SPOT_REQUEST_TIME.time():
        data = requests.get(
            "https://api.packet.net/market/spot/prices?legacy=exclude",
            headers={"Accept": "application/json", "X-Auth-Token": api_token},
        ).json()
    for facility, facility_data in data["spot_market_prices"].items():
        for plan, price_data in facility_data.items():
            yield {"facility": facility, "plan": plan, "price": price_data["price"]}


if __name__ == "__main__":
    with open(sys.argv[1]) as config_file:
        config = json.load(config_file)
        api_token = config["api_token"]

    start_http_server(9400)
    while True:
        collect()
        time.sleep(60)
