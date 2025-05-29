from flask import Flask

app = Flask(__name__)
@app.route('/')
def hello():
    return 'Ola, mundo!'

app.run(debug=True)