import smtplib
from email.mime.text import MIMEText
from typing import TypedDict, List

class Account(TypedDict):
  name: str
  user: str
  password: str

class MailContent(TypedDict):
  subject: str
  body: str

def send(account: Account, recipients : List[str], content: MailContent):
  msg = MIMEText(content['body'], 'html')
  msg['Subject'] = content['subject']
  msg['From'] = account['name']
  msg['To'] = ','.join(recipients)

  s = smtplib.SMTP_SSL(host = 'smtp.gmail.com', port = 465)
  s.login(user = account['user'], password = account['password'])
  s.sendmail(account['name'], recipients, msg.as_string())
  s.quit()