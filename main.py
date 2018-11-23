from PyQt5.QtCore import QByteArray, QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QCamera
from PyQt5.QtWidgets import QAction, QActionGroup, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QWidget, QInputDialog, QFileDialog
from PyQt5.QtGui import QImage
from PyQt5 import QtCore, QtWidgets
from GUI import Ui_Camera
from apis.motion_blur import detect_blur
from apis.landmark import find_bbox, draw_bbox, check_front_view
from apis.recognition import Recognizer
import os, sys, sqlite3, cv2


class Camera(QMainWindow):

	def __init__(self, parent=None):
		super(Camera, self).__init__(parent)		
		self.ui = Ui_Camera()
		self.pre_id=0
		self.cur_id=0
		self.count=0
		self.checked=0
		self.audio_settime = 0
		self.allow_flag=1
		self.check_list=[]
		self.camera = None
		self.imageCapture = None
		self.isCapturingImage = False
		self.applicationExiting = False
		self.ui.setupUi(self)
		cameraDevice = QByteArray()
		videoDevicesGroup = QActionGroup(self)
		videoDevicesGroup.setExclusive(True)
		for deviceName in QCamera.availableDevices():
			description = QCamera.deviceDescription(deviceName)
			videoDeviceAction = QAction(description, videoDevicesGroup)
			videoDeviceAction.setCheckable(True)
			videoDeviceAction.setData(deviceName)
			if cameraDevice.isEmpty():
				cameraDevice = deviceName
				videoDeviceAction.setChecked(True)
			self.ui.menuDevices.addAction(videoDeviceAction)
		videoDevicesGroup.triggered.connect(self.updateCameraDevice)
		self.setCamera(cameraDevice)
		
		# Create and load model
		path_pretrained = "apis/models/facenet/20180402-114759.pb"
		path_SVM = "apis/models/SVM/SVM.pkl"
		self.recognizer = Recognizer()
		self.recognizer.create_graph(path_pretrained, path_SVM)
		# self.ui.absenceNumber.hide()
		self.timer.start(5)

		# Others
		# self.file_path = ""
		# self.audios = ["../data/tone.mp3", "../data/face_stable.mp3", "look_ahead.mp3"]


	def setCamera(self, cameraDevice):
		'''[setup camera]
		
		[correct camera parameters]
		
		Arguments:
			cameraDevice -- [laptop camera]
		'''
		 
		self.camera = cv2.VideoCapture(0)
		self.image = None
		self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
		self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
		self.timer = QTimer()
		self.timer.timeout.connect(self.update_frame)
		self.timer.stop()



	def update_frame(self):
		'''[process frame]
		
		[face recognition ]
		'''
		name=""
		ret,self.image= self.camera.read(0)
		self.image=cv2.flip(self.image,1)
		# Remove motion-blur frame
		if not detect_blur(self.image, thres=5.0):
			face_locs = find_bbox(self.image)
			# n_faces = len(face_locs)
			# # Remove multi-face frame
			# if n_faces==1:
			for each_face in face_locs:
				is_frontal, _ = check_front_view(self.image, each_face)
				# Remove non-frontal-view frame
				if is_frontal:
					self.image, _, _ = draw_bbox(self.image, each_face, color="green")

					image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
					id, score = self.recognizer.recognize(image, each_face, 0.18825)

					if not id == "unknown":

						#Collect ID and name from text file
						filepath = 'ID_Name.txt'
						with open(filepath) as fp:
							line = fp.readline()
							while line:
								ID= line.strip()
								if ID == id:
									next_line= fp.readline()
									name= next_line.strip()
								else:
									pass
								line = fp.readline()
										
						# if int(id) == 1512489:
						# 	name="Phu"
					else:
						name =" Unname"
					self.pre_id= self.cur_id
					self.cur_id = id
					dis_str= "Student ID: %s, Name: %s" % (id, name)
					# Verification: ID was checked or not 
					self.ui.textBrowser.append(dis_str)
					for check_idx in self.check_list:
						if check_idx == id  :
							self.checked = True
						else:
							pass
					# Process if ID has not been checked
					# if not self.checked:
					if not id== "unknown":
						# positive ID 
						if self.pre_id==self.cur_id:
							self.count+=1
							# popup after 5 times 
							if self.count ==2:
								# print("here")
								id = int(id)
								self.ui.textBrowser_confirm.append(dis_str)
								self.checked =0
							else:
								pass
						else:
							self.count =0
					else:
						pass
						self.count=0  
				else:
					dis_str= "Face is not in frontal view"
					self.ui.textBrowser.append(dis_str)
					self.count=0
			# else:
			# 	dis_str= "Require 1 face in the camera"
			# 	self.ui.textBrowser.append(dis_str)
			# 	self.count=0
		else:
			dis_str= "Frame is montion-blurred"
			self.ui.textBrowser.append(dis_str)
			self.count =0
		self.displayImage(self.image,1)


	def displayImage(self,img,window=1):

		"""[display frame]
		
		[correct image type and on-screen display]
		
		Arguments:
			img {[cv2 image]} -- [processed frame]
		
		Keyword Arguments:
			window {number} -- [description] (default: {1})
		"""
		
		qformat= QImage.Format_Indexed8
		if len(img.shape) == 3:
			if img.shape[2] == 4:
				qformat= QImage.Format_RGBA8888
			else:
				qformat = QImage.Format_RGB888
		outImage=QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)
		outImage = outImage.rgbSwapped()
		if window ==1:		 
			self.ui.img_label.setPixmap(QPixmap.fromImage(outImage))
			self.ui.img_label.setScaledContents(True)


	def display_absences(self,absences):
		"""[display the number of absences]
		
		[The number of absences of each ID will be on-screen 
		if absent times >= threshold, a notification will appear on the screen]
		
		Arguments:
			absences {[int]} -- [absent times]
		"""
		self.ui.absenceNumber.display(absences)
		if absences == 3:
			QMessageBox.warning(self, 'Absent Warning', 'This is your last absence') 
		elif absences > 3:
			QMessageBox.critical(None,'Absent Fail',"Your absences exceeded the allowable threshold", QMessageBox.Abort)
	

	def startCamera(self):
		"""[start camera]
		
		[Unless file path is invalid, camera is closed]
		"""
		self.timer.start(5)


	def stopCamera(self):
		self.timer.stop()


	def displayCameraError(self):
		QMessageBox.warning(self, "Camera error", self.camera.errorString())


	def updateCameraDevice(self, action):
		"""[update camera]
		
		[Look for active cameras]
		
		Arguments:
			action  -- [flag of a active camera]
		"""
		self.setCamera(action.data())


	def close(self):
		"""[close event]
		
		[if there is a close event,data in the table will be saved to excel file  ]
		"""
		reply = QMessageBox.question(self, 'Message',
			"Are you sure to quit?", QMessageBox.Yes | 
			QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			QtCore.QCoreApplication.instance().quit
			sys.exit()
		else:
			pass


	def closeEvent(self, event):
		"""[close event ]
		
		[if we have a force exit event, a notification will be display for checking quit action
		if event is accepted, data will be saved and program close ]
		
		Arguments:
			event {[event]} -- [exit event from click (X)]
		"""
		
		reply = QMessageBox.question(self, 'Message',
			"Are you sure to quit?", QMessageBox.Yes | 
			QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			event.accept()
		else:
			event.ignore()  



	def correct_mssv(self,mssv):
		"""[confirm student ID]
		
		[confirm recognised student ID
		if ID is wrong, fill out another one and press Enter]
		
		Arguments:
			mssv {[int]} -- [student ID]
		"""
		mssv_check, okPressed = QInputDialog.getInt(self, "Student confirm","MSSV:", mssv, 0, 100000000, 1)
		if okPressed:
			return(mssv_check)
		else:
			return(mssv)


if __name__ == '__main__':

	app = QApplication(sys.argv)
	camera = Camera()
	camera.show()
	if(sys.exit(app.exec_())):
		camera.close()
