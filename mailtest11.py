import time
import imap_client as imapclient
import socket
import config
import email

def process_mail(msg_numbers):
    # msg_numbers is a list of message numbers
    print("Nieuwe email ontvangen!")
    print(msg_numbers)

    for number in msg_numbers:
        status, message = client.fetch(number)
        # print(f"Status: {status} Message: {message}")

        # mail_data = response.split()[1:]
        mail_message = email.message_from_string(message)
        print("Onderwerp:", mail_message['Subject'])
        print("Van:", mail_message['From'])
        print("Datum:", mail_message['Date'])
        print("Inhoud:")
        print(mail_message.get_payload())

client = imapclient.ImapClient(config.IMAP_SERVER, config.IMAP_PORT, config.USERNAME, config.PASSWORD, config.MAIL_CHECK_INTERVAL)
ok = client.connect()
ok = client.select_mailbox(config.MAILBOX_FOLDER)

if ok:
    # response = client.search('UNSEEN')
    # status, msg_numbers = client.search('UNSEEN')
    # print(f"Status: {status} Number of unread messages: {msg_numbers}")
    # if msg_numbers is not None and len(msg_numbers) > 0:
    #     process_mail(msg_numbers)
    # else:
    #     # No new messages
    #     print("No new messages")

    while True:
        try:

            response = client.idle()

            if response is not None:
                if response.startswith('*'):
                    # Received update
                    print(f'Received update: {response}')
                    msg_numbers = response.split()[1]
                    print(f"Status: Number of unread messages: {msg_numbers}")
                    if msg_numbers is not None and len(msg_numbers) > 0:
                        client.done()
                        process_mail(msg_numbers)

                elif response.startswith('+'):
                    # No update
                    print('Ready with updates')


            # ok = client.select_mailbox(config.MAILBOX_FOLDER)
            # messages = client.search('ALL')
            # response = client.search('UNSEEN')
            # status, msg_numbers = client.search('UNSEEN')
            # print(f"Status: {status} Number of unread messages: {msg_numbers}")
            # if msg_numbers is not None and len(msg_numbers) > 0:
            #     process_mail(msg_numbers)
            # else:
            #     # No new messages
            #     print("No new messages")


                # if response is not None:
                #     if response.startswith('*'):
                #         # Received update
                #         print(f'Received update: {response}')

                #     elif response.startswith('+'):
                #         # No update
                #         print('Ready with updates')
                # while True:
                #     # Send the IDLE command
                #     response = client.noop()
                #     if response is not None:
                #         if response.startswith('*'):
                #             # Received update
                #             print(f'Received update: {response}')
                #             break
                #         elif response.startswith('+'):
                #             # No update
                #             print('Ready with updates')

                # # Done met het IDLE commando
                # client.done()            


        except socket.timeout:
            # Connection timed out
            print('Connection timed out: No msg received')
            # client.connect() # Reconnect
            # ok = client.select_mailbox(config.MAILBOX_FOLDER)

        # Wacht een paar seconden voordat je weer het IDLE commando stuurt
        time.sleep(1)

    client.close()
    client.logout()
