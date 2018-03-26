import FreeCAD, FreeCADGui, Part, math
import DraftVecUtils
import pivy
import time

from joy import ListenerThread
from joy import JoyInterface

from pivy import coin
from FreeCAD import Base

try:
    from PySide import QtCore, QtGui
    FreeCAD.Console.PrintMessage("PySide is used" + "\n")
except:
    from PyQt4 import QtCore, QtGui
    FreeCAD.Console.PrintMessage("PyQt4 is needed" + "\n")

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

DEBUG = True

class Joynav(object):
    def __init__(self):
        super(Joynav, self).__init__()
        self.joyInterface = JoyInterface()
        self.getDevices()

    def getDevices(self):
        [self.deviceList, self.deviceNames] = self.joyInterface.findDevices()
        self.devicesAvailable = ( len(self.deviceList) > 0 )
        self.dprint(self.devicesAvailable)
        self.dprint(self.deviceList)

    def dprint(self,str):
        if DEBUG:
            print(str)

    def setupUI(self, Joynav):
        FCUi = FreeCADGui.UiLoader()
        self.width = 400
        self.height = 400

        # Window Properties
        Joynav.setObjectName(_fromUtf8("Joynav"))
        Joynav.resize(self.width, self.height)
        Joynav.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedKingdom))
        Joynav.setWindowTitle(QtGui.QApplication.translate("Joynav", "Joynav", None, QtGui.QApplication.UnicodeUTF8))
        
        # Main Layout Container
        self.mainLayout = QtGui.QVBoxLayout(Joynav)

        self.devicesLayout = QtGui.QHBoxLayout()

        ## Not Connected Label
        self.notConnectedLabel = QtGui.QLabel()
        self.notConnectedLabel.setWordWrap(True);
        self.notConnectedLabel.setObjectName(_fromUtf8("NotConnectedLabel"))
        self.notConnectedLabel.resize(self.width, self.height)
        self.notConnectedLabel.setText(QtGui.QApplication.translate("NotConnectedLabel", 
            "Connection to device couldn\'t be established. Make sure the joystick is plugged in properly and then try again to connect.", None, QtGui.QApplication.UnicodeUTF8))

        # Retry Button
        self.retryButton = QtGui.QToolButton()
        self.retryButton.setObjectName(_fromUtf8("Retry Button"))
        self.retryButton.setText(QtGui.QApplication.translate("Joynav", "Retry", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.retryButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.retryButtonPressed)

        ## Devices Label
        self.devicesLabel = QtGui.QLabel()
        self.devicesLabel.setWordWrap(True);
        self.devicesLabel.setObjectName(_fromUtf8("DevicesLabel"))
        self.devicesLabel.resize(self.width, self.height)
        self.devicesLabel.setText(QtGui.QApplication.translate("DevicesLabel", "Available Devices:", None, QtGui.QApplication.UnicodeUTF8))

        ## Device List ComboBox
        self.deviceSelect = QtGui.QComboBox()
        self.deviceSelect.setObjectName(_fromUtf8("DeviceSelect"))
        self.devicesLayout.addWidget(self.deviceSelect)
        
        # Connect Button
        self.connectButton = QtGui.QToolButton()
        self.connectButton.setObjectName(_fromUtf8("Connect Button"))
        self.connectButton.setText(QtGui.QApplication.translate("Joynav", "Connect", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.connectButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.connectButtonPressed)
        self.devicesLayout.addWidget(self.connectButton)

        # Start Button
        self.startButton = QtGui.QToolButton()
        self.startButton.setObjectName(_fromUtf8("Start Button"))
        self.startButton.setText(QtGui.QApplication.translate("Joynav", "Start", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.startButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.startButtonPressed)

        # Stop Button
        self.stopButton = QtGui.QToolButton()
        self.stopButton.setObjectName(_fromUtf8("StopButton"))
        self.stopButton.setText(QtGui.QApplication.translate("Joynav", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        QtCore.QObject.connect(self.stopButton, QtCore.SIGNAL(_fromUtf8("pressed()")), self.stopButtonPressed)

        self.updateUI()
        
        #QtCore.QMetaObject.connectSlotsByName(Joynav)

    def updateUI(self):
        # Update Device Select entries
        for i in range(len(self.deviceList)):
            self.deviceSelect.addItem(_fromUtf8(""))
            self.deviceSelect.setItemText(i, QtGui.QApplication.translate("DeviceSelect", self.deviceList[i] + ': ' + self.deviceNames[i], None, QtGui.QApplication.UnicodeUTF8))

        # Show/ hide UI elements
        if self.devicesAvailable:
            if not self.mainLayout.isEmpty():
                self.mainLayout.removeWidget(self.notConnectedLabel)
                self.notConnectedLabel.hide()
                self.mainLayout.removeWidget(self.retryButton)
                self.retryButton.hide()

            self.mainLayout.addLayout(self.devicesLayout)
            #self.mainLayout.addStretch(1)
            self.mainLayout.addWidget(self.startButton)
            self.mainLayout.addWidget(self.stopButton)
        else:
            if not self.mainLayout.isEmpty():
                self.mainLayout.removeLayout(self.devicesLayout)
                self.devicesLayout.hide()
                self.mainLayout.removeWidget(self.startButton)
                self.startButton.hide()
                self.mainLayout.removeWidget(self.stopButton)
                self.stopButton.hide()

            self.mainLayout.addWidget(self.notConnectedLabel)
            self.mainLayout.addWidget(self.retryButton)

    def retryButtonPressed(self):
        self.getDevices()
        self.updateUI()

    def connectButtonPressed(self):
        self.dprint("connect")
        self.axisMap = {}
        self.buttonMap = {}
        if self.devicesAvailable:
            [connectionSuccess, self.axisMap, self.buttonMap] = self.joyInterface.connect(0)
            if connectionSuccess:
                self.dprint( 'axes found: %s' % (', '.join(self.axisMap)))
                self.dprint( 'buttons found: %s' % (', '.join(self.buttonMap)))
            else:
                self.dprint('Connection to device couldn\'t be established.')

    def startButtonPressed(self):
        self.dprint("Starting Input Listener!" + "\n")
        #self.listener.start()

    def stopButtonPressed(self):
        self.dprint("Stopping input Listener!" + "\n")
        #self.listener.stop()
    
class JoynavMacro(object):
    d = QtGui.QWidget()
    d.ui = Joynav()
    d.ui.setupUI(d)
    if __name__ == '__main__':
        d.show()

def main():
    o = JoynavMacro()

if __name__ == '__main__':
    main()

#self.cam = Gui.ActiveDocument.ActiveView.getCameraNode()
#self.listener = ListenerThread(0, self.cam)
#self.listener.connect(0)

# import threading

# exitFlag = 0

# class myThread (threading.Thread):
#     def __init__(self, threadID, name, counter, cam):
#         threading.Thread.__init__(self)
#         self.threadID = threadID
#         self.name = name
#         self.counter = counter
#         self.cam = cam

#     def run(self):
#         print "Starting " + self.name
#         self.sequence(self.name)
#         print "Exiting " + self.name

#     def sequence(self, threadName):
#         self.moveCenter(0.0, 0.0, 0.0)
#         for i in range(0,360):
#             r = 20.0+10.0*math.cos(4.0*math.radians(i))
#             alpha = math.radians(i)
#             beta = math.radians(45.0)
#             gamma = math.radians(2*i)
#             self.zoom(r)
#             self.eulerRotation(alpha, beta, gamma)
#             time.sleep(0.01)

#     def moveCenter(self, x, y, z):
#         self.cam.position = coin.SbVec3f(x, y, z)

#     def zoom(self, d):
#         self.cam.height.setValue(d)

#     def eulerRotation(self, alpha, beta, gamma):
#         x = coin.SbVec3f(1.0,0.0,0.0)
#         y = coin.SbVec3f(0.0,1.0,1.0)
#         z = coin.SbVec3f(0.0,0.0,1.0)

#         r1 = coin.SbRotation()
#         r1.setValue(z, alpha)

#         r2 = coin.SbRotation()
#         r2.setValue(x, beta)

#         r3 = coin.SbRotation()
#         r3.setValue(z, gamma)
#         self.cam.orientation = r3*r2*r1

#def animate(self):
    #    thread1 = myThread(1, "Thread-1", 1, Gui.ActiveDocument.ActiveView.getCameraNode())
    #    thread1.start()