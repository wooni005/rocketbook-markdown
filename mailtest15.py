# List number of messages in INBOX folder
# and print details of the messages that are not deleted

from imapclient import IMAPClient
import config

server = IMAPClient(config.IMAP_SERVER)
server.login(config.USERNAME, config.PASSWORD)
server.select_folder("INBOX")

select_info = server.select_folder("INBOX")
print("%d messages in INBOX" % select_info[b"EXISTS"])



messages = server.search(["NOT", "DELETED"])
print("%d messages that aren't deleted\n" % len(messages))

print(f"Messages: {messages}")

response = server.fetch(messages, ["FLAGS", "RFC822.SIZE"])
for msgid, data in response.items():
    print(
        "   ID %d: %d bytes, flags=%s" % (msgid, data[b"RFC822.SIZE"], data[b"FLAGS"])
    )

server.logout()
