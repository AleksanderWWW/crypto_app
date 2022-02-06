"""Utility functions for the application GUI"""


def transform_ticker(ticker: str) -> str:
    ticker_no_x = ticker.split(":")[1]
    curr = ticker_no_x[-3:]
    base = ticker_no_x[:-3]
    return base + "-" + curr
