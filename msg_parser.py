"""MSG file parsing utilities.

This module contains a helper to extract metadata from Outlook
``.msg`` files. Importing ``win32com.client`` at module import time
would cause the application to crash on systems where the COM
library is unavailable (e.g., macOS/Linux). To avoid that, the
module imports ``win32com.client`` lazily within the parsing
function and gracefully handles ImportError.
"""

import os

def parse_msg(filepath: str) -> dict:
    """Parse a .msg file and extract key email metadata.

    The function attempts to open the message using the Outlook
    COM interface via ``win32com.client``. If Outlook is not
    available or the file cannot be parsed, a dictionary with
    ``error`` set to ``True`` and explanatory messages is returned.

    Parameters
    ----------
    filepath: str
        Absolute or relative path to the .msg file on disk.

    Returns
    -------
    dict
        A mapping containing ``sender``, ``email`` (recipients),
        ``subject``, ``received_time``, ``sent_time``, ``body``,
        and an ``error`` flag indicating whether parsing succeeded.
    """
    # Import inside function to avoid ImportError at module import
    try:
        import win32com.client  # type: ignore
    except Exception as e:
        # Return informative error when Outlook/COM is unavailable
        return {
            "sender": "Error: Outlook not available",
            "email": "",
            "subject": f"Could not parse: {os.path.basename(filepath)}",
            "received_time": "",
            "sent_time": "",
            "body": (
                f"Error: {str(e)}\n\n"
                "Make sure Microsoft Outlook is installed and configured."
            ),
            "error": True,
        }

    try:
        # Initialize Outlook
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    except Exception as e:
        return {
            "sender": "Error: Outlook not available",
            "email": "",
            "subject": f"Could not parse: {os.path.basename(filepath)}",
            "received_time": "",
            "sent_time": "",
            "body": (
                f"Error: {str(e)}\n\n"
                "Make sure Microsoft Outlook is installed and configured."
            ),
            "error": True,
        }

    try:
        msg = outlook.OpenSharedItem(os.path.abspath(filepath))
        data = {
            "sender": getattr(msg, "SenderName", ""),
            "email": getattr(msg, "To", ""),
            "subject": getattr(msg, "Subject", ""),
            "received_time": msg.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S")
            if getattr(msg, "ReceivedTime", None)
            else "",
            "sent_time": msg.SentOn.strftime("%Y-%m-%d %H:%M:%S")
            if getattr(msg, "SentOn", None)
            else "",
            "body": getattr(msg, "Body", ""),
            "error": False,
        }
        return data
    except Exception as e:
        return {
            "sender": "Error parsing file",
            "email": "",
            "subject": f"Could not parse: {os.path.basename(filepath)}",
            "received_time": "",
            "sent_time": "",
            "body": f"Error: {str(e)}",
            "error": True,
        }

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