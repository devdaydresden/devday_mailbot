#!/usr/bin/env python3
import os

from devday_mailbot import determine_address_source

if __name__ == "__main__":
    address_source_url = os.getenv("MAILBOT_ADDRESS_SOURCE")
    if not address_source_url:
        print("set MAILBOT_ADDRESS_SOURCE environment variable")
        exit(1)

    source = determine_address_source(address_source_url)

    for address in source.get_addresses():
        print(address)
