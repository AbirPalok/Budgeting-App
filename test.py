import re
from database_connection import *

#
# import smtplib, ssl
#
#
# # Recommended Port For SSL
# port = 465
#
# # Written directly here for testing
# password = "Budgetapp@123"
#
# # Creating a secure SSL context
# context = ssl.create_default_context()
#
#
# with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
#     sender_email = "budgetapp.paul@gmail.com"
#     receiver_email = "nuranysheikh.stan@gmail.com"
#     message = """SUBJECT: Tumi Faltu \nFROM: Budget App
#     \n\n
#     Dekho dekho. Ki shikhe Felechi.
#     - Sent from Python
#
#     """
#
#     # Login
#     server.login(sender_email, password)
#
#     server.sendmail(sender_email, receiver_email, message)


# This Works:
# import smtplib, ssl
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
#
# sender_email = "budgetapp.paul@gmail.com"
# receiver_email = "md.palok@gmail.com"
# password = "Budgetapp@123"
#
# message = MIMEMultipart("alternative")
# message["Subject"] = "HTML Test"
# message["From"] = sender_email
# message["To"] = receiver_email
#
# # Create the plain-text and HTML version of your message
# text = """\
# Ignore me
# """
#
# html = """\
# <!doctype html>
# <html lang="en">
# <body style="background-color: #c7c7c7">
#     <div style="width: 50vw; height: 90vh; background-color: #ffffff;
#     margin-left: auto; margin-right: auto; margin-top:25px">
#
#         <div style="height: 5rem; width: 100%; background-color: #0A9DFF; margin-top: 100px;
#         position: relative; top: 10%; vertical-align: middle; padding: 10px 0">
#
#             <h1 style="color: #363732; font-family: Verdana,sans-serif; text-align: center;">
#                 Budget App
#             </h1>
#         </div>
#         <div style="padding: 10px; margin: 25px;
#         font-family: 'Agency FB', sans-serif; font-size: 20px; font-weight: bold;
#                     position: relative; top: 5rem; left: 3rem">
#             <p>Hi Taharin,</p>
#             <p>Here is your transaction code: 141124000</p>
#         </div>
#
#     </div>
# </body>
# </html>
# """
#
# # Turn these into plain/html MIMEText objects
# part1 = MIMEText(text, "plain")
# part2 = MIMEText(html, "html")
#
# # Add HTML/plain-text parts to MIMEMultipart message
# # The email client will try to render the last part first
# message.attach(part1)
# message.attach(part2)
#
# # Create secure connection with server and send email
# context = ssl.create_default_context()
# with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#     server.login(sender_email, password)
#     server.sendmail(
#         sender_email, receiver_email, message.as_string()
#     )
#
# from datetime import date
# # Rought:
# print(date.today())

import time
print("Line 1")
print("Line 2")
print("Line 3")
time.sleep((2))
print("\r\r")
print("Hello!")

time.sleep((2))




