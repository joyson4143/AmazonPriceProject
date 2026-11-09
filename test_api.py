import requests

def get_exchange_rate():
    url = "https://api.frankfurter.dev/v2/rate/USD/INR"

    response = requests.get(url)
    data = response.json()

    return data["rate"]


usd_price = 239.99

rate = get_exchange_rate()

inr_price = usd_price * rate

print("USD Price: $", usd_price)
print("Exchange Rate:", rate)
print("Indian Price: ₹", round(inr_price, 2))