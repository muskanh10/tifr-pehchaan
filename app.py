import numpy as np
from flask import Flask, request, jsonify, render_template, flash, redirect
import os
import pickle
import uuid
from speaker_verification.model_evaluation import run_user_evaluation
from speaker_verification.deep_speaker.audio import NUM_FRAMES, SAMPLE_RATE, read_mfcc, sample_from_mfcc
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
#model = load_model('model.h5')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = 'templates'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///voice_features.db"
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db = SQLAlchemy(app)

# class attendance(db.Model):
#     id= db.Column(db.Integer, primary_key=True)
#     name= db.Column (db.String(100), nullable=False)
#     audio_url= db.Column (db.String(200), nullable=False)
    
#     def repr_(self) -> str: 
#         return f"{self.id} - {self.name}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/record')
def record():
    return render_template('record.html')
# @app.route('/predict',methods=['POST'])
# def predict():
#     '''
#     For rendering results on HTML GUI
#     '''
#     int_features = [int(x) for x in request.form.values()]
#     final_features = [np.array(int_features)]
#     prediction = model.predict(final_features)

#     output = round(prediction[0], 2)

#     return render_template('index.html', prediction_text='Employee Salary should be $ {}'.format(output))


@app.route('/save-record', methods=['POST'])
def save_record():
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    file_name = str(uuid.uuid4()) + ".wav"
    full_file_name = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
    print(full_file_name)
    file.save(full_file_name)
    path = "D:/" + UPLOAD_FOLDER + "/" + file_name
    enroll(1,path)
    return 'success'


@app.route('/enroll')
def speaker_verification():
    # audio_encodings = dict()
    # audio_encodings[1] = sample_from_mfcc(read_mfcc("D:/tifr pehchaan/tifr-voice-dataset/22_muskan.wav", SAMPLE_RATE), NUM_FRAMES)
    # file = open('audio_encodings.dat', 'wb')
    # pickle.dump(audio_encodings, file)
    # file.close()
    # enroll(2,"D:/tifr pehchaan/tifr-voice-dataset/muskan test.wav")
    if validate(2,"D:/tifr pehchaan/tifr-voice-dataset/muskan-2.wav"):
        print("muskiii")
    else:
        print("fake muski")

    return render_template('index.html')


def enroll(id,audio):
    try:
        with open(os.path.join(BASE_DIR, 'audio_encodings.dat'), 'rb') as f:
            audio_encodings = pickle.load(f)
    except:
        audio_encodings = {}
    mfcc = sample_from_mfcc(read_mfcc(audio, SAMPLE_RATE), NUM_FRAMES)
    audio_encodings[id] = mfcc    
    with open(os.path.join(BASE_DIR, 'audio_encodings.dat'), 'wb') as f:
        pickle.dump(audio_encodings, f)
    print("enrolled!")
    return

def validate(id,audio):
    try:
        with open(os.path.join(BASE_DIR, 'audio_encodings.dat'), 'rb') as f:
            audio_encodings = pickle.load(f)
    except:
        audio_encodings = {}
    mfcc = audio_encodings[id]
    score = run_user_evaluation(mfcc, audio)
    result = round(score[0] * 100, 2)
    print(result)
    if result > 55.00:
        return True
    else:
        return False

if __name__ == "__main__":
    app.run(debug=True)