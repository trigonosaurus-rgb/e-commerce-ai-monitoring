import os
import httpx

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

async def send_slack_alert(message: str):
    """
    Sends an alert to Slack via Webhook.
    If SLACK_WEBHOOK_URL is not set, it falls back to console logging.
    """
    if not SLACK_WEBHOOK_URL:
        print(f"[SLACK ALERT MOCK]: {message}")
        return
    
    payload = {"text": message}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SLACK_WEBHOOK_URL, json=payload)
            response.raise_for_status()
            print("Successfully sent alert to Slack.")
    except Exception as e:
        print(f"Failed to send Slack alert: {e}")
