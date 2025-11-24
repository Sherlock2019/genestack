from slack_sdk.webhook import WebhookClient
import os, datetime

today = datetime.datetime.now().strftime("%Y-%m-%d")
hook = os.getenv("SLACK_WEBHOOK_URL")

if not hook:
    print("⚠️ No Slack webhook set. Skipping...")
    exit(0)

webhook = WebhookClient(hook)
webhook.send(text=f"Genestack Intelligence update for {today} is ready.")

print("✅ Slack notification sent.")
