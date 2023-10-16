import requests
from datetime import datetime
import smtplib
from dotenv import load_dotenv
import os
import time

load_dotenv(override=True)

EMAIL = os.environ.get("SENDER")
PWD = os.environ.get("PWD")


# From https://www.latlong.net/
MY_LAT = 6.320439
MY_LONG = -75.567467


# Your position is within +5 or -5 degrees of the ISS position
def is_iss_close() -> bool:
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])
    if abs(iss_latitude - MY_LAT) <= 5 and abs(iss_longitude - MY_LONG) <= 5:
        return True
    return False


def is_night():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }

    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    time_now = datetime.now().hour

    if time_now >= sunset or time_now <= sunrise:
        return True
    return False


def send_email():
    if is_iss_close() and is_night():
        with smtplib.SMTP("smtp.gmail.com") as conn:
            conn.starttls()
            conn.login(user=EMAIL, password=PWD)
            conn.sendmail(
                from_addr=EMAIL,
                to_addrs=EMAIL,
                msg="Subject:Look up! ISS is close\n Look up, pal."
            )


if __name__ == '__main__':
    while True:
        send_email()
        time.sleep(60)
