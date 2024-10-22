# Dev Day Mailbot

A small bot to fetch mails from an IMAP mailbox and resend them to a list of recipients.

## Running with Docker

```
docker build --tag devday-mailbot:latest .
docker run -it --rm \
   -v $(pwd)/addresses.txt:/addresses.txt:ro \
   -e MAILBOT_IMAP_HOST=<imap_server_address> \
   -e MAILBOT_IMAP_PORT=<imap_server_port> \
   -e MAILBOT_IMAP_USER=<imap_user> \
   -e MAILBOT_IMAP_PASSWORD=<imap_password> \
   -e MAILBOT_SMTP_HOST=<smtp_server_address> \
   -e MAILBOT_SMTP_PORT=<smtp_server_port> \
   -e MAILBOT_SMTP_USER=<smtp_user> \
   -e MAILBOT_SMTP_PASSWORD=<smtp_server_password> \
   -e MAILBOT_SENDER_ADDRESS=<name_and_email_address_of_mailbot> \
   -e MAILBOT_ADDRESS_SOURCE=<uri_of_address_source>
```

## Address sources

The mailbot can either use a text file containing a list of email addresses. The mail source URI uses the `file` scheme
in this case.

File URI Example:
```
file:///addresses.txt
```

The other supported URI scheme is `pretix`.

Pretix URI Example:
```
pretix://:<pretix_token>@pretix.eu/<organizer>
```

`<pretix_token>` is the token used to authenticate the mailbot with the pretix API. See the [Pretix Token authentication documentation](https://docs.pretix.eu/en/latest/api/tokenauth.html#rest-tokenauth).

`<organizer>` is the short name of the organizer. You can find valid organizer names at https://pretix.eu/control/organizers/.

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
