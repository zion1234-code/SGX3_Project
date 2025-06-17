from flask import Flask


app = Flask(__name__)

#More line of code
#More Line of code

@app.route('/', methods=['GET'])
def hello_world():
    return "Hello World!\n"
@app.route('/<name>',methods=['GET'])
def hello_name(name):
    return f'Hello,{name}\n'
#the last line of you flask application
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8046)


