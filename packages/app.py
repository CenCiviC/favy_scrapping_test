from flask import Flask, jsonify, request, make_response
from controller.controller import *
from flask_cors import CORS



from api.googleapi import search_related_product
from utils.string import *
from utils.variables import CLOTHES_COLOR
from utils.files import convert_image_to_webp
from api.youtubeapi import get_youtube_video_info
from api.aws import save_file_to_s3


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

##TODO: error status code 추가
# @app.errorhandler(500)
# def error_handling_500(error):
#     return jsonify({'Error': "Some Error.."}, 500)


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
            params = request.get_json()
            url = params.get('url')
            
            #url = request.form["url"]
            
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


@app.route('/example', methods=['GET'])
def get_example():
    #response = data(json) or error + response data(status, kind) + etag
    
    #data json으로부터 받고
    example_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com"
    }
    
    
    #status, kind, received etag받아서
    #initial -> etag ->  etag로 확인->final response body만들기(진짜 or error body도)
    initial_response_body = jsonify({
        "status": "success",
        "kind" : "test",
        "data": example_data
    }).get_data(as_text=True)
    
    
    etag = generate_etag(initial_response_body)
    
    final_response_body = jsonify({
        "status": "success",
        "etag": etag,
        "data": example_data
    }).get_data(as_text=True)
    
    if request.headers.get('If-None-Match') == etag:
        return '', 304
    
    
    #header 추가 해서 response 만들기
    response = make_response(final_response_body, 200)
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['ETag'] = etag
    response.headers['Cache-Control'] = 'no-cache'
    
    return response


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400


    file_name = "test"
    file_name_with_extension = "test.webp"
    convert_image_to_webp(file, file_name)
    save_file_to_s3(file_name_with_extension, f"product/{file_name_with_extension}", isImage=True)
    # if s3_url:
    #     return jsonify({"url": s3_url}), 200
    # else:
    #     return jsonify({"error": "Failed to upload to S3"}), 500
    
    return jsonify({"url": "test"}), 200

if __name__ == '__main__':
    app.run(debug=True)
    
    
# url = "https://cafe24.poxo.com/ec01/catstreet0/3Edgez7aTEs2uDezllWuL0t85ZTakqes04USFRrl0i0QiyLFOYNQb1oPVGpGMwdQWIHLY/RkkXyi9ncDzjE1OA==/_/web/product/2024/s/20240403155020_sh.jpg"
# search_related_product(url)

# urls = "https://www.shopcider.com/product/detail?pid=1033633&style_id=137477&utm_campaign=CD20230303262556TT&utm_source=product-share&utm_medium=share"
# product_data = controller_product(urls)

videoid = "isTo5kISXMg"
get_youtube_video_info(videoid)