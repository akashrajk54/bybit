import requests

# Set the login URL
login_url = 'https://kite.zerodha.com/api/login'

# Set the user ID and password
user_id = 'YOUR_USER_ID_HERE'
password = 'YOUR_PASSWORD_HERE'

# Create the payload
payload = {
    'user_id': user_id,
    'password': password
}

# Make the login request
response = requests.post(login_url, json=payload)

# Print the response status code and text
print(response.status_code)
print(response.text)
