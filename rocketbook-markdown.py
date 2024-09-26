import time
import os
import imaplib2
import datetime
import email
import markdown
import html2text
import traceback
import re
import config

DEBUG = True
idle_command = False
mail = None

def print_debug(text):
    if DEBUG:
        print(text)

def move_file_to_folder_and_check_if_exists(filename_org, target_folder_name, note_title, note_date):
    if not os.path.exists(os.path.join(target_folder_name, filename_org)):
        # If the file doesn't exist in the target folder, move it to the folder
        os.replace(filename_org, os.path.join(target_folder_name, filename_org))
    else:
        # If the file exists, add a number to the end of the filename
        count = 1
        filename_new = f"{note_title}-{note_date}-{count}.md"
        while os.path.exists(os.path.join(target_folder_name, filename_new)):
            count += 1
            filename_new = f"{note_title}-{note_date}-{count}.md"
        os.replace(filename_org, os.path.join(target_folder_name, filename_new))

def process_mail_with_notes(mail):
    if mail is None:
        return

    # today = datetime.date.today()
    # # yesterday = today - datetime.timedelta(days=1)
    # day_str = today.strftime('%d-%b-%Y')
    # status, messages = mail.search(None, '(SINCE "%s")' % day_str)

    # status, messages = mail.search(None, '(UNSEEN)')
    status, messages = mail.search(None, 'ALL')

    print_debug(f"Status: {status} Number of unread messages: {len(messages[0].split())}")

    if status == 'OK':
        # Loop door de emails
        for num in messages[0].split():
            status, msg = mail.fetch(num, '(RFC822)')
            raw_message = msg[0][1].decode('utf-8')

            # print_debug(f"Message {raw_message}")
            # Parse de email
            # if isinstance(raw_message, int):
            #     print("Error: raw_message is an integer")
            #     print(raw_message)
            #     continue

            # message = email.message_from_bytes(raw_message)
            message = email.message_from_string(raw_message)

            subject = message['Subject']
            print_debug(subject)

            # match_title = re.match(r'^(.+?)-(\d+\.\d+\.\d+) \[.*?\]', subject)
            # if match_title is not None:
            #     # Regex found a match
            #     note_title = match_title.group(1)
            #     # Check if there is a note title found in subject
            #     note_date = match_title.group(2)
            # else:
            #     # No match with the subject default the title to Rocketbook with timestamp HH.MM.SS
            #     note_date = datetime.datetime.now().strftime('%H.%M.%S')
            #     note_title = f'Rocketbook-{note_date}'

            # # Get the tags from the subject
            # tags = re.findall(r'\[(.*?)\]', subject)

            # # if no tags found default to Rocketbook
            # if len(tags) == 0:
            #     tags = ['Rocketbook']

            # print_debug(f"Note title: {note_title}, tag(s): {tags} " )

            # # Check if there is an 'application/plain' attachment
            # ocr_text_source = 'text/html' # Default, the text is in the email body and not as an attachment
            # for part in message.walk():
            #     if part.get_content_type() == 'application/plain':
            #         # Yeah, there is a plain text attachment with the OCR
            #         ocr_text_source = 'application/plain'

            # # Loop through the attachments
            # for part in message.walk():
            #     if part.get_content_type() == ocr_text_source:
            #         print_debug("OCR text source: " + part.get_content_type())
                    # Get the attachment
                    # attachment = part.get_payload()
                    # print_debug(attachment.decode('utf-8'))
                    # text = attachment.decode('utf-8')

            #         # Convert plain text to Markdown which contains HTML
            #         html_text = markdown.markdown(text)
            #         # print_debug(html_text)

            #         if config.CONFIG_REMOVE_LINE_ENDINGS:
            #             h = html2text.HTML2Text()
            #             h.ignore_images = True
            #             html_text2 = h.handle(html_text)

            #         # Improve the Markdown output
            #         markdown_text = html_text2.replace('<h1>', '# ').replace('</h1>', '')
            #         markdown_text = html_text2.replace('<h2>', '## ').replace('</h2>', '')
            #         markdown_text = html_text2.replace('<h3>', '### ').replace('</h3>', '')
            #         markdown_text = html_text2.replace('<p>', '\n').replace('</p>', '\n')
            #         markdown_text = html_text2.replace('<strong>', '**').replace('</strong>', '**')
            #         markdown_text = html_text2.replace('<em>', '*').replace('</em>', '*')
            #         markdown_text = html_text2.replace('<br>', '\n')

            #         # Make a link at the top of the page in the markdown text to the pdf file
            #         pdf_file = None
            #         for part in message.walk():
            #             if part.get_content_type() == 'application/pdf':
            #                 pdf_file = part.get_payload(decode=True)
            #                 break
            #         if pdf_file:
            #             if config.DATE_IN_FILENAME:
            #                 pdf_filename = f"{note_title}-{note_date}.pdf"
            #             else:
            #                 pdf_filename = f"{note_title}.pdf"
            #             with open(pdf_filename, 'wb') as f:
            #                 f.write(pdf_file)
            #             time_format = note_date.replace('.', ':')
            #             markdown_text = config.get_pdf_link_text(time_format, pdf_filename, pdf_filename) + markdown_text

            #         # Store the markdown in a file
            #         if config.DATE_IN_FILENAME:
            #             markdown_filename = f"{note_title}-{note_date}.md"
            #         else:
            #             markdown_filename = f"{note_title}.md"
            #         with open(markdown_filename, 'w') as f:
            #             f.write(markdown_text)

            #         if DEBUG:
            #             # Store the HTML in a file for debugging/checking
            #             if config.DATE_IN_FILENAME:
            #                 html_filename = f"{note_title}-{note_date}.html"
            #             else:
            #                 html_filename = f"{note_title}.html"
            #             with open(html_filename, 'w') as f:
            #                 f.write(html_text)
            #         else:
            #             html_filename = None

            #         # Move the markdown file to the correct folder
            #         folder_name = tags[0] # Take the first tag for the folder
            #         if folder_name in config.TAG_TO_PATH_CONVERSION:
            #             folder_name = config.TAG_TO_PATH_CONVERSION[folder_name]

            #         # Check if the folder exists
            #         if not os.path.exists(folder_name):
            #             # Create the folder
            #             os.makedirs(folder_name)

            #         # Move the Markdown file
            #         move_file_to_folder_and_check_if_exists(markdown_filename, folder_name, note_title, note_date)
            #         if html_filename:
            #             # Move the HTML file if it exists
            #             move_file_to_folder_and_check_if_exists(html_filename, folder_name, note_title, note_date)
            #         if pdf_file:
            #             # Move the PDF file if it exists
            #             move_file_to_folder_and_check_if_exists(pdf_filename, folder_name, note_title, note_date)

def check_idle_capability(mail):
    # Send a "CAPABILITY" command
    cap_response = mail.capability()[1][0].decode('utf-8')
    # print_debug(cap_response)

    # Check the "IDLE" capability
    if 'IDLE' in cap_response:
        print_debug("The server supports IDLE mode")
        return True
    else:
        print_debug("The server does not support IDLE mode")
        return False

def connect_to_imap():
    try:
        mail = imaplib2.IMAP4_SSL(config.IMAP_SERVER, config.IMAP_PORT)
        mail.login(config.USERNAME, config.PASSWORD)
        mail.select(config.MAILBOX_FOLDER)
        return mail
    except Exception as e:
        print_debug(f'ERROR while connecting to IMAP-server: {e}')
        return None

def reconnect_to_imap(mail):
    try:
        mail.logout()
        mail = connect_to_imap()
        return mail
    except Exception as e:
        print_debug(f'ERROR while reconnecting to IMAP-server: {e}')
        return None

def main():
    global mail

    starting_up = True
    while True:
        if mail is None:
            print_debug("No server connection, connect to IMAP server")
            mail = connect_to_imap()
            if mail is None:
                # Connect failed, sleep for a while and try again
                time.sleep(config.MAIL_CHECK_INTERVAL)
            else:
                # Connect successful, check if the server supports IDLE
                if not config.FORCE_DISABLE_IDLE_COMMAND:
                    idle_command = check_idle_capability(mail)
                else:
                    # For example for Google Workspace, the server does not work well with IDLE
                    idle_command = False

        if mail is not None:
            try:
                if not idle_command:
                    # Not using IDLE, so connect to the server
                    mail = connect_to_imap()
                else:
                    # Using IDLE, so wait for new mail
                    print_debug("Wait for new mail with IDLE command")
                    if not starting_up:
                        status, data = mail.idle()

                        if status == 'OK':

                            print_debug("Server connection OK")
                        else:
                            print_debug("Server connection not OK, send NOOP command to test the server connection")
                            response = mail.noop()
                            print_debug(f"NOOP response: {response}")

                        print_debug(f"typ: {status} data: {data}")
                    else:
                        starting_up = False
                
                process_mail_with_notes(mail)

                if idle_command:
                    # When using IDLE, we need to send DONE to the server
                    print_debug("Let the server know the processing is done")
                    mail.send(b'DONE\r\n')
                else:
                    # When not using IDLE, close the connection and sleep for a while
                    mail.close()
                    mail.logout()
                    print_debug("No IDLE command just sleep for a while")
                    time.sleep(config.MAIL_CHECK_INTERVAL)

            except Exception as e:
                print_debug(f'ERROR while getting notes from IMAP-server: {e}')
                print_debug(traceback.format_exc())
                mail = reconnect_to_imap(mail)
                if mail is None:
                    # Reconnect failed, sleep for a while and try again
                    time.sleep(config.MAIL_CHECK_INTERVAL)

if __name__ == '__main__':
    main()
