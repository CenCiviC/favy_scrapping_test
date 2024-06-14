import sys
import os
import hashlib
import hmac
import base64
import requests
import time

def	make_signature():
	timestamp = int(time.time() * 1000)
	timestamp = str(timestamp)

	access_key = "NwLmYT7zI5tUZDP6wfu9"				# access key id (from portal or Sub Account)
	secret_key = "mycVZQ6BoYyzIHFvp2lAMzneDxbNLEd0iLDqAsuh"				# secret key (from portal or Sub Account)
	secret_key = bytes(secret_key, 'UTF-8')

	method = "POST"
	uri = "/alimtalk/v2/services/ncp:kkobizmsg:kr:3343526:favy-sms-test/messages"

	message = method + " " + uri + "\n" + timestamp + "\n" + access_key
	message = bytes(message, 'UTF-8')
	signingKey = base64.b64encode(hmac.new(secret_key, message, digestmod=hashlib.sha256).digest())
	return signingKey


from datetime import datetime

# 현재 UTC 시간을 가져옵니다
current_time = datetime.utcnow()

# 1970년 1월 1일 00:00:00 UTC를 기준으로 경과 시간을 계산합니다
epoch = datetime(1970, 1, 1)

# 경과 시간을 밀리초 단위로 계산합니다
elapsed_time_ms = int((current_time - epoch).total_seconds() * 1000)



print(make_signature())
print(elapsed_time_ms)
