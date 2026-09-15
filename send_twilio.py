import os

from twilio.rest import Client

# Your Account SID and Auth Token from console.twilio.com
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+2348168981743",
    from_="+15017250604",
    body="Hello from Eminence!")

print(message.sid)