# Custom Crypto Example Application

This is an application demonstrating the use of custom cryptography to obfuscate requests and responses and frustrate attackers. It is intended to demonstrate the use of [my custom crypto Burp Extension](https://github.com/MWR-CyberSec/custom-crypto-burp-extension).

# Setup

Install `pipenv` through either your package manager (for Kali, Debian or Ubuntu this will be `sudo apt install pipenv`) or via pip (`pip install --user pipenv` and then add it to your PATH).

Then navigate to the project directory, and run `pipenv install`
```
pip3 install -r requirements.txt
python -m flask run
```

Access the web application at http://127.0.0.1:5000/ (default)