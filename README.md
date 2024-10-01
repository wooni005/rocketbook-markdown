# Rocketbook to Markdown

This script is waiting for a Rocketbook email with a PDF and a OCR text attachment. When receiving an email it converts the contents automatically to Markdown and puts it in the right notes folder.

## What is a Rocketbook?

A [Rocketbook](https://getrocketbook.com/) is a reusable notebook that combines traditional handwriting with digital technology. You write on the pages with a special pen (Pilot Frixion), and then use a smartphone app to scan your notes and save them to the cloud. The pages can be erased with water or a microwave, making them endlessly reusable. It's a great way to stay organized while reducing paper waste.

## How does it work?

The script reads the Rocketbook email, which contains a PDF and an OCR text attachment.
The subject of the email is used for the filename of the note, the tags between brackets are used to store the content in the correct notes folder.
The script converts the PDF to Markdown and puts it in the right folder. Also the PDF will be moved to this folder with the same filename. At the top of the Markdown file is a link to the original PDF.

Why is **IMAP IDLE** used? With the IMAP IDLE command, the conversion is responding immediately. It is also possible to check the mail on polling base, but to many requests to the IMAP server is not recommended. Your account can be suspended if you put the delay time too short. So IMAP IDLE is ideal, it is constantly waiting for a new mail.
Remark: With the IDLE command, this script is constantly waiting for a new mail. But the IMAP servers are not giving imidiately a response. It can take some time to get a response, to speed up the waiting, you can use an external IMAP client and sync the mail, this will trigger also the IDLE command of this script.

## Installation

```bash
# Go to your home directory
$ cd

# Clone the repository and enter the directory
$ git clone https://github.com/wooni005/rocketbook-markdown.git
$ cd rocketbook-markdown

# Make the script executable
$ chmod +x rocketbook-markdown.py
```

Install the required Python3 modules:
```bash
$ sudo pip3 install imaplib2 email python-markdown html2text
```

## Configuration

Create a configuration file in the `config.py` file with the example file as a template:

```bash
$ cd rocketbook-markdown
$ cp config.py.example config.py
```

Fill in your IMAP mailserver settings and the corresponding credentials to read the IMAP folder and fill in the other settings for the conversion process.

```bash
$ nano config.py

# Mail settings
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
USERNAME = 'your@email'
PASSWORD = 'yourPassword'
MAILBOX_FOLDER = "Rocketbook"
MAIL_CHECK_INTERVAL = 60 # [sec]

# Conversion settings
DATE_IN_FILENAME = False
CONFIG_REMOVE_LINE_ENDINGS = True
TAG_TO_PATH_CONVERSION = {
    'Rocketbook': 'notes/rocketbook', # Default tag with default path
    'YourTag1': '/your/path/for/your/notes_tag1',
    'YourTag2': '/your/path/for/your/notes_tag2',
}
```

## Configuration settings

**IMAP_SERVER**: IMAP server address.
**IMAP_PORT**: IMAP server SSL port.
**USERNAME**: IMAP username. Your email adress at this mail server.
**PASSWORD**: IMAP password. When using Gmail, generate a new app password here: https://myaccount.google.com/apppasswords

**MAILBOX_FOLDER**: IMAP folder. The default value is "Rocketbook", make sure all email from Rocketbook is moved to this folder. If you put here "INBOX", all incoming emails will be processed, also the not Rocketbook emails. Make a filter in your mailbox to achieve this.

**MAIL_CHECK_INTERVAL** is the time in seconds between each check of the IMAP folder. The default value is 60 seconds.
Remark! Don't use a too short interval, risk that your account will be suspended.

**DATE_IN_FILENAME**: When set to True, the date is added to the filenames. The default value is False. This is handy when you scan multiple times the same notes.

**CONFIG_REMOVE_LINE_ENDINGS**: Set to True if you want to remove line endings from the converted files. The default value is True.
In case you want to keep line endings, like in the notes, set it to False.

**TAG_TO_PATH_CONVERSION**: Set the tags and their corresponding paths. The default value is the Rocketbook tag with the default path.

**DEBUG**: Set to True if you want to debug the script. The default value is False.

## Rocketbook Destination Settings

Open de Rocketbook application and perform the following settings:

- Settings - Handwriting Recognition (OCR)
  - Smart Titles: **Enable**
  - Use Smart Titles to group scans: **Disable**
  - Smart Search: **Enable**
  - Smart lists: **Disable** (Is making automatically todo lists for you)
  - Smart Tags: **Disable** (Is only for Rocketbook Pro pages)
- File Naming Template: **Page-Time**
- Email Naming Template: **Filename-Time**

Destinations: Pick one of the icons you want to use for this script:
- Change Recipient: **'your@email'** (Your email address which is used in the script)
- Change Destination: **Email**
- File Type: **PDF**
- Bundle Scans: **Enable**
- OCR Transription: **Enable**
  - Attach: **Enable**
- Send Smart Tag: **Enable**
- Smart Tag Subject Line: **Enable**

## Testing the script

```bash
# Put on the DEBUG mode
$ nano rocketbook-markdown.py
...
DEBUG = True
...

# Run the script
$ python3 rocketbook-markdown.py
```

## Run the script as a service

If everything works nicely, you can run the script as a service.
Remark: Make sure that you switch off the DEBUG mode before running the service.

```bash
$ cd rocketbook-markdown
# Copy the service file to the system
$ sudo cp rocketbook-markdown.service /etc/systemd/system

# Reload the service file
$ systemctl daemon-reload

# Enable and start the service
$ systemctl enable rocketbook-markdown
$ systemctl start rocketbook-markdown
```

## OCR tips for better results

For OCR software it is not easy to read your handwriting. Here are some tips for better results.

1. Take a clear and stable image with enough light to get high contrast
2. Place the Rocketbook notes on a flat surface and take the picture right above the Rocketbook and not in an angle
3. Use block letters in your Rocketbook notes
4. Keep a open line between two written lines if the software is mixing lines
5. Keep the surface clean, leaving some rest after erasing a mistake gives strange results
6. Try other scan settings for better results, menu: Settings > Scan Settings > Rocketbook Enhancement Type

Here are some other tips:
- https://getrocketbook.com/blogs/news/rocket-labs-002-improve-formatting-in-ocr-transcription
- https://youtu.be/R3BSJtiiCIo

## Tips for improving the conversion process

1. Use the Smart Titles feature in Rocketbook, the Smart Titles are used for the filename, otherwise the default is `Rocketbook`
2. Tags are used for to store the notes in the correct folder, the default is the Rocketbook folder, see config.py

## Use Markdown in the Rocketbook notes

It is possible to use Markdown format already in your notes, so you don't need to edit them afterwards.

For example you use the following Markdown syntax in your Rocketbook handwritten notes:

- Headings: H1='#', H2='##', H3='###', etc
- Bullet lists with dashes: - or *
- Numbered lists with numbers: 1. etc
- Bold: **bold**
- Italic: _italic_ or *italic*
- Strikethrough (~): ~~strikethrough~~
- Code: (`) `code`
- Links: `[text](url)`
- Images: `![alt text](url)`

To get also a drawing from your Rocketbook notes, I'm taking a screenshot of the drawing in the PDF and past that in the Markdown file.

## OCR processing locally

My plan was to add the possibility to scan with JPG do the OCR locally, but the Rocketbook OCR is much more precise.
Also tested some more OCR tools, but never better than the Rocketbook one.

```bash
$ sudo apt-get install tesseract-ocr libssl-dev
$ sudo pip3 install Pillow pytesseract opencv-python
```

Then run the script with the JPG file as input.

```python
import pytesseract
from PIL import Image

# Open the JPEG image file
image = Image.open('image.jpg')

# Process the image with Tesseract
text = pytesseract.image_to_string(image)

# Print the extracted text
print(text)
```

# Tips and tricks

## Google Workspace

I'm using Google Workspace and I couldn't get the IDLE mode working. When testing on capability, it returns that the IDLE command is supported, but it doesn't work. It waits forever on the IDLE command and doesn't report that a new email is received. I'm not sure why, I checked all settings in the IMAP admin settings, everything seems to be set OK. Please use a normal Gmail account and forward it to your Google Workspace email account if you like to have it there, but it is not necessary.
