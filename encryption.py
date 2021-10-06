# Vigenere cipher + transposition (to be added)
import sys, getopt
from sympy import nextprime
from random import randint
from typing import List

def main(argv):
  if (len(argv) > 0):
    opts, args = getopt.getopt(argv,'ve:d:t:',['string=','encstring=', 'string='])
    for opt, arg in opts:
      if opt in ('-e', '--string'):
        encrypt(arg)
      elif opt in ('-d', '--encstring'):
        decrypt(arg)
      elif opt in ('-t', '--string'):
        decrypt(encrypt(arg))


def encrypt(input : str) -> str:
  output = r''
  output_len = (len(input) // 32 + 1) * 64
  keys = []
  charset = create_charset()

  preimage = randint(0, len(charset) - 1)
  bin_hash = dist_hash(preimage)

  # creating key array
  num_keys = nextprime(output_len // 16)
  for i in range(num_keys):
    key_val = randint(0, len(charset) - 1)
    keys.append(key_val)

  # mapping keys to output using distibution hash
  output += charset[preimage]
  key_idx = 0
  for output_idx in range(output_len // 4):
    if key_idx == num_keys:
      break
    elif bin_hash[output_idx % 13] == '1':
      output += charset[keys[key_idx]]
      key_idx += 1
    else:
      output += random_char(charset)

  for i in range(output_len // 4 - len(output)): # key padding
    output += random_char(charset)

  # mapping message to output using keys and distribution hash
  length_incl = False
  input_idx = 0
  for output_idx in range(int(output_len * 3/4)):
    if input_idx == len(input):
      if not length_incl:
        partial_length = len(input) % len(charset)
        output += charset[partial_length]
      break
    elif bin_hash[output_idx % 13] == '1':
      charset_index = charset.index(input[input_idx])
      shift = keys[input_idx % num_keys]
      output += charset[(charset_index + shift) % len(charset)] # input char shifted by corresponding key value
      input_idx += 1
    elif not length_incl:
        partial_length = len(input) % len(charset)
        output += charset[(partial_length + keys[0]) % len(charset)]
        length_incl = True
    else:
      output += random_char(charset)

  for i in range(output_len - len(output)): # message padding
    output += random_char(charset)

  print(output)
  return output

def decrypt(input : str):
  charset = create_charset()
  input_len = len(input)
  key_len = input_len // 4

  raw_key = input[1:key_len]
  raw_message = input[key_len:]
  preimage = charset.index(input[0])
  bin_hash = dist_hash(preimage)

  # extracting keys from raw key string using hash distribution
  keys = []
  num_keys = nextprime(key_len//4)
  key_idx = 0
  for input_idx in range(len(raw_key)):
    if key_idx == num_keys:
      break
    elif bin_hash[input_idx % 13] == '1':
      keys.append(charset.index(raw_key[input_idx])) # appending key (from index in charset)
      key_idx += 1

  # extracting message from raw message string using key values and hash distribution
  length_read = False
  message_len = 0
  message = ''
  message_idx = 0
  for input_idx in range(len(raw_message)):
    if (length_read and message_idx == message_len) or message_idx == input_len//2: # how do we get the actual length of input here?
      break
    elif bin_hash[input_idx % 13] == '1':
      charset_index = charset.index(raw_message[input_idx])
      shift = keys[message_idx % num_keys]
      message += charset[(charset_index - shift) % len(charset)]
      message_idx += 1
    elif not length_read:
      message_len = (charset.index(raw_message[input_idx]) - keys[0]) % len(charset)
      length_read = True

  """   print('\n-- HASH PREIMAGE --')
  print(preimage)
  print('-- HASH DIST --')
  print(bin_hash)
  print('-- RAW KEY --')
  print(raw_key)
  print('-- MESSAGE LENGTH --')
  print(message_len)
  print('-- RAW MESSAGE --')
  print(raw_message)
  print('-- KEYS --')
  print(keys)
  print('-- MESSAGE --')
  print(message)
  print() """

  return message

def create_charset():
  char_ranges = [[32, 126], [161, 172], [174, 255]] #printable characters (excluding no break space, soft hyphen)
  charset = []
  for range in char_ranges:
    char = range[0]
    while char <= range[1]:
      charset.append(chr(char))
      char += 1
  return charset

def random_char(charset : List[str]):
  return charset[randint(0, len(charset) - 1)]


def dist_hash(preimage):
  pre_hash = '{0:016b}'.format((preimage + 13) ** 2 + 7)
  bin_hash = pre_hash[-13:]
  while not is_valid(bin_hash):
    bin_hash = '{0:013b}'.format(int(bin_hash, 2) << 1)[-13:]
  return bin_invert(bin_hash)

def is_valid(bin_hash):
  num_ones = 0
  for bit in bin_hash:
    if bit == '1':
      num_ones += 1
  if (num_ones > len(bin_hash) // 3):
    return False
  return True

def bin_invert(bin_str):
  return ''.join('1' if x == '0' else '0' for x in bin_str)


if __name__ == '__main__':
    main(sys.argv[1:])