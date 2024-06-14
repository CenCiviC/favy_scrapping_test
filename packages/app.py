from flask import Flask, jsonify, request
from controller.controller import *
from flask_cors import CORS
from api.googleapi import search_related_product
from utils.string import *
from utils.variables import CLOTHES_COLOR
from utils.files import download_image_by_url


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({"data": 'FAVY AI api'})

#video id를 받아서 codies에 대한 전체 정보 출력
@app.route('/video/<string:video_id>', methods = ['GET'])
def video(video_id):
    if request.method == 'GET':
        try:
            data = controller_video(video_id)
            
            return jsonify(data)
        except:
            return jsonify({'error': 'Api error occurs'})
    else:
        return jsonify({'error': 'Invalid request method'})

#사이트 url을 받아서 product 기본 정보 출력
@app.route('/product', methods=['POST'])
def product():
    if request.method == 'POST':
        try:
            # params = request.get_json()
            # url = params.get('url')
            
            url = request.form["url"]
            
            if url:
                product_data = controller_product(url)
            return jsonify(product_data)
        except Exception as e:
            return jsonify({'error': 'Invalid request methodㄴ'})
    else:
        return jsonify({'error': 'Invalid request method'})

#상품의 imageurl, 이름을 받아서 product category, color 정보 출력
@app.route('/product_detail', methods=['POST'])
def product_detail():
    if request.method == 'POST':
        try:
            imageUrl = request.form['url']
            productName = request.form['name']

            data = controller_product_detail(imageUrl, productName)

            return jsonify(request)
        except:
            return jsonify({'error': 'Api error occurs'})
    else:
        return jsonify({'error': 'Invalid request method'})


#상품의 image url, 이름을 받아서 관련 상품 기본 정보 출력
@app.route('/related_product', methods=['POST'])
def related_product():
    if request.method == 'POST':
        try:
            imageUrl = request.form['url']
            productName = request.form['name']
            data = controller_related_product(imageUrl, productName)

            return jsonify(data)
        except:
            return jsonify({'error': 'Api error occurs'})
    else:
        return jsonify({'error': 'Invalid request method'})


# if __name__ == '__main__':
#     app.run(debug=True)
    
    
# url = "https://cafe24.poxo.com/ec01/catstreet0/3Edgez7aTEs2uDezllWuL0t85ZTakqes04USFRrl0i0QiyLFOYNQb1oPVGpGMwdQWIHLY/RkkXyi9ncDzjE1OA==/_/web/product/2024/s/20240403155020_sh.jpg"
# search_related_product(url)

urls = "https://www.musinsa.com/app/goods/3968472"
product_data = controller_product(urls)