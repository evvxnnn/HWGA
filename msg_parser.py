import win32com.client
import os
import pythoncom

def parse_msg(filepath):
    try:
        # Try to initialize Outlook
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    except Exception as e:
        # Return a dictionary with error information
        return {
            "sender": "Error: Outlook not available",
            "email": "",
            "subject": f"Could not parse: {os.path.basename(filepath)}",
            "received_time": "",
            "sent_time": "",
            "body": f"Error: {str(e)}\n\nMake sure Microsoft Outlook is installed and configured.",
            "error": True
        }
    
    try:
        msg = outlook.OpenSharedItem(os.path.abspath(filepath))

        data = {
            "sender": msg.SenderName,
            "email": msg.To,
            "subject": msg.Subject,
            "received_time": msg.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S") if msg.ReceivedTime else "",
            "sent_time": msg.SentOn.strftime("%Y-%m-%d %H:%M:%S") if msg.SentOn else "",
            "body": msg.Body,
            "error": False
        }

        return data
    except Exception as e:
        # Return error info if file couldn't be parsed
        return {
            "sender": "Error parsing file",
            "email": "",
            "subject": f"Could not parse: {os.path.basename(filepath)}",
            "received_time": "",
            "sent_time": "",
            "body": f"Error: {str(e)}",
            "error": True
        }