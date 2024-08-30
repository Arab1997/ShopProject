import requests
import json

class GeneratePayLink:
    PAYME_URL = "https://checkout.paycom.uz/api"
    PAYME_KEY = "PS0hbhKTg4DRvTfWhDwKw?nknY6UQxeMkO7r"  # Replace with your actual Payme merchant key



    def __init__(self, order_id, amount):
        self.order_id = order_id
        self.amount = amount

    def generate_link(self):
        # Prepare the payload
        payload = {
            "method": "CreateTransaction",
            "params": {
                "account": {
                    "order_id": self.order_id
                },
                "amount": int(self.amount * 100),  # Convert to tiyin
                "description": "Order payment",
            }
        }

        headers = {
            "Content-Type": "application/json",
            "X-Auth": self.PAYME_KEY
        }

        # Send the request to Payme API
        response = requests.post(self.PAYME_URL, data=json.dumps(payload), headers=headers)

        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                return data["result"].get("pay_link", "")
            else:
                raise ValueError("Failed to generate payment link: " + data.get("error", {}).get("message", "Unknown error"))
        else:
            raise ValueError("Failed to connect to Payme API")