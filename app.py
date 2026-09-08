import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from Adyen.client import AdyenClient
from Adyen.services import AdyenCheckoutApi

# Load environment variables explicitly
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

API_KEY = os.environ.get("ADYEN_API_KEY")
MERCHANT_ACCOUNT = os.environ.get("ADYEN_MERCHANT_ACCOUNT")
CLIENT_KEY = os.environ.get("ADYEN_CLIENT_KEY")

app = Flask(__name__)

# Initialize Adyen client
adyen_client = AdyenClient()
adyen_client.xapikey = API_KEY
adyen_client.platform = "test"
checkout_service = AdyenCheckoutApi(client=adyen_client)

# In-memory database to track order states
orders_db = {}

@app.route('/')
def index():
    return render_template('index.html', client_key=CLIENT_KEY)

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/failed')
def failed():
    reason = request.args.get('reason', 'Transaction Declined')
    return render_template('failed.html', reason=reason)

@app.route('/api/admin/orders')
def get_orders():
    return jsonify(list(orders_db.values())[::-1])

@app.route('/api/sessions', methods=['POST'])
def sessions():
    data = request.get_json() or {}
    cart_total = data.get("amount", 1000)
    
    # Extract dynamic region data (default to Europe if missing)
    currency = data.get("currency", "EUR")
    country_code = data.get("countryCode", "NL")
    
    reference = f"order_{os.urandom(4).hex()}"

    # Save the specific currency to the admin database
    orders_db[reference] = {
        "reference": reference,
        "amount": f"{cart_total / 100:.2f}",
        "currency": currency,
        "status": "Pending Webhook ⏳",
        "psp_reference": "N/A"
    }

    payload = {
        "merchantAccount": MERCHANT_ACCOUNT,
        "amount": {"value": cart_total, "currency": currency},
        "returnUrl": "http://localhost:8080/handleRedirect",
        "reference": reference,
        "countryCode": country_code, # This tells Drop-in which local methods to show
        "blockedPaymentMethods": ["wechatpayMiniProgram", "wechatpaySDK","wechatpayQR"]
    }

    try:
        response = checkout_service.payments_api.sessions(payload)
        return jsonify(response.message)
    except Exception as e:
        print("Adyen API Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/handleRedirect', methods=['GET', 'POST'])
def handle_redirect():
    redirect_result = request.args.get('redirectResult')
    if redirect_result:
        try:
            details_payload = {"details": {"redirectResult": redirect_result}}
            response = checkout_service.payments_api.payments_details(details_payload)
            result_code = response.message.get("resultCode", "Error")
            if result_code in ["Authorised", "Received", "Pending"]:
                return render_template('success.html')
            return render_template('failed.html', reason=result_code)
        except Exception as e:
            return render_template('failed.html', reason="Validation Error")
    return render_template('failed.html', reason="No Redirect Result Received")

@app.route('/api/webhooks', methods=['POST'])
def webhooks():
    data = request.get_json() or {}
    for item in data.get("notificationItems", []):
        event = item.get("NotificationRequestItem", {})
        reference = event.get("merchantReference")
        event_code = event.get("eventCode")
        success = event.get("success") == "true"
        psp_ref = event.get("pspReference", "N/A")

        # Update order status in database when notification arrives
        if reference in orders_db:
            if event_code == "AUTHORISATION":
                orders_db[reference]["status"] = "Authorised ✅" if success else "Refused ❌"
                orders_db[reference]["psp_reference"] = psp_ref

        print(f"\n🔔 WEBHOOK | Order: {reference} | Status: {'Authorised' if success else 'Refused'} | PSP: {psp_ref}")

    return jsonify({"notificationResponse": "[accepted]"}), 200

if __name__ == '__main__':
    app.run(port=8080, debug=True)