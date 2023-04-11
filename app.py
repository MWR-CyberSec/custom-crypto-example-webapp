from flask import Flask, render_template, request
import pyaes
import rsa
from base64 import b64encode, b64decode
import logging
from urllib.parse import parse_qs, quote
import sys

rot13trans = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 
   'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')
with open("public.pem", "r") as keyfile:
	pubKey = rsa.PublicKey.load_pkcs1_openssl_pem(keyfile.read())

def rot13(input):
	return input.translate(rot13trans)

def aes_decrypt(key, input):
	decrypter = pyaes.Decrypter(pyaes.AESModeOfOperationCBC(key, "0000000000000000"))
	decrypted = decrypter.feed(input)
	decrypted += decrypter.feed()
	return decrypted

def aes_encrypt(key, input):
	encrypter = pyaes.Encrypter(pyaes.AESModeOfOperationCBC(key, "0000000000000000"))
	ciphertext = encrypter.feed(input)
	ciphertext += encrypter.feed()
	return ciphertext


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
app = Flask(__name__)

@app.before_request
def log_request_info():
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Body: %s', request.get_data())

@app.route("/")
def index():
	return render_template('index.html')

@app.route("/congratulations")
def congrats():
	return render_template('congrats.html')

@app.route("/login", methods=['POST'])
def login():
	data = b64decode(request.form["data"])
	# Mistake 1: ROT13 is not an encryption scheme, and should not be used as such
	# Mistake 2: Don't include secret or private keys in requests (or anywhere the client can see them)
	# 	Either use RSA encryption so that the client doesn't have access to the private key,
	# or better yet use a key exchange algorithm such as Diffe-Helman Key Exchange
	aeskey = b64decode(rot13(request.form["mac"]))
	sign = b64decode(request.form["sign"])

	# Mistake 3: AES-CBC is an unauthenticated cipher, and thus can be tampered with
		# For this reason, the authenticated GCM, CTR or CFB block modes are recommended instead
		# If this is not possible, an encrypt-then-MAC or encrypt-then-sign approach should be taken
		# 	using HMAC or RSA
	# Mistake 4: a cryptograhpically random Initialisation Vector (IV) should be used for each encryption (each request)
		# This IV can be attached to the request, as it is not secret
	decrypted = aes_decrypt(aeskey,data)
	app.logger.debug(str(decrypted))
	# Mistake 5: the plaintext is used for verification, rather than the ciphertext, making the decryption unauthenticated
		# in Mistake 3, we discuss encrypt-then-sign - this is not the approach used below
	if (not rsa.verify(decrypted, sign, pubKey)):
		return "result=" + quote(b64encode(aes_encrypt(aeskey, "Payload verification failed!"))), 400
	values = parse_qs(str(decrypted, 'utf-8'))
	app.logger.debug(values)
	if (values["username"][0] != "MWR"):
		return "result=" + quote(b64encode(aes_encrypt(aeskey, "Username is not `MWR`"))), 403
	if (values["password"][0] != "supersecretpassword"):
		return "result=" + quote(b64encode(aes_encrypt(aeskey, "Password is not `supersecretpassword`"))), 403
	
	return "result=" + quote(b64encode(aes_encrypt(aeskey, "Congratulations, you cracked the code!")))

	
	
