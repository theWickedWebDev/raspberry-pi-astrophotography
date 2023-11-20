from flask import Flask, render_template, request, send_file

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/latest')
def get_image():
    return send_file('/home/pi/astrophotography/image-server/public/latest.jpg', mimetype='image/jpeg')