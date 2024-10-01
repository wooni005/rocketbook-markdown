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
server.select_folder(config.MAILBOX_FOLDER)

response = server.capabilities()
print(f"Capabilities: {response}")

if b"IDLE" in response:
    print("Server supports IDLE")
else:
    print("Server does not support IDLE")
    server.logout()
    exit(1)

# Start IDLE mode
server.idle()
print("Idle mode activated")

while True:
    try:
        # Wait for up to 30 seconds for an IDLE response
        responses = server.idle_check()
        print(f"Server sent: {responses}")

        if responses:
            # Loop door de updates
            for response in responses:
                print(f"Server sent: {response}")
                msg_id = response[0]
                messages = response[1]
                # print(f"Number: {msg_id} messages: {messages}")
                if messages == b'EXISTS':
                    print("Mailbox updated")
                    server.idle_done()

                    # Search for unseen messages
                    messages = server.search("UNSEEN")
                    for uid, message_data in server.fetch(messages, "RFC822").items():
                        email_message = email.message_from_bytes(message_data[b"RFC822"])
                        print(uid, email_message.get("From"), email_message.get("Subject"))

                    # messages = server.search(["NOT", "DELETED"])
                    # print("%d messages that aren't deleted\n" % len(messages))

                    # print(f"Messages: {messages}")

                    # response = server.fetch(messages, ["FLAGS", "RFC822.SIZE"])
                    # for msgid, data in response.items():
                    #     print(
                    #         "   ID %d: %d bytes, flags=%s" % (msgid, data[b"RFC822.SIZE"], data[b"FLAGS"])
                    #     )

                    server.idle()

    except KeyboardInterrupt:
        break

server.idle_done()
print("\nIDLE mode done")
server.logout()