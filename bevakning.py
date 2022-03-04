#!/usr/bin/env python3
"""Bevakning av sista minuten-tider hos Folktandvården."""

import re
import time
from email.message import EmailMessage
from pathlib import Path
from subprocess import PIPE, Popen
from urllib.parse import urljoin

import markdownify
import requests  # https://docs.python-requests.org/en/master/
from bs4 import BeautifulSoup

import config

OUTPUT_FILE = "out.md"


def main():
    """Check for new bookable times at Folktandvården."""
    if Path(OUTPUT_FILE).is_file():
        with open(OUTPUT_FILE, "r") as f:
            old_content = f.read()
    else:
        old_content = ""

    url = "https://folktandvarden.vgregion.se/boka-besokstider/AvailableAppointments/"

    data = [
      ('undefined', 'undefined'),
      # Göteborg
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000144'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000146'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000015795'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000147'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000148'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000149'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000155'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000231'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000152'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000012121'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000010399'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000154'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000010587'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000157'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000158'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000160'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000161'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000011956'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000232'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000164'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000165'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000166'),
      # Mölndal
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000137'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000138'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000136'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000005700'),
      ('AppointmentSearchViewModel.SelectedClinincs', 'SE2321000131-E000000000139'),
      ('isLastMinute', 'true'),
    ]

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en;q=0.9,sv;q=0.8,de-DE;q=0.7,de;q=0.6',
        'cache-control': 'max-age=0',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': 'epi-cms-public-1-ext-got-adc-insert=3596527244.47873.0000; ASP.NET_SessionId=kusp0s0wthg1ox2s03hw51ox; TS01608e63=01c69f8384df64b985e5a250e16301ccb4dbe86ae07f2d85373a2678abef60e31284f38cf59e63934e0685c70b76014b8fc87299f6629a82f54ac81fa57e9b173f7fa41b678ea45d3811fbc397e88cc48271e46d5a; TSdbca8b71027=0857e74f39ab200050768e6df49cfb9be85d99810581f8d02ce7ccfb195fa1a05cd7e7cdfeb313b3087ebae0ad11300018f5fbf09d3b4175b5879546eead6c21debbe07e551170c188891b6859ea87e6ced3fa3fc03e8c7cee9a6a57a671e19d',
        'origin': 'https://folktandvarden.vgregion.se',
        'referer': 'https://folktandvarden.vgregion.se/',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36'
    }

    # Try multiple times if request fails
    for _x in range(5):
        try:

            response = requests.post(url, data, headers=headers)
            # print(response.text)

            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            interesting_area = soup.find("main").find("div", {"class": "ftv-booking__tightblock"})

            for tag in ["button", "form", "input"]:
                for t in interesting_area.find_all(tag):
                    t.decompose()

            interesting_area.find("div", "block__generic-body").unwrap()
            interesting_area.find("div", "block__header").unwrap()
            interesting_area.find("ol", "vgr-pagination").decompose()

            # Make URLs absolute
            for a in interesting_area.find_all("a"):
                a["href"] = urljoin(url, a.get("href"))

            # print(interesting_area)

            # Convert to markdown
            md = markdownify.markdownify(str(interesting_area), heading_style="ATX")
            md = md.strip()
            md = re.sub("\n+", "\n", md)

            # Send email and save output if there is any new information
            if (md != "# Lediga tider\nTyvärr finns det inga sista minuten-tider tillgängliga just nu.") and (md != old_content):
                send_email(str(interesting_area))
                with open(OUTPUT_FILE, "w") as f:
                    f.write(md)
            break

        except AttributeError:
            time.sleep(10)


def send_email(content):
    """Compose and send email."""
    sender = config.sender
    subject = "Nya lediga tider hos Folktandvården"

    msg = EmailMessage()
    msg.set_content(content, subtype="html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = config.receiver

    p = Popen(["/usr/sbin/sendmail", "-t"], stdin=PIPE)
    p.communicate(msg.as_bytes())


if __name__ == '__main__':
    main()
