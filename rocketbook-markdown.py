import time
import os
from imapclient import IMAPClient
import email
import datetime
import markdown
import html2text
import traceback
import re
import config

server = None

def print_debug(text):
    if config.DEBUG:
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

def process_mail_with_notes():
    global server
    if server is None:
        return

    # today = datetime.date.today()
    # # yesterday = today - datetime.timedelta(days=1)
    # day_str = today.strftime('%d-%b-%Y')
    # status, messages = server.search(None, '(SINCE "%s")' % day_str)

    # Search for unseen messages
    messages = server.search("UNSEEN")
    # messages = server.search("ALL")

    for uid, message_data in server.fetch(messages, "RFC822").items():
        message = email.message_from_bytes(message_data[b"RFC822"])
        print(uid, message.get("From"), message.get("Subject"))

        subject = message.get("Subject")
        print_debug(f"Subject: {subject}")

        match_title = re.match(r'^(.+?)-(\d+\.\d+\.\d+) \[.*?\]', subject)
        if match_title is not None:
            # Regex found a match
            note_title = match_title.group(1)
            # Check if there is a note title found in subject
            note_date = match_title.group(2)
        else:
            # No match with the subject default the title to Rocketbook with timestamp HH.MM.SS
            note_date = datetime.datetime.now().strftime('%H.%M.%S')
            note_title = f'Rocketbook-{note_date}'

        # Get the tags from the subject
        tags = re.findall(r'\[(.*?)\]', subject)

        # if no tags found default to Rocketbook
        if len(tags) == 0:
            tags = ['Rocketbook']

        print_debug(f"Note title: {note_title}, tag(s): {tags} " )

        # Check if there is an 'application/plain' attachment
        ocr_text_source = 'text/html' # Default, the text is in the email body and not as an attachment
        for part in message.walk():
            # print(f"Content type: {part.get_content_type()}")
            if part.get_content_type() == 'application/plain':
                # There is a plain text attachment with the OCR
                ocr_text_source = 'application/plain'

        print_debug("OCR text source: " + ocr_text_source)

        # Loop through the attachments
        for part in message.walk():
            print(f"Content type: {part.get_content_type()}")
            if part.get_content_type() == ocr_text_source:
                print(f"{part}")
                # Get the attachment
                attachment = part.get_payload(decode=True)
                print_debug(attachment.decode('utf-8'))
                text = attachment.decode('utf-8')

                # Convert plain text to Markdown which contains HTML
                html_text = markdown.markdown(text)
                # print_debug(html_text)

                if config.CONFIG_REMOVE_LINE_ENDINGS:
                    h = html2text.HTML2Text()
                    h.ignore_images = True
                    html_text2 = h.handle(html_text)

                # Improve the Markdown output
                markdown_text = html_text2.replace('<h1>', '# ').replace('</h1>', '')
                markdown_text = html_text2.replace('<h2>', '## ').replace('</h2>', '')
                markdown_text = html_text2.replace('<h3>', '### ').replace('</h3>', '')
                markdown_text = html_text2.replace('<p>', '\n').replace('</p>', '\n')
                markdown_text = html_text2.replace('<strong>', '**').replace('</strong>', '**')
                markdown_text = html_text2.replace('<em>', '*').replace('</em>', '*')
                markdown_text = html_text2.replace('<br>', '\n')

                # Make a link at the top of the page in the markdown text to the pdf file
                pdf_file = None
                for part in message.walk():
                    if part.get_content_type() == 'application/pdf':
                        pdf_file = part.get_payload(decode=True)
                        break
                if pdf_file:
                    if config.DATE_IN_FILENAME:
                        pdf_filename = f"{note_title}-{note_date}.pdf"
                    else:
                        pdf_filename = f"{note_title}.pdf"
                    with open(pdf_filename, 'wb') as f:
                        f.write(pdf_file)
                    time_format = note_date.replace('.', ':')
                    markdown_text = config.get_pdf_link_text(time_format, pdf_filename, pdf_filename) + markdown_text

                # Store the markdown in a file
                if config.DATE_IN_FILENAME:
                    markdown_filename = f"{note_title}-{note_date}.md"
                else:
                    markdown_filename = f"{note_title}.md"
                with open(markdown_filename, 'w') as f:
                    f.write(markdown_text)

                if config.DEBUG:
                    # Store the HTML in a file for debugging/checking
                    if config.DATE_IN_FILENAME:
                        html_filename = f"{note_title}-{note_date}.html"
                    else:
                        html_filename = f"{note_title}.html"
                    with open(html_filename, 'w') as f:
                        f.write(html_text)
                else:
                    html_filename = None

                # Move the markdown file to the correct folder
                folder_name = tags[0] # Take the first tag for the folder
                if folder_name in config.TAG_TO_PATH_CONVERSION:
                    folder_name = config.TAG_TO_PATH_CONVERSION[folder_name]

                # Check if the folder exists
                if not os.path.exists(folder_name):
                    # Create the folder
                    os.makedirs(folder_name)

                # Move the Markdown file
                move_file_to_folder_and_check_if_exists(markdown_filename, folder_name, note_title, note_date)
                if html_filename:
                    # Move the HTML file if it exists
                    move_file_to_folder_and_check_if_exists(html_filename, folder_name, note_title, note_date)
                if pdf_file:
                    # Move the PDF file if it exists
                    move_file_to_folder_and_check_if_exists(pdf_filename, folder_name, note_title, note_date)

def check_idle_capability(server):
    # Send a "CAPABILITY" command
    response = server.capabilities()
    # print_debug(f"Capabilities: {response}")

    # Check the "IDLE" capability
    if b"IDLE" in response:
        print_debug("Server supports IDLE")
        return True
    else:
        print("Server does not support IDLE")
        return False

def connect_to_imap():
    try:
        server = IMAPClient(config.IMAP_SERVER, timeout=config.IDLE_MODE_TIMEOUT)
        server.login(config.USERNAME, config.PASSWORD)
        server.select_folder(config.MAILBOX_FOLDER)
        return server
    except Exception as e:
        print_debug(f'ERROR while connecting to IMAP-server: {e}')
        return None

def main():
    global server

    test_mode = False
    exit_loop = False
    while not exit_loop:
        if server is None:
            # No server connection, try to connect
            print_debug("No server connection, connect to IMAP server")
            server = connect_to_imap()
            if server is None:
                # Connect failed, sleep for a while and try again
                time.sleep(900) # 15 minutes
            else:
                if not check_idle_capability(server):
                    server.logout()
                    time.sleep(60)
                    exit(1)
            if server is None:
                # No server connection, sleep for a while
                print_debug("No server connection, sleep for a while")
                time.sleep(300)

        if server is not None:
            # Server connection OK, process mail

            if not test_mode:
                # Start IDLE mode
                server.idle()
                print_debug("Idle mode activated, wait for new mail")

                while not exit_loop:
                    try:
                        # Wait for up to 30 seconds for an IDLE response
                        responses = server.idle_check()
                        # print_debug(f"Server sent: {responses}")

                        if responses:
                            # Response from IDLE mode
                            for response in responses:
                                print(f"Server sent: {response}")
                                # Loop through the responses
                                if response[1] == b'EXISTS':
                                    print_debug("Mailbox updated")
                                    # Stop IDLE mode while processing the mail
                                    server.idle_done()

                                    process_mail_with_notes()

                                    # Enable IDLE mode again
                                    server.idle()
                            
                    except KeyboardInterrupt:
                        exit_loop = True
                        break

                server.idle_done()
                print_debug("\nIDLE mode done")
            else:
                process_mail_with_notes()
                exit_loop = True
            server.logout()

if __name__ == '__main__':
    main()
