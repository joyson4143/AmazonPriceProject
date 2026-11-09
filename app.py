from flask import Flask, request, jsonify
from dotenv import load_dotenv
from channel3_sdk import Channel3
import requests
import os

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("CHANNEL3_API_KEY")
client = Channel3(api_key=API_KEY) if API_KEY else None


@app.route("/")
def home():
    return "Amazon Product Price Finder API is Running!"


@app.route("/search")
def search():

    product = request.args.get("name", "").strip()

    if not product:
        return jsonify({"error": "Product name required"}), 400

    if not client:
        return jsonify({"error": "API Key missing"}), 500

    try:
        response = client.products.search(
            query=product,
            limit=10
        )

        products = []

        exchange_response = requests.get(
            "https://open.er-api.com/v6/latest/USD",
            timeout=10
        )

        exchange_data = exchange_response.json()

        if exchange_data.get("result") != "success":
            return jsonify({"error": "Exchange rate unavailable"}), 502

        rate = exchange_data["rates"]["INR"]

        for item in response.items:

            product_data = item.model_dump(mode="json")

            offers = product_data.get("offers", [])

            for offer in offers:
                price_info = offer.get("price", {})
                usd_price = price_info.get("price")
                currency = price_info.get("currency")

                if usd_price is not None and currency == "USD":
                    price_info["inr_price"] = round(usd_price * rate, 2)
                    price_info["inr_currency"] = "INR"

            products.append(product_data)

        return jsonify({
            "product_name": product,
            "exchange_rate": rate,
            "currency": "INR",
            "total_results": len(products),
            "products": products
        })

    except Exception as e:
        print("API Error:", e)

        return jsonify({
            "error": "Product search failed"
        }), 502


if __name__ == "__main__":
    app.run(debug=True, port=5000)