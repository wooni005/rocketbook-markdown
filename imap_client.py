import imaplib
import email
import socket
import random

from enum import Enum

class Status(Enum):
    OK = 0
    FAIL = 1
    DONE = 2
    IDLING = 3
    TIMEOUT = 4


class ImapClient:
    """
    A class for interacting with an IMAP server and extending the imaplib module.
    """
    def __init__(self, host, port, username, password, timeout=30):
        """
        Initializes the ImapClient object.

        Args:
            host (str): The hostname of the IMAP server.
            port (int): The port number of the IMAP server.
            username (str): The username to use for authentication.
            password (str): The password to use for authentication.
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.tag_counter = 0
        self.server = None

    def generate_tag(self):
        """
        Generates a new tag for the current session.

        Returns:
            str: The generated tag.
        """
        self.tag_counter += 1
        tag = f"A{self.tag_counter:06}"
        return tag

    def connect(self) -> Status:
        """
        Connects to the IMAP server.

        Returns:
            bool: True if the connection was successful, False otherwise.

        Raises:
            imaplib.IMAP4_SSL.error: If the connection fails.
        """
        self.server = imaplib.IMAP4_SSL(self.host, self.port, timeout=self.timeout)
        response = self.server.login(self.username, self.password)

        print(f"login response: {response}")
        
        if response[0] == 'OK':
            print('Logged in successfully into the IMAP server.')
            return Status.OK
        else:
            print('Unable to login into the IMAP server.')
            return Status.FAIL

    def send(self, command):
        """
        Sends a command to the IMAP server

        Args:
            command (str): The command to send to the IMAP server.

        Returns:
            The response from the IMAP server.
        """
        tag = self.generate_tag()
        command = f"{tag} {command}\r\n"
        print(f"\n--> {command}", end="")
        self.server.send(command.encode('utf-8'))

        response = self.server.readline()
        response = response.decode()

        return response


    def send_and_check(self, command):
        """
        Sends a command to the IMAP server and checks the response.

        Args:
            command (str): The command to send to the IMAP server.

        Returns:
            Status: The status of the response.
            data: The data returned by the IMAP server.
        """
        data = None
        try:
            tag = self.generate_tag()
            command = f"{tag} {command}\r\n"
            print(f"\n--> {command}", end="")
            self.server.send(command.encode('utf-8'))

            print(f"Search for {tag} in response")
            status = Status.FAIL
            while True:
                response = self.server.readline()
                response = response.decode()

                if isinstance(response, list):
                    print(f"response: {response}", end="")
                    # response is a list, the first element is the status
                    if response[0] == 'OK':
                        status = Status.OK
                else:
                    print(f"Check response: {response}", end="")
                    # response is a string or multiple strings
                    if not response:
                        break  # No rows anymore
                    elif response.startswith(f"{tag} OK"):
                        # Last line of the response
                        status = Status.OK
                        break
                    elif response.startswith(f"{tag} NO"):
                        # Last line of the response
                        status = Status.FAIL
                        break
                    elif response.startswith("* SEARCH"):
                        # Get the message numbers
                        # Example: * SEARCH 6 7
                        data = response.split()[2:] # returns: ['6', '7']
                        # break
                    elif response.startswith("+ idling"):
                        # Idle mode untill new message received
                        # Example: + idling
                        pass
                    elif response.split(' ')[1] == 'OK':
                        # Detected OK in the response
                        status = Status.OK
                    elif response.startswith('*'):
                        pass
                        # Not the last line of the response yet
                        # messages.append(response.split()[1])

        except socket.timeout:
            self.connect() # Reconnect
            # Connection timed out
            status = Status.TIMEOUT
        return status, data

    def send_and_fetch(self, command, message_id=None):
        """
        Sends a command to the IMAP server and checks the response.

        Args:
            command (str): The command to send to the IMAP server.

        Returns:
            Status: The status of the response.
            data: The data returned by the IMAP server.
        """
        data = None
        try:
            tag = self.generate_tag()
            command = f"{tag} {command}\r\n"
            print(f"\n--> {command}", end="")
            self.server.send(command.encode('utf-8'))

            # print(f"Search for {tag} in response")
            status = Status.FAIL
            message = ''
            while True:
                response = self.server.readline()
                response = response.decode()

                # response is a string or multiple strings
                if not response:
                    break  # No rows anymore
                elif response.startswith(f"{tag} OK"):
                    # Last line of the response
                    print(f"Check FETCH response: {response}", end="")
                    status = Status.OK
                    break
                elif response.startswith(f"{tag} NO"):
                    # Last line of the response
                    print(f"Check FETCH response: {response}", end="")
                    status = Status.FAIL
                    break
                elif response.startswith(f"{tag} BAD"):
                    # Last line of the response
                    print(f"Check FETCH response: {response}", end="")
                    status = Status.FAIL
                    break
                elif response.startswith('* BYE'):
                    # The server has closed the connection
                    print(f"Check FETCH response: {response}", end="")
                    print("The server has closed the connection")
                    break
                elif response.startswith(f"* {message_id} FETCH"):
                    # Get the message numbers
                    # Example: * 6 FETCH (RFC822 {5462}
                    print(f"Check FETCH response: {response}", end="")
                    print("Start fetching message")
                    pass
                else:
                    message += response

            print(f"Check FETCH response: {response}")

        except socket.timeout:
            self.connect() # Reconnect
            # Connection timed out
            status = Status.TIMEOUT
        return status, message


    def select_mailbox(self, mailbox):
        """
        Selects a mailbox.

        Args:
            mailbox (str): The name of the mailbox to select.

        Returns:
            bool: True if the mailbox was selected successfully, False otherwise.

        Raises:
            imaplib.IMAP4_SSL.error: If the mailbox does not exist.
        """
        # response = self.server.select(mailbox)
        status, _ = self.send_and_check(f"SELECT {mailbox}")

        if status == Status.OK:
            print(f"Selected mailbox: {mailbox}")
            return True
        else:
            print(f"Unable to select mailbox: {mailbox}")
            return False

    def search(self, criteria):
        """
        Searches for messages in the selected mailbox.

        Args:
            criteria (str): The search criteria.

        Returns:
            list: A list of message IDs that match the search criteria.
        """
        return self.send_and_check(f"SEARCH {criteria}")

    def idle(self, timeout=None) -> Status:
        """
        Enables IDLE mode.

        Raises:
            imaplib.IMAP4_SSL.error: If IDLE mode cannot be enabled.
        """
        # response = self.send_and_check('IDLE')
        response = self.send('IDLE')
        print(f"IDLE response: {response}")

        # Wait for feedback
        response = self.server.readline().decode()
        print(f"IDLE response: {response}")

        # print(f"IDLE response: {response}")
        return response

    def noop(self):
        """
        Sends a NOOP command to the IMAP server.
        """
        response = self.send('NOOP')
        print(f"NOOP response: {response}")

    def fetch(self, message_id):
        """
        Fetches a message from the selected mailbox.

        Args:
            message_id (str): The ID of the message to fetch.

        Returns:
            email.message.Message: The fetched message.
        """
        status, message = self.send_and_fetch(f'FETCH {message_id} (RFC822)', message_id=message_id)

        return status, message
        # status, message = self.server.fetch(message_id, '(RFC822)')
        # return email.message_from_bytes(message[1])

    def done(self):
        """
        Disables IDLE mode.

        Raises:
            imaplib.IMAP4_SSL.error: If IDLE mode cannot be disabled.
        """
        # response = self.send(b'DONE')
        self.server.send(b'DONE\r\n')
        response = self.server.readline().decode()
        print(f"DONE response: {response}")
        # if response.startswith(b'+ idling'):
        #     print('IDLE mode done.')
        # else:
        #     print('Failed to disable IDLE mode.')

    def logout(self):
        """
        Logs out of the IMAP server.

        Raises:
            imaplib.IMAP4_SSL.error: If the logout fails.
        """
        # self.server.logout()
        status, _ = self.send_and_check(f"LOGOUT")

        if status == Status.OK:
            print(f"Logged out successfully")
            return True
        else:
            print(f"Unable to logout")
            return False

    def close(self):
        """
        Closes the connection to the IMAP server.
        """
        # self.server.close()
        status, _ = self.send_and_check(f"CLOSE")

        if status == Status.OK:
            print(f"Closed connection successfully")
            return True
        else:
            print(f"Unable to close connection")
            return False
