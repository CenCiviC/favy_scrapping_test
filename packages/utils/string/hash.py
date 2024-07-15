import hashlib

def generate_etag(response_body: str):
    return hashlib.sha256(response_body.encode('utf-8')).hexdigest()

def encode_to_base62(input_str: str) -> str:
    def encode_base62(num):
        characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        if num == 0:
            return characters[0]
        base62 = []
        while num:
            num, remainder = divmod(num, 62)
            base62.append(characters[remainder])
        return ''.join(reversed(base62))
    
    
    bytes_data = input_str.encode()
    num = int.from_bytes(bytes_data, 'big')
    return encode_base62(num)

def decode_from_base62(base62_str: str) -> str:
    def decode_base62(base62_str):
        characters = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        value = 0
        for char in base62_str:
            value = value * 62 + characters.index(char)
        return value
    num = decode_base62(base62_str)

    num_bytes = num.to_bytes((num.bit_length() + 7) // 8, 'big')
    return num_bytes.decode()