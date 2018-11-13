# Face-Attendance-System
An Attendance Checking System using Deep Facial Recognition, written in Python.
[Small demo](https://www.youtube.com/watch?v=XzDDHDtsNwk)


## Setup guidance
* Install dependences:
```
sudo apt-get install -y python-pip python3-pip cmake
```
* Create a folder containing virtual environments:
```
mkdir ~/.virtualenvs
cd ~/.virtualenvs
```
* Install virtual-environment packages:
```
sudo /usr/local/bin/pip install virtualenv virtualenvwrapper
sudo /usr/local/bin/pip3 install virtualenv virtualenvwrapper
```
* Using a text editor, open file "~/.bashrc", then add the following text into the end of the file, and save the file:
```
# virtualenv and virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/local/bin/virtualenvwrapper.sh
```
* Create a virtual environment, named *face_attendace*:
```
source ~/.bashrc
/usr/local/bin/virtualenv -p /usr/bin/python3 face_attendace
workon face_attendace
```
* Change to the directory containing your downloaded project, then install requirements:
```
cd <dir_to_project>
pip install -r requirements.txt
```


## Team members

* **Nguyen Tan Phu**
* **Nguyen Tan Sy**
* **Nguyen Tai**
* **Nguyen Van Quang**
