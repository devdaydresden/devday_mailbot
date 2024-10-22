#!/usr/bin/env python3
#
# Copyright 2024 Dev Day Dresden e.V.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
from email.message import EmailMessage
from email.parser import BytesParser
from imaplib import IMAP4, IMAP4_SSL
from smtplib import SMTP
from typing import Iterable
from urllib.parse import urlparse

from requests import get


def fetch_latest_mails(imap_conn: IMAP4) -> Iterable[bytes]:
    imap_conn.select()
    typ, data = imap_conn.search(None, "NOT SEEN")
    if typ != "OK":
        raise RuntimeError("Error fetching latest mails")
    result = []

    for num in data[0].split():
        typ, message = imap_conn.fetch(num, "(RFC822)")
        if typ != "OK":
            raise RuntimeError(f"Error fetching mail {num}")
        print("Fetched mail", num.decode("utf-8"))
        result.append(message[0][1])

    return result


class AddressSource:
    def get_addresses(self) -> list[str]:
        raise NotImplementedError("must be implemented in subclass")


class FileAddressSource(AddressSource):
    def __init__(self, filename: str):
        self.filename = filename

    def get_addresses(self) -> list[str]:
        with open(self.filename, "r", encoding="utf-8") as sourcefile:
            return sourcefile.readlines()


class PretixAddressSource(AddressSource):
    def __init__(self, token, netloc, path):
        self.token, self.netloc, self.organizer = token, netloc, path[1:]

    def get_addresses(self) -> list[str]:
        r = get(
            f"https://{self.netloc}/api/v1/organizers/{self.organizer}/customers/",
            headers={"Authorization": f"Token {self.token}"},
        )
        r.raise_for_status()
        return [
            c["email"].lower()
            for c in r.json()["results"]
            if c["is_active"] and c["is_verified"]
        ]


def determine_address_source(src_url: str) -> AddressSource:
    url = urlparse(src_url)

    if url.scheme == "file":
        return FileAddressSource(url.path)

    if url.scheme == "pretix":
        return PretixAddressSource(url.password, url.hostname, url.path)

    raise ValueError(f"unsupported URL scheme {url.scheme}")


def process_mail(
    smtp_conn: SMTP, address_source: AddressSource, sender_address: str, mail: bytes
):
    email_parser = BytesParser()
    mail_data = email_parser.parsebytes(mail)

    new_message = EmailMessage()
    new_message.add_header("Subject", mail_data.get("Subject"))
    new_message.add_header("From", sender_address)
    new_message.add_header("Date", mail_data.get("Date"))
    new_message.add_header("Content-Type", mail_data.get_content_type())
    if "Reply-To" in mail_data:
        new_message.add_header("Reply-To", mail_data.get("Reply-To"))
    new_message.set_payload(mail_data.get_payload())

    smtp_conn.send_message(new_message, sender_address, address_source.get_addresses())


def main():
    imap_host = os.getenv("MAILBOT_IMAP_HOST", "localhost")
    imap_port = int(os.getenv("MAILBOT_IMAP_PORT", "143"))
    imap_user = os.getenv("MAILBOT_IMAP_USER")
    imap_password = os.getenv("MAILBOT_IMAP_PASSWORD")

    smtp_host = os.getenv("MAILBOT_SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("MAILBOT_SMTP_PORT", "25"))
    smtp_user = os.getenv("MAILBOT_SMTP_USER")
    smtp_password = os.getenv("MAILBOT_SMTP_PASSWORD")

    sender_address = os.getenv("MAILBOT_SENDER_ADDRESS", "Mailbot <info@example.org")
    address_source_url = os.getenv("MAILBOT_ADDRESS_SOURCE")
    address_source = determine_address_source(address_source_url)

    with IMAP4_SSL(imap_host, imap_port) as imap_conn:
        try:
            imap_conn.login(imap_user, imap_password)
            mails = fetch_latest_mails(imap_conn)
        finally:
            imap_conn.close()
            imap_conn.logout()

    with SMTP(smtp_host, smtp_port) as smtp_conn:
        smtp_conn.ehlo_or_helo_if_needed()
        smtp_conn.starttls()
        smtp_conn.login(smtp_user, smtp_password)

        for mail in mails:
            process_mail(
                smtp_conn,
                address_source,
                sender_address,
                mail,
            )


if __name__ == "__main__":
    main()
