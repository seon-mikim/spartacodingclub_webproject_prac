from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://gogotest:spa0727rtan@cluster0.xukpzid.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

import requests
from bs4 import BeautifulSoup

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/all')
def all():
   return render_template('all.html')

@app.route('/Gangneung')
def gangneung():
   return render_template('Gangneung.html')

@app.route('/Sokcho')
def Sokcho():
   return render_template('Sokcho.html')

@app.route('/Yangyang')
def Yangyang():
   return render_template('Yangyang.html')

@app.route('/Donghae')
def Donghae():
   return render_template('Donghae.html')



@app.route("/food", methods=["POST"])
def food_post():
    url_receive = request.form['url_give']
    star_receive = request.form['star_give']
    comment_receive = request.form['comment_give']
    area_receive = request.form['area_give']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url_receive, headers=headers)

    soup = BeautifulSoup(data.content, 'html.parser')

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

@app.route("/gangwonfood", methods=["GET"])
def gangwon_get():
    foods_list = list(db.foods.find({},{'_id':False}))
    return jsonify({'movies':foods_list})



@app.route("/Gangneungfood", methods=["GET"])
def Gangneung_get():
    foods_list = list(db.foods.find({'area':'강릉'}, {'_id': False}))
    return jsonify({'movies': foods_list})

@app.route("/Donghaefood", methods=["GET"])
def Donghae_get():
    foods_list = list(db.foods.find({'area':'동해'}, {'_id': False}))
    return jsonify({'movies': foods_list})

@app.route("/Sokchofood", methods=["GET"])
def Sokcho_get():
    foods_list = list(db.foods.find({'area':'속초'}, {'_id': False}))
    return jsonify({'movies': foods_list})

@app.route("/Yangyangfood", methods=["GET"])
def Yangyang_get():
    foods_list = list(db.foods.find({'area':'양양'}, {'_id': False}))
    return jsonify({'movies': foods_list})


if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)
