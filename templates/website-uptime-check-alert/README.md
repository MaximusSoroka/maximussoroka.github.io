# Website uptime check to alert

Local n8n workflow template. Import the JSON into your own n8n instance. It ships **inactive** (`active: false`) and contains **no real secrets** — only placeholder SMTP credentials and `https://example.com/`.

Every 5 minutes the workflow requests a URL. If the HTTP status is not 200, or no status is returned (timeout or network error), it **waits 60 seconds** and requests the URL again. An alert email is sent **only if the second check also fails**. A successful 200 on the first or the second check does not send mail.

## Files

- `workflow.json` — importable n8n workflow. No secrets. SMTP is a placeholder credential named `SMTP account (placeholder)`.

## Setup

1. In n8n: **… → Import from File** and choose `workflow.json`.
2. Open **Request website** and **Retry request website** and replace `https://example.com/` with the URL to check in both nodes. Also replace that URL in the subject and body of **Send down alert**.
3. Create an **SMTP** credential in n8n, attach it to **Send down alert** (remove the placeholder), and set From and To.
4. The default retry wait is **60 seconds**. To change it, open the **Wait 60 seconds** node and edit **Amount** and **Unit**.
5. Optionally change the interval in **Every 5 minutes**, the 10-second timeout, or the If conditions if you want to accept other 2xx codes.
6. Run a test against a URL you control (or temporarily point it at a path that returns 404) to see the wait and the alert, then point it at the real URL and **Activate**. Leave it inactive until the test works.

## Notes

- After the first failed check, the **Wait 60 seconds** node pauses for 60 seconds, then **Retry request website** runs. The alert is sent only if **Retry status is not 200** is also true.
- The HTTP nodes use “full response”, “never error”, and `onError: continueRegularOutput`, so a 4xx/5xx or a failed request can be evaluated instead of stopping the workflow.
- This is a simple local check, not a hosted monitoring service. It will not run while n8n is stopped, and it does not measure uptime percentages.
- Required n8n nodes are built-in: Schedule Trigger, HTTP Request, If, Wait, Send Email.
