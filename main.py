import httpx

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
            # Create a new registration to obtain an ID and token
            print("Generating temporary registration to validate license key...")
            reg_response = client.post("/reg")
            reg_data = reg_response.json()

            id = reg_data["id"]
            token = reg_data["token"]
            headers_post = {"Authorization": f"Bearer {token}"}

            # Attach the license key to the account
            license_update_payload = {"license": license_key}
            update_response = client.put(f"/reg/{id}/account", headers=headers_post, json=license_update_payload)

            if update_response.status_code != 200:
                print("Failed to update license key. Please ensure the key is valid.")
                return

            # Fetch account details
            account_response = client.get(f"/reg/{id}/account", headers=headers_post)
            if account_response.status_code == 200:
                account_data = account_response.json()
                print("\nLicense Details:")
                print(f"Account Type: {account_data['account_type']}")
                print(f"Data Allocated: {account_data['referral_count']} GB")
                print(f"License Key: {account_data['license']}")
            else:
                print("Failed to retrieve account details. Please try again.")

            # Clean up by deleting the temporary registration
            client.delete(f"/reg/{id}", headers=headers_post)
            print("Temporary registration deleted.")
    except httpx.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    print("\nWARP+ License Key Checker\n")
    license_key = input("Enter the license key to check: ").strip()
    if license_key:
        check_license_details(license_key)
    else:
        print("No license key entered. Exiting.")
