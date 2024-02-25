import bcrypt
import json


def storeUserPW(user, pw, email):

  with open("auth.json", "r") as data:
    authDict = json.load(data)
    authORG = authDict
    print(authORG)
  try:
    password = pw.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password, salt)
    authDict[user] = {
      "password": hashed_password.decode('utf-8'),
      "email": email
    }

    with open("auth.json", "w") as f:
      json.dump(authDict, f)

  except:
    with open("auth.json", "w") as f:
      json.dump(authORG, f)


def verify(user, pw):

  with open("auth.json", "r") as data:
    authDict = json.load(data)

  password = pw.encode("utf-8")
  try:
    check = bcrypt.checkpw(password,
                           authDict[user]["password"].encode("utf-8"))
    return check
  except:
    return False
