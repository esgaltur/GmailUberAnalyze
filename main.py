import base64
import os.path
import pickle
from datetime import datetime

import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
from consts import *


def main():
    plot_data = {}
    messages_list = []
    messages_list = get_messages_list_from_gmail_or_local_load(messages_list)
    decoded_messages_list = []
    for message in messages_list:
        if message[PAYLOAD][PARTS][PART_0][MIME_TYPE] == "text/html":
            decoded_messages_list.append(
                base64.urlsafe_b64decode(message[PAYLOAD][PARTS][PART_0][BODY][DATA].encode('UTF-8')))
    first_type = []
    second_type = []
    for message in decoded_messages_list:
        clean_text_html = BeautifulSoup(message, "html.parser")
        for s in clean_text_html(['script', 'style']):
            s.decompose()
        clean_text = clean_text_html.text.replace("\n", "").replace(", Dmtriy", "").replace("Uber", "")
        if clean_text != "":
            if len(clean_text.split("|")) == 3:
                second_type.append(clean_text.split("|")[0])
            else:
                first_type.append(clean_text)

    for message in first_type:
        words_list = list(filter(None, message.split(" ")))
        ride_date = datetime.strptime(words_list[4] +
                                      " " +
                                      words_list[5] +
                                      " " +
                                      words_list[6],
                                      FIRST_DATE_FORMAT)
        if "₽" in words_list[0]:
            continue
        ride_price = int(float(words_list[0].replace(CZK, "").replace(KC, "")))
        plot_data[ride_date] = ride_price
    for message in second_type:
        words_list = list(filter(None, message.split(" ")))
        if ("₽" in words_list[1]):
            continue
        ride_price = int(float(words_list[1].replace(CZK, "").replace(KC, "")))
        ride_date = datetime.strptime(words_list[2] +
                                      words_list[3] +
                                      " " +
                                      words_list[4] +
                                      words_list[5],
                                      SECOND_DATE_FORMAT)
        plot_data[ride_date] = ride_price
    plt.plot(*zip(*sorted(plot_data.items())))
    plt.show()


def get_messages_list_from_gmail_or_local_load(messages_list):
    if (not os.path.exists(MESSAGES_FILE_LOCAL)):
        service = prepare_gmail_api_service()
        get_uber_messages_list(messages_list, service)
        with open(MESSAGES_FILE_LOCAL, WB) as file:
            pickle.dump(messages_list, file)
    else:
        with open(MESSAGES_FILE_LOCAL, RB) as file:
            messages_list = pickle.load(file)
    return messages_list


def prepare_gmail_api_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE_LOCAL):
        with open(TOKEN_FILE_LOCAL, RB) as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE_LOCAL, WB) as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service


def get_uber_messages_list(messages_list, service):
    response = service.users().messages().list(userId='me', q=LABEL_UBER).execute()
    while NEXT_PAGE_TOKEN in response:
        page_token = response[NEXT_PAGE_TOKEN]
        messages = response.get('messages', [])
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            messages_list.append(msg)
        response = service.users().messages().list(userId='me',
                                                   q=LABEL_UBER,
                                                   pageToken=page_token).execute()


if __name__ == '__main__':
    main()
