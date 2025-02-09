import requests
from fastapi import FastAPI, HTTPException

ZAPIER_WEBHOOK_URL = "https://hooks.zapier.com/hooks/catch/21630305/2afz1n8/"

def send_email(to_email, subject, response):
    if not to_email or "@" not in to_email:
        raise HTTPException(status_code=400, detail="Invalid recipient email address")

    # Prepare the payload for Zapier
    payload = {
        "to_email": to_email,
        "subject": subject,
        "response": response
    }

    try:
        # Send the data to Zapier webhook
        response = requests.post(ZAPIER_WEBHOOK_URL, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors

        return {"status": "success", "detail": "Email sent successfully via Zapier"}
    except requests.exceptions.RequestException as e:
        # Handle any errors from the request
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")