from flask import Flask, request, Blueprint, send_from_directory, render_template
import sendutil
import os
import authutil
from flask_cors import CORS, cross_origin
import json

app = Flask(__name__)
#푸쉬 테스트
CORS(app)


@app.route('/auth', methods=['POST'])
def auth():
  res = authutil.verify(request.form["username"], request.form["password"])
  if res:
    return 'AUTH_ACCEPT'
  else:
    return 'AUTH_DECLINE'


@app.route('/')
def home():
  f = open('apps.json', 'r')
  apps = json.loads(f.read())
  last_four_apps = apps[-4:]

  apps_sorted = sorted(apps, key=lambda x: x['rating'], reverse=True)

  top_four_apps = apps_sorted[:4]
  return render_template('index.html', apps=last_four_apps, recommend=top_four_apps)


@app.route('/rate', methods=['POST'])
def rate():
  score = request.headers['rating']
  code = request.headers['code']
  f = open(f'./DB/AppDB/{code}/ratings.txt', 'a')
  f.write(f'{score}\n')
  f.close()
  f = open(f'./DB/AppDB/{code}/ratings.txt', 'r')
  lines = f.readlines()
  ratings = []
  for line in lines:
    line = line.strip()
    line = float(line)
    ratings.append(line)
  sum = 0
  for i in range(0, len(ratings)):
    sum += ratings[i]
  total = sum / len(ratings)
  with open('apps.json', 'r') as f:
    data = json.load(f)
  realtotal = round(total, 1)
  # 특정 값을 가지는 키의 값을 수정하기
  for item in data:
    if item['code'] == code:
      item['rating'] = realtotal

  # JSON파일로 다시 저장하기
  with open('apps.json', 'w') as f:
    json.dump(data, f, indent=4)
  return 'SUCCESS'


@app.route('/description/<string:code>')
def description(code):
  with open('apps.json', 'r') as file:
    apps = json.load(file)
  search_code = code
  app_name = None
  for app in apps:
    if app.get('code') == search_code:
      app_name = app.get('name')
      logo_path = app.get('logo')
      rating = app.get('rating')
      descript = app.get('description')
      reimage = app.get('representname')
      #매우 비효율적인 코딩(천재 강지오/박사랑씨께서 수정할 예정) 

      # 한승우가 코딩한거 박제!
      # 근데, 이 방식으로 프론트엔드쪽에서 별 표시하는건 ㄹㅇ 천재인듯 ^^

      # if rating == 1:
      #   webrating = 20
      # elif rating == 1.5:
      #   webrating = 31
      # elif rating == 2:
      #   webrating = 40
      # elif rating == 2.5:
      #   webrating = 51
      # elif rating == 3:
      #   webrating = 60
      # elif rating == 3.5:
      #   webrating = 71
      # elif rating == 4:
      #   webrating = 80
      # elif rating == 4.5:
      #   webrating = 91
      # elif rating == 5:
      #   webrating = 100

      webrating = rating * 20 + (rating * 2 % 2)  # - 박사랑

      return render_template('description.html',
                             appname=app_name,
                             logo=logo_path,
                             appcode=code,
                             rating=webrating,
                             image=reimage,
                             explain=descript)


@app.route('/account')
def account():
  return render_template('account.html')


@app.route('/apply', methods=['GET', 'POST'])
def apply():
  if request.method == 'POST':
    appname = request.form["name"]
    company = request.form["company"]
    description = request.form["description"]
    repim = request.form["repim"]

    file = request.files["appfile"]
    code = sendutil.genCode()
    os.makedirs(f'VMDrive/{code}/')
    file.save(f'VMDrive/{code}/{file.filename}')

    banner = request.files["bannerimage"]
    banner.save(f'static/banner/{banner.filename}')

    logo = request.files["icon"]
    logo.save(f'static/logo/{logo.filename}')

    reimage = request.files["represent"]
    reimage.save(f'static/represent/{reimage.filename}')

    with open('apps.json', 'r') as file:
      apps = json.load(file)
    apps_original = apps
    try:
      apps.append({
        "name": appname,
        "company": company,
        "image": f"banner/{banner.filename}",
        "logo": f"{logo.filename}",
        "rating": 0,
        "code": code,
        "description": description,
        "representname": repim
      })
      # write back to apps.json
      with open('apps.json', 'w') as file:
        json.dump(apps, file, indent=4)

      return render_template(
        'purethanks.html',
        message="App Uploading Success!",
      )
    except:
      return render_template("message.html",
                             message="Failed! Please try again.")

  else:
    return render_template('apply.html')


@app.route('/apps/<string:category>', methods=['GET'])
def apps(category):
  category_list = ['tools', 'music', 'games', 'health', 'education', 'finance', 'graphic', 'weather', 'news', 'books', 'business', 'shopping', 'social', 'sports', 'travel']
  if category in category_list:
    f = open('apps.json', 'r')
    apps = json.loads(f.read())
    apps = [item for item in apps if item['category'] == category]
    return render_template('apps.html', apps=apps, category=category)


# I'll be back some time later
@app.route('/signin', methods=['GET', 'POST'])
def signin():
  if request.method == "GET":
    return render_template('login.html')
  else:
    res = authutil.verify(request.form["username"], request.form["password"])
    if res:
      return render_template('thank.html',
                             why="Sign In",
                             name1=request.form["username"],
                             name2=request.form["username"])
    else:
      return render_template('message.html',
                             message="Wrong username or password")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == "GET":
    return render_template("auth.html")
  else:
    authutil.storeUserPW(request.form["username"], request.form["password"],
                         request.form["email"])
    return render_template('thank.html',
                           why="Registration",
                           name1=request.form["username"],
                           name2=request.form["username"])


ft = Blueprint('files', __name__, url_prefix='/files')


@app.route('/ypr')
def easteregg():
  return render_template('mut.html')


@ft.route('/upload', methods=['POST'])
def upload():
  if 'file' not in request.files:
    return 'No file part in the request.'

  file = request.files['file']
  if file.filename == '':
    return 'No selected file.'

  if file:
    code = sendutil.genCode()
    os.makedirs(f'VMDrive/{code}/')
    file.save(f'VMDrive/{code}/{file.filename}')
    return code


# URL: BASE/files/serve/<code>
@ft.route('/serve/<string:code>/', methods=['GET'])
def serve(code):
  filename = os.listdir(f'VMDrive/{code}')[-1]
  return send_from_directory(f'VMDrive/{code}', filename)


@ft.route('/download', methods=['POST'])
def download():
  code = request.form["code"]
  try:
    filename = os.listdir(f'VMDrive/{code}')[-1]
  except:
    filename = os.listdir(f'VMDrive/uot')[-1]
    return send_from_directory(f'VMDrive/{code}', filename)

  return send_from_directory(f'VMDrive/{code}', filename)


@app.route('/save', methods=['POST'])
def save():
  code = sendutil.genCode()
  os.makedirs(f'VMDrive/{code}/')
  file = request.files['file']
  file.save(f'VMDrive/{code}/{file.filename}')
  return render_template('dwn.html', code=code)


@app.route('/protocread', methods=['POST'])
def adkcode_read():
  json_code = request.form["json"]
  code = sendutil.genCode()
  os.mkdir(f'VMDrive/{code}')
  with open(f'VMDrive/{code}/config.json', "w") as cfj:
    cfj.write(json_code)
  return {"code": code}


@app.route('/protocserve/<string:code>/', methods=['GET'])
def adkcode_serve(code):
  filename = os.listdir(f'VMDrive/{code}')[-1]
  with open(f"VMDrive/{code}/{filename}", "r") as f:
    js = f.read()
  return {"data": js}


@app.route('/appserve', methods=['GET'])
def appserve():
  with open('apps.json', 'r') as f:
    apps = json.loads(f.read())
  return json.dumps(apps)

@app.route('/private', methods=['GET'])
def private_ft():
  return render_template("private.html")

# This is a test.

app.register_blueprint(ft)
app.run(host='0.0.0.0', port=10000, debug=True)
