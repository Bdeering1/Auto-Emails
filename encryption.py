# Vigenere cipher with Myszkowski transposition
import sys, getopt, math
from sympy import nextprime
from secrets import randbelow
from typing import List

def main(argv):
  verbose = False
  if (len(argv) > 0):
    opts, args = getopt.getopt(argv,'ve:d:t:',['string=','encstring=', 'string='])
    for opt, arg in opts:
      if opt == '-v':
        verbose = True
      if opt in ('-e', '--string'):
        encrypt(arg)
      elif opt in ('-d', '--encstring'):
        decrypt(arg, verbose)
      elif opt in ('-t', '--string'):
        decrypt(encrypt(arg), verbose)


# ENCRYPTION / DECRYPTION FUNCTIONS
def encrypt(input : str) -> str:
  output = r''
  output_len = (len(input) // 32 + 1) * 64
  keys = []
  charset = create_charset()

  preimage = randbelow(len(charset))
  bin_hash = dist_hash(preimage)

  # creating key array
  num_keys = nextprime(output_len // 16)
  for _ in range(num_keys):
    key_val = randbelow(len(charset))
    keys.append(key_val)
  
  detranspose(transpose(input, keys[1]), keys[1])

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

  for _ in range(output_len // 4 - len(output)): # key padding
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

  for _ in range(output_len - len(output)): # message padding
    output += random_char(charset)

  print(output)
  return output

def decrypt(input : str, verbose : bool = False):
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

  if (verbose):
    print('\n-- HASH PREIMAGE --')
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
    print()

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
  return charset[randbelow(len(charset))]


# TRANSPOSITION FUNCTIONS
def transpose(input : str, preimage : int):
  base = 5
  transpose_hash = transposition_hash(preimage, base)

  num_cols = len(transpose_hash)
  col_arr = [''] * num_cols
  for idx, char in enumerate(input):
    col_arr[idx % num_cols] += char

  output = ''
  for i in range(base):
    cols = []
    for idx, col_str in enumerate(col_arr):
      if i == transpose_hash[idx]:
        cols.append(col_str)
    if len(cols) == 0:
      break
    for idx in range(len(cols[0])):
      for col in cols:
        if idx < len(col): output += col[idx]

  print('\n-- TRANSPOSITION HASH --')
  print(transpose_hash)
  print('-- COLUMN ARRAY --')
  print(col_arr)
  print('-- TRANSPOSED STRING --')
  print(output)
  return output

def detranspose(input: str, preimage : int):
  base = 5
  transpose_hash = transposition_hash(preimage, base)

  num_cols = len(transpose_hash)
  col_arr = [''] * num_cols
  col_length = math.ceil(len(input) / num_cols)
  last_full_col = len(input) - (num_cols - len(input) % col_length) if len(input) % col_length != 0 else len(input) # this might be wrong
  print(last_full_col)
  output = ''
  total_collisions = 0
  for hash_idx in range(base):
    cols = []
    possible_collisions = 0
    for idx in range(len(col_arr)):
      if hash_idx == transpose_hash[idx]: # currently finding strings with incorrect lengths (after one is incorrect the rest become shifted)
        possible_collisions += 1
        if possible_collisions >= 2: total_collisions += 1
        new_hash_idx = hash_idx + total_collisions
        start_idx = col_length * new_hash_idx
        end_idx = col_length * (new_hash_idx+1) if col_length * (new_hash_idx+1) < last_full_col else None
        cols.append(input[start_idx:end_idx])
    print(cols)
    if len(cols) == 0:
      break
    for idx in range(len(cols[0])):
      for col in cols:
        if idx < len(col): output += col[idx]

  print(output)
  return 0

def transposition_hash(preimage : int, base : int): # returns an array [0..n] s.t. for each non-zero number a there exists b=a-1
  pre_hash = (preimage + 13) ** 2 + 7
  based_hash = int_to_base(pre_hash, base)

  check_arr = hash_check(based_hash, base)
  check_idx = 0
  hash_idx = 0
  while not(all(check == True for check in check_arr)):
    if check_arr[check_idx]:
      check_idx = check_idx + 1 if check_idx < len(check_arr)-1 else 0
    else:
      based_hash[hash_idx] = check_idx
      hash_idx = hash_idx + 1 if hash_idx < len(based_hash)-1 else 0
      check_arr = hash_check(based_hash, base)

  return based_hash

def hash_check(hash : List[int], base):
  check_arr = [False] * (base-1)
  for idx, check in enumerate(check_arr):
    for num in hash:
      if num == idx:
        check_arr[idx] = True
        break
  return check_arr

def int_to_base(n, base) -> List[int]:
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(n % base)
        n //= base

    return digits[::-1]


# DISTRIBUTION FUNCTIONS (padding char distribution)
def dist_hash(preimage : int):
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