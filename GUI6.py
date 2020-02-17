from PyQt5.QtGui import *  
from PyQt5.QtGui import QValidator
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication

###############################################################################
#Import Needed Machine Learning Functions
import numpy as np
#Need 2 Functions to extract all the data from csv files
from ExtractDataFunctions import ExtractAccelerometerData
from ExtractDataFunctions import ExtractAcousticData

#Need 3 Functions to Organize all the all the data
from OrganizationFunctions import Inputs2CondensedForm
from OrganizationFunctions import System2CondensedForm
from OrganizationFunctions import AllData2WorkingForm

#Need 1 Function to Organize Files into TestDataFrame
from FeatureFunctions import getTESTDataFrame

#Need 2 Functions for Graphing
from FeatureFunctions import getGraphs
from FeatureFunctions import truncate

#Need # Functions to perform Machine Learning
from MachineLearningFunctions import getTESTMatrix
from MachineLearningFunctions import GetTrainingData
from MachineLearningFunctions import TrainModel
from MachineLearningFunctions import PredictModel
from MachineLearningFunctions import PredictProbModel
###############################################################################

import os
import sip
import csv


from PyQt5.uic import loadUiType
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
message = ""
"""
These RegExp are used to check for user input correctness

"""
regexp_checkCSV = QRegExp('^\/([A-z0-9-_+\s]+\/)*([A-z0-9]+\.(csv))$')
validator = QRegExpValidator(regexp_checkCSV)

regexp_checkint = QIntValidator()
intvalidator = QRegExpValidator(regexp_checkint)

regexp_checkdouble = QDoubleValidator()
doublevalidator = QRegExpValidator(regexp_checkdouble)
	
Ui_MainWindow, QMainWindow = loadUiType('MQAAdraft4_3.1.ui')

class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ): #provide values for attributes at runtime
        super(Main, self).__init__()
        self.setupUi(self)
        self.pushBrowse.clicked.connect(self.selectFile)
        self.pushBrowse_2.clicked.connect(self.selectmlFile)
        self.pushApply.clicked.connect(self.apply)
        self.pushRun.clicked.connect(self.run)
        self.HomeDirectory = os.getcwd() #saves the primary working directory
        self.directory = os.listdir(self.HomeDirectory)
        self.saveBttn.clicked.connect(self.file_save)
        self.actionOpen.triggered.connect(self.file_open)
        self.actionReset.triggered.connect(self.plots_close)
        self.message = 0
        #self.UI = []
        self.reset = 0
        
        
        #check User input for correct .csv file
        self.inputFile.setValidator(validator)
        self.inputFile.textChanged.connect(self.check_state)
        self.inputFile.textChanged.emit(self.inputFile.text())
        #check User input for correct .csv file for ml
        self.mlData.setValidator(validator)
        self.mlData.textChanged.connect(self.check_state)
        self.mlData.textChanged.emit(self.mlData.text())
        #shaft speed
        self.shaftSpeed.setValidator(regexp_checkdouble)
        self.shaftSpeed.textChanged.connect(self.check_state)
        self.shaftSpeed.textChanged.emit(self.shaftSpeed.text())
        #Num of rolling elements
        self.numberofElements.setValidator(regexp_checkint)
        self.numberofElements.textChanged.connect(self.check_state)
        self.numberofElements.textChanged.emit(self.numberofElements.text())
        #diameter of rolling elements
        self.diameterofElements.setValidator(regexp_checkdouble)
        self.diameterofElements.textChanged.connect(self.check_state)
        self.diameterofElements.textChanged.emit(self.diameterofElements.text())
        #pitch diameter
        self.pitchDiameter.setValidator(regexp_checkdouble)
        self.pitchDiameter.textChanged.connect(self.check_state)
        self.pitchDiameter.textChanged.emit(self.pitchDiameter.text())
        #Contact angle
        self.contactAngle.setValidator(regexp_checkdouble)
        self.contactAngle.textChanged.connect(self.check_state)
        self.contactAngle.textChanged.emit(self.contactAngle.text())
        #Frequency Acoustic
        self.samFreqAcst.setValidator(regexp_checkdouble)
        self.samFreqAcst.textChanged.connect(self.check_state)
        self.samFreqAcst.textChanged.emit(self.samFreqAcst.text())
        #Frequency Accelerometer
        """self.samFreqac.setValidator(regexp_checkdouble)
        self.samFreqac.textChanged.connect(self.check_state)
        self.samFreqac.textChanged.emit(self.samFreqac.text())"""
        
        
        
   
    def check_state(self, *args, **kwargs): 
        #this function is changes the color of the lineedit fields depending on state
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)
        
    #creates a dictionary from the saved CSV 
    def file_open(self): 
        #function called when the open file action in triggered. Creates a dictionary from a CSV file.
        filename = QFileDialog.getOpenFileName()[0]
        reader = csv.reader(open(filename, 'r'))
        d = {}
        for row in reader:
            k, v = row
            d[k] = v
                   
        print(d)
        
        self.setTextInfile(d)
        return True
    #used the dicitonary created above to assign saved variables to input parameters
    def setTextInfile(self, d):
        self.inputName.setText(d['inputName'])
        self.inputApplication.setText(d['inputApplication'])
        self.inputModelnum.setText(d['inputModelnum'])
        self.inputSavingalias.setText(d['inputSavingalias'])
        self.inputFile.setText(d['inputFile'])
        self.mlData.setText(d['mlData'])
        self.horsepower.setText(d['horsepower'])
        self.voltage.setText(d['voltage'])
        self.phase.setText(d['phase'])
        self.shaftnum.setText(d['shaftnum'])
        self.shaftSpeed.setText(d['shaftSpeed'])
        self.numberofElements.setText(d['numberofElements'])
        self.diameterofElements.setText(d['diameterofElements'])
        self.pitchDiameter.setText(d['pitchDiameter'])
        self.contactAngle.setText(d['contactAngle'])
        self.samFreqAcst.setText(d['samFreq'])
        

    
    """
    Hmm i wonder if this is used to save the file?
    """
    def file_save(self,): 
        #called when the save btn is clicked. converts user input to dictionary
        #then to dataframe then to csv file. 
        dict = CreateSaveDictionary(self.inputName.text(),\
                                    self.inputApplication.text(),\
                                    self.inputModelnum.text(),\
                                    self.inputSavingalias.text(),\
                                    self.inputFile.text(),\
                                    self.mlData.text(), \
                                    self.horsepower.text(), \
                                    self.voltage.text(), \
                                    self.phase.text(), \
                                    self.shaftnum.text(),\
                                    self.shaftSpeed.text(),\
                                    self.numberofElements.text(), \
                                    self.diameterofElements.text(), \
                                    self.pitchDiameter.text(), \
                                    self.contactAngle.text(), \
                                    self.samFreqAcst.text())
        CreateCSVfromDict(dict)
    """
    These functions create the figure widgets and toolbars
    """  
    
    #Accelerometer
    def addmpl(self, fig):
        self.canvas = FigureCanvas(fig)
        #self.canvas.setParent(None)
        self.graph01UI.addWidget(self.canvas)
        #self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,self.mainspectrum, coordinates=True)
        #self.toolbar.setParent(None)
        self.graph01UI.addWidget(self.toolbar)
        
    def addmpl02(self, fig):
        self.canvas = FigureCanvas(fig)
        #self.canvas.setParent(None)
        self.graph02UI.addWidget(self.canvas)
        #self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,self.mainspectrum, coordinates=True)
        #self.toolbar.setParent(None)
        self.graph02UI.addWidget(self.toolbar)
        
        
    def addgraph11(self, fig):
        self.canvas1 = FigureCanvas(fig)
        self.graph11UI.addWidget(self.canvas1)
        #self.canvas1.draw()
        self.toolbar1 = NavigationToolbar(self.canvas1,self.graph11, coordinates=True)
        self.graph11UI.addWidget(self.toolbar1)
        
    def addgraph12(self, fig):
        self.canvas2 = FigureCanvas(fig)
        self.graph12UI.addWidget(self.canvas2)
        #self.canvas2.draw()
        self.toolbar2 = NavigationToolbar(self.canvas2, 
                self.graph12, coordinates=True)
        self.graph12UI.addWidget(self.toolbar2)
        
    def addgraph21(self, fig):
        self.canvas3 = FigureCanvas(fig)
        self.graph21UI.addWidget(self.canvas3)
        #self.canvas3.draw()
        self.toolbar3 = NavigationToolbar(self.canvas3, 
                self.graph21, coordinates=True)
        self.graph21UI.addWidget(self.toolbar3)
        
    def addgraph22(self, fig):
        self.canvas4 = FigureCanvas(fig)
        self.graph22UI.addWidget(self.canvas4)
        #self.canvas4.draw()
        self.toolbar4 = NavigationToolbar(self.canvas4, 
                self.graph22, coordinates=True)
        self.graph22UI.addWidget(self.toolbar4)
        
    #ACOUSTIC
    def addmpl_2(self, fig):
        self.canvas = FigureCanvas(fig)
        #self.canvas.setParent(None)
        self.graph01UI_2.addWidget(self.canvas)
        #self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,self.mainspectrum_2, coordinates=True)
        #self.toolbar.setParent(None)
        self.graph01UI_2.addWidget(self.toolbar)
        
    def addmpl02_2(self, fig):
        self.canvas = FigureCanvas(fig)
        #self.canvas.setParent(None)
        self.graph02UI_2.addWidget(self.canvas)
        #self.canvas.draw()
        self.toolbar = NavigationToolbar(self.canvas,self.mainspectrum_2, coordinates=True)
        #self.toolbar.setParent(None)
        self.graph02UI_2.addWidget(self.toolbar)
        
        
    def addgraph11_2(self, fig):
        self.canvas1 = FigureCanvas(fig)
        self.graph11UI_2.addWidget(self.canvas1)
        #self.canvas1.draw()
        self.toolbar1 = NavigationToolbar(self.canvas1,self.graph11_2, coordinates=True)
        self.graph11UI_2.addWidget(self.toolbar1)
        
    def addgraph12_2(self, fig):
        self.canvas2 = FigureCanvas(fig)
        self.graph12UI_2.addWidget(self.canvas2)
        #self.canvas2.draw()
        self.toolbar2 = NavigationToolbar(self.canvas2, 
                self.graph12_2, coordinates=True)
        self.graph12UI_2.addWidget(self.toolbar2)
        
    def addgraph21_2(self, fig):
        self.canvas3 = FigureCanvas(fig)
        self.graph21UI_2.addWidget(self.canvas3)
        #self.canvas3.draw()
        self.toolbar3 = NavigationToolbar(self.canvas3, 
                self.graph21_2, coordinates=True)
        self.graph21UI_2.addWidget(self.toolbar3)
        
    def addgraph22_2(self, fig):
        self.canvas4 = FigureCanvas(fig)
        self.graph22UI_2.addWidget(self.canvas4)
        #self.canvas4.draw()
        self.toolbar4 = NavigationToolbar(self.canvas4, 
                self.graph22_2, coordinates=True)
        self.graph22UI_2.addWidget(self.toolbar4)

       
    #clearly selects file
    def selectFile(self,):
        self.inputFile.setText(QFileDialog.getOpenFileName()[0])
        self.inputfile = self.inputFile.text()
    #selects file but for a ml data   
    def selectmlFile(self,):
        self.mlData.setText(QFileDialog.getOpenFileName()[0])
        
    """
    Apply checks user inputs and then assigns them to function parameter variables
    In case the user doesn't supply input for a specific field, default inputs will
    be inserted.
    """    
    def apply(self,):
        if self.inputSavingalias.text() != "":
           self.savingalias = self.inputSavingalias.text()+".csv"
           self.inputSavingalias.setText(self.savingalias)
            
        if self.inputFile.text() != "":
            try:
                temp = self.inputFile.text()
                self.FileOfInterest = self.inputFile.text()
            except: 
                print("pu")
        else:
            print("no input file selected, using demo file.")
            self.FileOfInterest = "AccelerometerActualDataEdited.csv"
            self.inputFile.setText("/AccelerometerActualDataEdited.csv")
            
        if self.mlData.text() != "":
            self.TrainingDataFile = self.mlData.text() 
            print(self.TrainingDataFile)
        else:
            print("no ML data selected")
            self.TrainingDataFile = "MLSynthesizedData.csv" #default file location
            self.mlData.setText("/MLSynthesizedData.csv")
            
        if self.shaftSpeed.text() != "":
            self.n = float(self.shaftSpeed.text())
            print("type n =",type(self.n))
        else:
            print("no shaft speed selected")
            self.n = 2000/60
            self.shaftSpeed.setText(str(self.n))
            
            
        if self.numberofElements.text() != "":
            self.N = int(self.numberofElements.text())
        else:
            print("Number of elements not specified")
            self.N = 16
            self.numberofElements.setText(str(self.N))
            
        if self.diameterofElements.text() != "":
            self.Bd = float(self.diameterofElements.text())   
        else:
            print("Diameter of elements not specified")
            self.Bd = 0.331*254
            self.diameterofElements.setText(str(self.Bd))
            
        if self.pitchDiameter.text() != "":
            self.Pd = float(self.pitchDiameter.text())
        else:
            print("no pitch diameter specified")
            self.Pd = Pd = 2.815*254
            self.pitchDiameter.setText(str(self.Pd))
            
        if self.contactAngle.text() != "":
            self.phi = float(self.contactAngle.text())
        else:
            print("Contact angle not specified")
            self.phi = (15.17*3.14159)/180
            self.contactAngle.setText(str(self.phi))
        
        if self.samFreqAcst.text() != "":
            self.SampleFrequency = float(self.samFreqAcst.text())
           
        else:
            print("no sample frequency specified")
            self.SampleFrequency = 20000
            self.samFreqAcst.setText(str(self.SampleFrequency))
            
        self.popup = MyPopup("Applied")
        self.popup.setGeometry(QtCore.QRect(100, 100, 400, 200))
        self.popup.show()
        

 ##############################################       
    def getPlot(self,WhichPlot,plotinfo):
        X = plotinfo[0]
        Y = plotinfo[1]
        xlabel = plotinfo[2]
        ylabel = plotinfo[3]
        Title = plotinfo[4]
        if self.reset != 0:
            WhichPlot.cla()
            
        WhichPlot.plot(X,Y,c = np.random.rand(3,))
        WhichPlot.set_xlabel(xlabel, fontsize=12)
        WhichPlot.set_ylabel(ylabel, fontsize=12)
        WhichPlot.set_title(Title)
        WhichPlot.grid(True)
        if self.reset !=0:    
            self.canvas.draw()
        
    
        return None 
    
        
    def run(self,): #called when run is clicked
            
        if self.reset == 0:
            #instantiate the figures
            self.fig0 = plt.figure()
            self.sub0 = self.fig0.subplots()
            
            self.fig1 = plt.figure() 
            self.sub1 = self.fig1.subplots()
            
            self.fig2 = plt.figure()
            self.sub2 = self.fig2.subplots()
            
            self.fig3 = plt.figure()
            self.sub3 = self.fig3.subplots()
            
            self.fig4 = plt.figure()
            self.sub4 = self.fig4.subplots()
            
            self.fig5 = plt.figure()
            self.sub5 = self.fig5.subplots()
            
            self.fig6 = plt.figure() 
            self.sub6 = self.fig6.subplots()
            
            self.fig7 = plt.figure()
            self.sub7 = self.fig7.subplots()
            
            self.fig8 = plt.figure()
            self.sub8 = self.fig8.subplots()
            
            self.fig9 = plt.figure()
            self.sub9 = self.fig9.subplots()
            
        
        ###############################################################################
        #begin calling ml functions for processing

        #General
        Name_ID = "1"
        Application = "2"
        ModelNumber = "3"
        SavingAlias = "4"
        AccelerometerDataFilename = 'AccelerometerActualDataEdited.csv' #filename #main file
        AcousticDataFilename = 'DataOutputMic2Col.csv' #Wave File Name
        MLDataFilename = "MLSynthesizedData.csv"
        
        #Motor Characteristics
        Horsepower = "6"
        RatedVoltage = "7"
        ACorDC = "DC"
        NumberOfPolePairs = "9"
        NumberofShafts = "10"
        
        #Bearing Information
        ShaftSpeed = 300 #Also Used for Motor Characteristics
        NumberOfRollingElements = 3
        DiameterOfRollingElements = 3
        PitchDiameter = .2
        ContactAngle = .2
        
        #Processing Information 
        AccelerometerSamplingFrequency = 14000 #must be an non-zero int or float
        AcousticSamplingFrequency = 30000 #must be an non-zero int or float
        
        
        #Microcontroller Information
        #Receive Required Information
        A2DResolution = 16
        VoltageMax = 5
        VoltageMin = 0
        
        #System/Sensor Known Constants
        AccelerationMax = 50 
        AccelerationMin = -50
                
        #Convert User Inputs into a condensed form
        OnlyUserInput = Inputs2CondensedForm(Name_ID, Application, ModelNumber, SavingAlias,\
                                             AccelerometerDataFilename, AcousticDataFilename, \
                                             MLDataFilename, Horsepower, RatedVoltage, ACorDC, \
                                             NumberOfPolePairs, NumberofShafts, \
                                             ShaftSpeed, NumberOfRollingElements, \
                                             DiameterOfRollingElements,PitchDiameter, ContactAngle, \
                                             AccelerometerSamplingFrequency, AcousticSamplingFrequency)
        
        SystemInputs = System2CondensedForm(A2DResolution,VoltageMax,VoltageMin,AccelerationMax,AccelerationMin)
        
        #Acquire Accelerometer Actual Data
        time, amp, Voltage, Acceleration = ExtractAccelerometerData(OnlyUserInput,SystemInputs)
        
        #Acquire Acoustic Actual Data
        Channel1Time,Channel1Value,Channe21Time,Channe2Value = ExtractAcousticData(OnlyUserInput,SystemInputs)
        
        #Put All Data into Working Form
        trial = 2 #Select the instance of the data ************needs future work
        AllData = AllData2WorkingForm(OnlyUserInput,SystemInputs,time[trial], \
                                      amp[trial], Voltage[trial], Acceleration[trial],\
                                     Channel1Time,Channel1Value,Channe21Time,Channe2Value)
        
        #Machine Learning
        TestDF = getTESTDataFrame(AllData)
        TestMatrix = getTESTMatrix(TestDF)
        Xall_train, Yall_train, dataset = GetTrainingData(AllData)
        FinalClassifier = TrainModel(Xall_train, Yall_train)
        
        #Predict
        prediction,prediction_string = PredictModel(FinalClassifier,TestMatrix)
        prediction_proba = PredictProbModel(FinalClassifier,TestMatrix)

        plt.close('all')
        plot0info,plot1info,plot2info,plot3info,plot4info,\
        plot5info,plot6info,plot7info,plot8info,plot9info = getGraphs(AllData)
        #ACCELEROMETER PLOTTING
        self.getPlot(self.sub0,plot0info) #Raw Data
        self.getPlot(self.sub1,plot1info) #Raw Data w DC removed
        self.getPlot(self.sub2,plot2info) #Normalized
        self.getPlot(self.sub3,plot3info) #FFT
        self.getPlot(self.sub4,plot4info) #PSD
        
        #ACOUSTIC PLOTTING
        self.getPlot(self.sub5,plot5info)
        self.getPlot(self.sub6,plot6info)
        self.getPlot(self.sub7,plot7info)
        self.getPlot(self.sub8,plot8info)
        self.getPlot(self.sub9,plot9info)
        
        
        ###############################################################################
    
        if self.reset == 0:
            self.addmpl(self.fig0)
            self.addmpl02(self.fig2)
            self.addgraph11(self.fig1)
            self.addgraph12(self.fig3)
            self.addgraph21(self.fig4)
            #self.addgraph22(self.fig4)
            
            self.addmpl_2(self.fig5) #Raw Data
            self.addmpl02_2(self.fig7) #normalized
            self.addgraph11_2(self.fig6) #Raw Data w DC removed
            self.addgraph12_2(self.fig8) #FFT
            self.addgraph21_2(self.fig9) #PSD
            
            
        self.BSF.setText(str(truncate(TestDF["BSF"].values[0],2)))
        self.BPFI.setText(str(truncate(TestDF["BPFI"].values[0],2)))
        self.BPFO.setText(str(truncate(TestDF["BPFO"].values[0],2)))
        self.FTF.setText(str(truncate(TestDF["FTF"].values[0],2)))
        
        self.earlyEdit.setText(str(truncate(prediction_proba[0,0],2)))
        self.suspectEdit.setText(str(truncate(prediction_proba[0,1],2)))
        self.normalEdit.setText(str(truncate(prediction_proba[0,2],2)))
        """
        self.immEdit.setText(str(Prediction[0,3]))
        self.innerEdit.setText(str(Prediction[0,4]))
        self.rollingEdit.setText(str(Prediction[0,5]))
        self.stageEdit.setText(str(Prediction[0,6]))
        """
        self.reset = 1 
 
        
    def close_application(self,): #self explanitory
        sys.exit()

###############################################################################
    def updategraphs(self,fig):
        print("made it to update graphs")
        sip.delete(self.canvas)
        sip.delete(self.canvas1)
        sip.delete(self.canvas2)
        sip.delete(self.canvas3)
        sip.delete(self.canvas4)
        #self.spectrumUI.removeWidget(self.canvas)
        self.canvas = FigureCanvas(fig[0])
        self.canvas1 = FigureCanvas(fig[1])
        self.canvas2 = FigureCanvas(fig[2])
        self.canvas3 = FigureCanvas(fig[3])
        self.canvas4 = FigureCanvas(fig[4])
        
    def rmmpl(self,):
        print("in rmmpl")
        self.spectrumUI.removeWidget(self.canvas)
        self.canvas.close()
        self.spectrumUI.removeWidget(self.toolbar)
        self.toolbar.close()
        
        self.graph11UI.removeWidget(self.canvas)
        self.canvas.close()
        self.graph11UI.removeWidget(self.toolbar)
        self.toolbar.close()
        
        self.graph12UI.removeWidget(self.canvas)
        self.canvas.close()
        self.graph12UI.removeWidget(self.toolbar)
        self.toolbar.close()
        
        self.graph21UI.removeWidget(self.canvas)
        self.canvas.close()
        self.graph21UI.removeWidget(self.toolbar)
        self.toolbar.close()
        
        self.graph22UI.removeWidget(self.canvas)
        self.canvas.close()
        self.graph22UI.removeWidget(self.toolbar)
        self.toolbar.close()       
            
    def plots_close(self,):
        print("made it to plots_close")
        self.spectrumUI.removeWidget(self.canvas)
        sip.delete(self.canvas)
        self.canvas = None
        self.spectrumUI.removeWidget(self.toolbar)
        sip.delete(self.toolbar)
        self.toolbar = None
    
        self.graph11UI.removeWidget(self.canvas1)
        self.canvas1.close()
        self.graph11UI.removeWidget(self.toolbar1)
        self.toolbar1.close()
        
        self.graph12UI.removeWidget(self.canvas2)
        self.canvas2.close()
        self.graph12UI.removeWidget(self.toolbar2)
        self.toolbar2.close()
        
        self.graph21UI.removeWidget(self.canvas3)
        self.canvas3.close()
        self.graph21UI.removeWidget(self.toolbar3)
        self.toolbar3.close()
        
        self.graph22UI.removeWidget(self.canvas4)
        self.canvas4.close()
        self.graph22UI.removeWidget(self.toolbar4)
        self.toolbar4.close()       

class MyPopup(QWidget): #creates popup windows
    def __init__(self, message):
        QWidget.__init__(self)
        alertholder = QLabel(self)
        alertholder.setText(message)
        alertholder.setAlignment(Qt.AlignCenter)
        
        vbox = QVBoxLayout()
        vbox.addWidget(alertholder)
        self.setLayout(vbox)
 
        
        
if __name__ == "__main__": #instantiates GUI and opens it
    from PyQt5 import *
    import sys
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    app.exec_()

    