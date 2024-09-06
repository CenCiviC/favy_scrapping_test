from flask import Flask, jsonify, request, make_response
from flask_cors import CORS

from utils.string import *
from service import *


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

##TODO: error status code 추가
# @app.errorhandler(500)
# def error_handling_500(error):
#     return jsonify({'Error': "Some Error.."}, 500)


@app.route('/')
def home():
    return jsonify({"data": 'FAVY AI api'})


########## youtube 용 api

#video id를 받아서 codies에 대한 전체 정보 출력
@app.route('/video/<string:video_id>', methods = ['GET'])
def video(video_id):
    if request.method == 'GET':
        try:
            data = service_video(video_id)
            
            return jsonify(data)
        except:
            return jsonify({'error': 'Api error occurs'})
    else:
        return jsonify({'error': 'Invalid request method'})

########## instagram 용 api 

@app.route('/ig/shot', methods= ['POST'])
def upload_instagram_shot():
    if request.method == 'POST':
        try:
            instagram_url = request.form['url']
            ig_shot_info_json = service_instagrm_shot_info(instagram_url)
            if not ig_shot_info_json:
                return jsonify({'error': "error"})
            
            return ig_shot_info_json
        except ValueError as ve:
            return jsonify({'error': ve})
            
    else:
        return jsonify({'error': 'Invalid request method'})

    
########## common api

#사이트 url을 받아서 product 기본 정보 출력
@app.route('/product', methods=['GET'])
def product_info():
    if request.method == 'GET':
        try:
            url = request.form['url']
            product_info_json = service_product_info(url)
            
            if not product_info_json:
                return jsonify({'error': 'Invalid request method'})
            return jsonify(product_info_json)
        except Exception as e:
            return jsonify({'error': 'Invalid request method'})
    else:
        return jsonify({'error': 'Invalid request method'})

#상품의 image url, 이름을 받아서 관련 상품 기본 정보 출력
@app.route('/related_product', methods=['GET'])
def related_product():
    if request.method == 'GET':
        try:
            imageUrl = request.form['url']
            productName = request.form['name']
            data = service_related_product_info(imageUrl, productName)

            return jsonify(data)
        except:
            return jsonify({'error': 'Api error occurs'})
    else:
        return jsonify({'error': 'Invalid request method'})

#상품의 판매처 api,
@app.route('/sales', methods=['GET'])
def sales():
    if request.method == 'GET':
        try:
            imageUrl = request.form['url']
            data = service_sales(imageUrl)

            return jsonify(data)
        except:
            return jsonify({'error': 'Api error occurs'})
    else:
        return jsonify({'error': 'Invalid request method'})
    
if __name__ == '__main__':
    app.run(debug=True)