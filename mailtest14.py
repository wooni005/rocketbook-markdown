# Open a connection in IDLE mode and wait for notifications from the
# server.

from imapclient import IMAPClient
import email
import config
from enum import Enum
import socket

# import logging
# logging.basicConfig(
#     format='%(asctime)s - %(levelname)s: %(message)s',
#     level=logging.DEBUG
# )

server = IMAPClient(config.IMAP_SERVER, timeout=config.MAIL_CHECK_INTERVAL)
server.login(config.USERNAME, config.PASSWORD)
server.select_folder("INBOX")

# Start IDLE mode
server.idle()
print("Connection is now in IDLE mode, send yourself an email or quit with ^c")

while True:
    try:
        # Wait for up to 30 seconds for an IDLE response
        responses = server.idle_check(timeout=5)
        print(f"Server sent: {responses}")

        if responses or True:
            # Loop door de updates
            for response in responses:
                print(f"Server sent: {response}")
                msg_id = response[0]
                messages = response[1]
                print(f"Number: {msg_id} messages: {messages}")
                if messages == b'EXISTS':
                    print("Nieuw mailbericht ontvangen")
                    server.idle_done()

                    messages = server.search(["NOT", "DELETED"])
                    print("%d messages that aren't deleted\n" % len(messages))

                    print(f"Messages: {messages}")

                    response = server.fetch(messages, ["FLAGS", "RFC822.SIZE"])
                    for msgid, data in response.items():
                        print(
                            "   ID %d: %d bytes, flags=%s" % (msgid, data[b"RFC822.SIZE"], data[b"FLAGS"])
                        )

                    server.idle()

                    # Nieuw mailbericht ontvangen
                    # typ, data = server.search(None, ['UNSEEN'])
                    # msg_id = data[0].split()[-1]
                    # message_nrs = [5 , 6]
                    # print(f"Message numbers: {message_nrs}")
                    # status, message = fetch(msg_id)
                    # typ, data = server.fetch(message_nrs, ['INTERNALDATE', 'RFC822'])

                    # msg = email.message_from_bytes(data[0][1])
                    # Verwerk de e-mail hier (bijvoorbeeld print de afzender en onderwerp)
                    # print('Afzender:', msg['From'])
                    # print('Onderwerp:', msg['Subject'])


                    # messages = server.search('UNSEEN')
                    # for uid, message_data in server.fetch(messages, "RFC822").items():
                    #     email_message = email.message_from_bytes(message_data[b"RFC822"])
                    #     print(uid, email_message.get("From"), email_message.get("Subject"))                    
                    # message_nrs = [number]

                    # _, data = server.fetch(message_nrs, ["RFC822"])
                    # print(f"Data: {data}")
                    # if data:
                    #     msg = email.message_from_bytes(data[0][1])
                    #     # Process the email
                    #     print("Subject:", msg['Subject'])
                    #     print("From:", msg['From'])
                    #     print("Date:", msg['Date'])
                    #     print("Content:")
                    #     print(msg.get_payload())


        # Send NOOP command to keep the connection alive
        # server.noop()
    except KeyboardInterrupt:
        break

server.idle_done()
print("\nIDLE mode done")
server.logout()