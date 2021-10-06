import datetime, sys, os, getopt
from dotenv import load_dotenv

from mail import Account, MailContent, send
from encryption import decrypt


# Globals
chores = ['Garbage', 'Dishwasher', 'Bathroom']
offset = 0

def main(argv):
  # Date and Rotation
  date = datetime.datetime(2021, 10, 3)
  today = datetime.datetime.now()
  week_start = today - datetime.timedelta(days=today.weekday() + 1)
  delta_days = (week_start - date).days
  rotation = (delta_days // 7) % 4 + offset

  message=''
  force = False
  if (len(argv) > 0):
    opts, args = getopt.getopt(argv,'ifm:',['message=']) # parse command line arguments
    for opt, arg in opts:
      if opt == '-i':
        week_start_str = week_start.strftime('%A, %B %-d')
        print('-- Script Info --\n')
        print(f'Week Start: {week_start_str}')
        print(f'Rotation: {rotation}\n')
        sys.exit(0)
      elif opt in ('-m', '--message'):
        message += arg
      elif (opt == '-f'):
        force = True


  with open('rotation.txt', 'r+') as old:
    if (rotation == int(old.read()) and not force): # check if the email has been sent already
      print('Not running (duplicate)')
      sys.exit(0)
    else:
      old.seek(0)
      old.write(f'{rotation}  ')
    old.close()

  names = []
  recipient_emails = []
  with open('recipient_info.txt', 'r') as recipient_info:
    tokens = recipient_info.read().replace('\n', ',').split(',')
    for item in tokens:
      if tokens.index(item) % 2 == 0:
        names.append(item.strip())
      else:
        recipient_emails.append(item.strip())
  
  # Subject and Body
  email_subject = week_start.strftime('%A, %B %-d - Keats Chores')

  email_body = f'''
  <b>{names[0]:\u00A0<7}</b> - {chores[rotation]}
  <b>{names[1]:\u00A0<8}</b> - {chores[rotation + 1]}
  <b>{names[2]:\u00A0<7}</b> - {chores[rotation + 2]}

  {message}
  '''
  email_body = email_body.replace('\n', '<br/>')

  # Mail Function Objects
  load_dotenv('.env')
  password = decrypt(os.getenv('PASSWORD'))

  sender_info : Account = {
    'name': 'Bryn',
    'user': 'bryn.automail@gmail.com',
    'password': password
  }
  email_content : MailContent = {
    'subject': email_subject,
    'body': email_body
  }

  send(sender_info, recipient_emails, email_content)


def print_message(subject : str, body : str):
  print('--- YOUR MESSAGE ---\n' + subject + '\n' + body)


if __name__ == '__main__':
  main(sys.argv[1:])