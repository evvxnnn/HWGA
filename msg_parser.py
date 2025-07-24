import win32com.client
import os

def parse_msg(filepath):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    msg = outlook.OpenSharedItem(os.path.abspath(filepath))

    data = {
        "sender": msg.SenderName,
        "email": msg.To,
        "subject": msg.Subject,
        "received_time": msg.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S") if msg.ReceivedTime else "",
        "sent_time": msg.SentOn.strftime("%Y-%m-%d %H:%M:%S") if msg.SentOn else "",
        "body": msg.Body,
    }

    return data
