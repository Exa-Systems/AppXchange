import random
import string

letters = string.ascii_uppercase + string.digits
def genCode():
  code = ''.join(random.choice(letters) for i in range(6))
  totf = ""
  with open("used.exar", "r") as m:
    totf = m.read()
  if code in totf.split("\n"):
    return genCode()
  else:
    with open("used.exar", "a") as f:
      f.write(code + "\n")

    return code