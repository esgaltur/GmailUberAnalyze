import os.path
import pickle
from datetime import datetime

import matplotlib.pyplot as plt
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
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
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    response = service.users().messages().list(userId='me', q="label:uber").execute()
    x = []
    y = []
    while "nextPageToken" in response:
        page_token = response['nextPageToken']

        messages = response.get('messages', [])
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            if (":" in msg["snippet"]):
                res = msg["snippet"].split(":")[1].split(" ")
                try:
                    dt = res[2] + " " + res[3] + " " + res[4] + " " + res[5]
                    str1 = datetime.strptime(dt, "%a, %b %d, %Y")
                    x.append(int(float(res[1].replace("Kč", "").replace("₽", ""))))
                    y.append(str1)
                    print(res[1] + " " + str(str1))
                except Exception as e:

                    print(msg["snippet"].split(":")[0].split(" "))
                    print(e)
            else:
                try:
                    res = msg["snippet"].split(" ")
                    if ("₽" in res[0]):
                        continue
                    dt = res[6] + " " + res[7] + " " + res[8]
                    str1 = datetime.strptime(dt, "%d %B %Y")
                    x.append(int(float(res[0].replace("Kč", "").replace("₽", ""))))
                    y.append(str1)
                    print(res[0] + " " + str(str1))
                except:
                    res = msg["snippet"].split(" ")
                    dt = res[6] + " " + res[7] + " " + res[8]
                    str1 = datetime.strptime(dt, "%d %B %Y")
                    x.append(int(float(res[0].replace("CZK", "").replace("₽", ""))))
                    y.append(str1)

        response = service.users().messages().list(userId='me',
                                                   q="label:uber",
                                                   pageToken=page_token) \
            .execute()
    plt.plot(y, x)
    plt.show()


if __name__ == '__main__':
    main()
