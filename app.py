from flask import Flask, render_template, request, jsonify
import httpx

app = Flask(__name__)

def check_license_details(license_key):
    headers = {
        "CF-Client-Version": "a-6.11-2223",
        "Host": "api.cloudflareclient.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.12.1",
    }

    try:
        with httpx.Client(base_url="https://api.cloudflareclient.com/v0a2223", headers=headers, timeout=30.0) as client:
            # Create a temporary registration
            reg_response = client.post("/reg")
            reg_data = reg_response.json()

            id = reg_data["id"]
            token = reg_data["token"]
            headers_post = {"Authorization": f"Bearer {token}"}

            # Attach the license key to the account
            license_update_payload = {"license": license_key}
            update_response = client.put(f"/reg/{id}/account", headers=headers_post, json=license_update_payload)

            if update_response.status_code != 200:
                return {"error": "Invalid or unauthorized license key."}

            # Fetch account details
            account_response = client.get(f"/reg/{id}/account", headers=headers_post)
            if account_response.status_code == 200:
                account_data = account_response.json()
                # Clean up temporary registration
                client.delete(f"/reg/{id}", headers=headers_post)

                return {
                    "account_type": account_data["account_type"],
                    "referral_count": account_data["referral_count"],
                    "license": account_data["license"],
                }
            else:
                return {"error": "Failed to retrieve account details."}
    except Exception as e:
        return {"error": str(e)}

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        license_key = request.form.get("license_key")
        if license_key:
            details = check_license_details(license_key)
            return render_template("index.html", details=details)
    return render_template("index.html", details=None)

if __name__ == "__main__":
    app.run(debug=True)
