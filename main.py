import sys, os
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import *
from PyQt5.QtGui import *
# from PIL import Image
# import cv2
# import face_recognition
from scipy.io import wavfile
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import sounddevice as sd
import time
import pickle
from speaker_verification.model_evaluation import run_user_evaluation
from speaker_verification.deep_speaker.audio import NUM_FRAMES, SAMPLE_RATE, read_mfcc, sample_from_mfcc

admin_verified = False
admin = "user"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
filename = ""

class Ui_MainWindow(object):
    def __init__(self):
        self.sr = 44100
        self.max_duration = 600
        self.ch = 1
        self.save_num = 0
        self.audio = np.array([])
        self.input_device = sd.query_devices(kind='input')
        self.output_device = sd.query_devices(kind='output')
        self.time = 0
        self.status = 0

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(472, 340)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(180, 70, 131, 51))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label.setText('status')
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.input = QtWidgets.QLabel(self.centralwidget)
        self.input.setGeometry(QtCore.QRect(50, 130, 381, 16))
        self.input.setObjectName("input")
        self.input.setText('input device :: '+self.input_device['name'])

        self.output = QtWidgets.QLabel(self.centralwidget)
        self.output.setGeometry(QtCore.QRect(50, 170, 381, 15))
        self.output.setObjectName("output")
        self.output.setText('output device :: '+self.output_device['name'])

        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(40, 210, 395, 30))
        self.widget.setObjectName("widget")

        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.rec_B = QtWidgets.QPushButton(self.widget)
        self.rec_B.setObjectName("rec_B")
        self.horizontalLayout.addWidget(self.rec_B)
        self.rec_B.clicked.connect(self.rec)

        self.play_B = QtWidgets.QPushButton(self.widget)
        self.play_B.setObjectName("play_B")
        self.horizontalLayout.addWidget(self.play_B)
        self.play_B.clicked.connect(self.play)

        self.stop_B = QtWidgets.QPushButton(self.widget)
        self.stop_B.setObjectName("stop_B")
        self.horizontalLayout.addWidget(self.stop_B)
        self.stop_B.clicked.connect(self.stop)

        # self.save_B = QtWidgets.QPushButton(self.widget)
        # self.save_B.setObjectName("save_B")
        # self.horizontalLayout.addWidget(self.save_B)
        # self.save_B.clicked.connect(self.save)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 472, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.rec_B.setText(_translate("MainWindow", "REC"))
        self.play_B.setText(_translate("MainWindow", "ENROLL"))
        self.stop_B.setText(_translate("MainWindow", "STOP"))
        # self.save_B.setText(_translate("MainWindow", "SAVE"))

    def rec(self):
        self.audio = sd.rec(frames=self.max_duration*self.sr, samplerate=self.sr, channels=self.ch, dtype='float32',
                            device=self.input_device['name'])
        self.time = time.time()
        self.status = 'rec'
        self.label.setText('REC')

    def play(self):
        try:
            # sd.play(data=self.audio, samplerate=self.sr, device=self.output_device['name'])
            # self.label.setText('PLAY')
            # save the file and then do it 
            self.status = 'play'
            try:
                with open(os.path.join(BASE_DIR, 'audio_encodings.dat'), 'rb') as f:
                    audio_encodings = pickle.load(f)
            except:
                audio_encodings = {}
            mfcc = sample_from_mfcc(read_mfcc("D:/tifr pehchaan/"+file_name, SAMPLE_RATE), NUM_FRAMES)
            audio_encodings[1] = mfcc    
            with open(os.path.join(BASE_DIR, 'audio_encodings.dat'), 'wb') as f:
                pickle.dump(audio_encodings, f)
            self.label.setText('Enrolled')
        except:
            self.label.setText('None')

    def stop(self):
        sd.stop()
        if self.status == 'rec':
            s_time = time.time() - self.time
            self.audio = self.audio[:int(round(s_time, 0)*self.sr)]
            global file_name
            file_name = 'rec_audio'+str(self.save_num)+'.wav'
            wavfile.write(file_name, self.sr, self.audio)
            print(file_name)
        # self.status = 'stop'
        try:
            with open(os.path.join(BASE_DIR, 'audio_encodings.dat'), 'rb') as f:
                audio_encodings = pickle.load(f)
        except:
            audio_encodings = {}
        mfcc = audio_encodings[1]
        score = run_user_evaluation(mfcc, file_name)
        result = round(score[0] * 100, 2)
        print(result)
        if result > 55.0:
            self.label.setText('verified')
        else:
            self.label.setText('not verified')
        # self.label.setText('no')


    def save(self):
        if len(self.audio) != 0:
            file_name = 'rec_audio'+str(self.save_num)+'.wav'
            wavfile.write(file_name, self.sr, self.audio)
            self.save_num += 1
            self.label.setText(str(self.save_num)+'_SAVE')
        else:
            self.label.setText('None')
    
    #for esp32
    '''w
    def download(url, save_location):
    try:
        audio = requests.get(url)
        with open(save_location, 'wb') as audio_file:
            audio_file.write(audio.content)
    except IOError as err:
        print(err)
        print("There was an error retrieving the data. Check your internet connection and try again.")
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n\nYou have interrupted an active download.\n Cleaning up files now.")
        os.remove(save_location)
        sys.exit(1)
    '''


# app = QApplication(sys.argv)

# widget = QtWidgets.QStackedWidget()

# landingpage = MySAdminLogin()
# widget.addWidget(landingpage)
# widget.setFixedWidth(962)
# widget.setFixedHeight(730)
# widget.show()
# sys.exit(app.exec_())

# # if path is empty display msg
# # bg set
# # grayscale
# # disable text writing in labels
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())