"""Functions testing suite."""
import pandas as pd
import utils
from pandas.testing import assert_frame_equal


def test_get_api_data(mocker):
    mock_response = mocker.patch("utils.requests.get")
    mock_response.return_value.content = """{
        "Meta Data": {
            "1. Information": "Daily Prices (open, high, low, close) and Volumes",
            "2. Symbol": "goog",
            "3. Last Refreshed": "2021-10-27",
            "4. Output Size": "Compact",
            "5. Time Zone": "US/Eastern"
        },
        "Time Series (Daily)": {
            "2021-10-27": {
                "1. open": "2798.0500",
                "2. high": "2982.3600",
                "3. low": "2798.0500",
                "4. close": "2928.5500",
                "5. volume": "2583748"
            }
        }
    }"""

    expected_open, expected_high, expected_low, expected_close = (
        2798.05,
        2982.36,
        2798.05,
        2928.55,
    )
    actual_open, actual_high, actual_low, actual_close = utils.get_api_data(
        end_point="https://www.test-api.com/", date="2021-10-27"
    )

    assert expected_open == actual_open
    assert expected_high == actual_high
    assert expected_low == actual_low
    assert expected_close == actual_close


def test_get_plot_data(mocker):
    mock_response = mocker.patch("utils.SqLiteClient")
    mock_response().to_frame.return_value = pd.DataFrame(
        {
            "date": [
                "2021-10-01",
                "2021-10-04",
                "2021-10-05",
                "2021-10-06",
                "2021-10-07",
                "2021-10-08",
                "2021-10-11",
            ],
            "close": [
                3283.260000,
                3236.520000,
                3231.346667,
                3239.012500,
                3251.696000,
                3257.850000,
                3251.690000,
            ],
        }
    )

    expected_df = pd.DataFrame(
        {
            "close": [
                3283.260000,
                3236.520000,
                3231.346667,
                3239.012500,
                3251.696000,
                3257.850000,
                3251.690000,
            ]
        },
        index=[
            "2021-10-01",
            "2021-10-04",
            "2021-10-05",
            "2021-10-06",
            "2021-10-07",
            "2021-10-08",
            "2021-10-11",
        ],
    )
    expected_df.index.name = "date"
    actual_df = utils.get_plot_data(
        stock_symbol="amazn",
        date_to="2021-10-11",
    )
    assert_frame_equal(expected_df, actual_df)
