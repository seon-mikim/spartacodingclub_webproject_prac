from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('mongodb+srv://gogotest:spa0727rtan@cluster0.xukpzid.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta_plus_signup


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
        return render_template('category.html')

    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,
        "password": password_hash,
        "profile_name": username_receive,
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/category')
def all():
   return render_template('category.html')

@app.route('/Gangneung.html')
def gangneung():
   return render_template('Gangneung.html')

@app.route('/Sokcho.html')
def Sokcho():
   return render_template('Sokcho.html')

@app.route('/Yangyang.html')
def Yangyang():
   return render_template('Yangyang.html')

@app.route('/Donghae.html')
def Donghae():
   return render_template('Donghae.html')



@app.route("/place", methods=["POST"])
def place_post():
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    area_receive = request.form['area_give']

    chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1928x1090')
    options.add_argument('disable-gpu')

    try:
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', chrome_options=options)
    except:
        chromedriver_autoinstaller.install(True)
        driver = webdriver.Chrome(f'./{chrome_ver}/chromedriver.exe', chrome_options=options)

    driver.get(url_receive)
    WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "entryIframe")))

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    title = soup.select_one('meta[property="og:title"]')['content'].split(":")
    image = soup.select_one('meta[property="og:image"]')['content']
    desc = soup.select_one(
        '#app-root > div > div > div > div:nth-child(6) > div > div.place_section.no_margin._18vYz > div > ul > li._1M_Iz._1aj6- > div > a > span._2yqUQ').text

    doc = {
        'title': title[0],
        'image': image,
        'desc': desc,
        'star': star_receive,
        'comment': comment_receive,
        'area': area_receive
    }
    db.foods.insert_one(doc)

    return jsonify({'msg':'맛집 등록 완료!'})

@app.route("/Gangwonfood", methods=["GET"])
def gangwon_get():
    foods_list = list(db.foods.find({},{'_id':False}))
    return jsonify({'place':foods_list})

@app.route("/Gangneungfood", methods=["GET"])
def Gangneung_get():
    foods_list = list(db.foods.find({'area':'강릉'}, {'_id': False}))
    return jsonify({'place': foods_list})

@app.route("/Donghaefood", methods=["GET"])
def Donghae_get():
    foods_list = list(db.foods.find({'area':'동해'}, {'_id': False}))
    return jsonify({'place': foods_list})

@app.route("/Sokchofood", methods=["GET"])
def Sokcho_get():
    foods_list = list(db.foods.find({'area':'속초'}, {'_id': False}))
    return jsonify({'place': foods_list})

@app.route("/Yangyangfood", methods=["GET"])
def Yangyang_get():
    foods_list = list(db.foods.find({'area':'양양'}, {'_id': False}))
    return jsonify({'place': foods_list})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
