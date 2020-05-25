from selenium import webdriver
import numpy as np
import pandas as pd
from datetime import datetime
import time
import itertools

CAMPING_BASE_WEB = "https://booking.euro-camping.com/search"
OPTIONS = "?checkin={DATE_IN}&checkout={DATE_OUT}&guestAges={AGES}&promotionCode=&categoryIds={TYPE}&lang=en"

type_options = {
    "Luxe": 3,
    "Confort": 2,
    "Standard": 1
}


def get_ages_str(n_persons: int):
    return ",".join([str(18) for i in range(n_persons)])


def get_price(browser, date_in, date_out, n_persons, type_pitch, base_url=CAMPING_BASE_WEB, options=OPTIONS):

    # Url to scrape
    full_url = base_url + options.format(
        DATE_IN=date_in,
        DATE_OUT=date_out,
        AGES=get_ages_str(n_persons),
        TYPE=type_options[type_pitch]
    )

    # Extract html content
    browser.get(full_url)
    print("sleeping...")
    time.sleep(5)

    # Find prices
    matching_elements = \
        browser.find_elements_by_xpath("//*[@class='price ng-binding' and contains(text(), '€')]")
    scraped_prices = [float(e.text[1:]) for e in matching_elements]
    print(scraped_prices)

    # Average and format output
    price_dict = {
        "persones": n_persons,
        "parcela": type_pitch,
        "dies": (datetime.strptime(date_out, "%Y-%m-%d") - datetime.strptime(date_in, "%Y-%m-%d")).days,
        "preu": np.mean(scraped_prices),
    }

    return price_dict


if __name__ == "__main__":
    params = [
        ["2020-08-22"],
        ["2020-08-23", "2020-08-30"],
        list(range(1, 7)),
        list(type_options.keys()),
    ]

    browser = webdriver.Chrome()

    prices_list = []
    for e in itertools.product(*params):
        prices_list.append(
            get_price(
                browser=browser,
                date_in=e[0],
                date_out=e[1],
                n_persons=e[2],
                type_pitch=e[3]
            )
        )

    browser.quit()

    prices_df = pd.DataFrame(prices_list)
    print(prices_df.to_csv("scraped_prices.csv", index=False))

