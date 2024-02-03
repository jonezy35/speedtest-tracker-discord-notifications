import requests
import datetime
import os
from dateutil import parser, tz
os.system("")

# This is a python script that parses the JSON data from ghcr.io/alexjustesen/speedtest-tracker:latest and sends it to a discord webhook bot

#### VARIABLES ####
GITHUB_WEBHOOK_URL = 'YOURWEBHOOOKURL'
TARGET_TIMEZONE = 'EST' # Specify your timezone
THRESHOLD_DOWNLOAD = 0    # Set your download threshold in Mbps (0 to disable)
THRESHOLD_UPLOAD = 0      # Set your upload threshold in Mbps (0 to disable)
THRESHOLD_PING = 0        # Set your ping threshold in ms (0 to disable)


def fetch_speedtest_results():
    """Fetch the latest speed test results."""
    response = requests.get("http://localhost:8765/api/speedtest/latest") # Change this to match your setup. This should work for default setups
    response.raise_for_status()  # Raises stored HTTPError, if one occurred.
    return response.json()

def send_message_to_webhook(message):
    """Send a customized message to the GitHub webhook."""
    payload = {'content': message}
    response = requests.post(GITHUB_WEBHOOK_URL, json=payload)
    response.raise_for_status()

def main():
    data = fetch_speedtest_results()['data']
    ping = data['ping']
    upload = data['upload']
    download = data['download']
    created_at_utc = parser.parse(data['created_at'])

    # Check individual thresholds
    # if (THRESHOLD_DOWNLOAD > 0 and download < THRESHOLD_DOWNLOAD) or \
    #    (THRESHOLD_UPLOAD > 0 and upload < THRESHOLD_UPLOAD) or \
    #    (THRESHOLD_PING > 0 and ping > THRESHOLD_PING):
    #     return

    threshold_message = ""
    if THRESHOLD_DOWNLOAD > 0 and download < THRESHOLD_DOWNLOAD:
        threshold_message += f"**Download speed is below threshold ({THRESHOLD_DOWNLOAD} Mbps**).\n"
    if THRESHOLD_UPLOAD > 0 and upload < THRESHOLD_UPLOAD:
        threshold_message += f"**Upload speed is below threshold ({THRESHOLD_UPLOAD} Mbps**).\n"
    if THRESHOLD_PING > 0 and ping > THRESHOLD_PING:
        threshold_message += f"**Ping latency is above threshold ({THRESHOLD_PING} ms**).\n"

    # Convert UTC from speedtest-tracker to target timezone
    target_tz = tz.gettz(TARGET_TIMEZONE)
    converted_time = created_at_utc.astimezone(target_tz).strftime("%I:%M:%S %p %Z")

    # Get the current time in the specified timezone & convert it
    current_time = datetime.datetime.now(tz.gettz(TARGET_TIMEZONE))
    current_time_formatted = current_time.strftime("%I:%M:%S %p %Z")

    if threshold_message:
        message = f"{threshold_message}Current Time: {current_time_formatted}\nSpeed Test Results as of: {converted_time}\n- Download: {download}Mbps\n- Upload: {upload}Mbps\n- Ping: {ping}ms\n"
        send_message_to_webhook(message)
    elif THRESHOLD_DOWNLOAD == 0 and THRESHOLD_UPLOAD == 0 and THRESHOLD_PING == 0:
        message = f"There Are New Speedtest Results For Your Network\nCurrent Time: {current_time_formatted}\nSpeed Test Results as of: {converted_time}\n- Download: {download}Mbps\n- Upload: {upload}Mbps\n- Ping: {ping}ms\n"
        send_message_to_webhook(message)

if __name__ == '__main__':
    main()

