#!/bin/env python3
import sys
import json
import PyQt5.QtCore as Qc
import PyQt5.QtGui as Qg
import PyQt5.QtWidgets as Qw

class MainWindow(Qw.QMainWindow):
    '''
    MainWindow is the base window of Neuromake. It has one pushButton for each
    key in config. Selecting that pushButton launches the ConfigWindow for that
    key
    '''
    def __init__(self,config):
        super().__init__()
        self.config = config
        self.setWindowTitle('Neuromake')
        self.setGeometry(300,300,700,300)

        # Create central widget, will have 3 columns
        self.wMain = Qw.QWidget()
        self.mainLayout = Qw.QHBoxLayout()

        # left column: main setting selection (keys of config)
        self.wLeft = Qw.QListWidget()
        self.wLeft.addItems(self.config.keys())
        self.wLeft.currentRowChanged.connect(self.show_subsettings)
        self.mainLayout.addWidget(self.wLeft,1)

        # mid column: stacked lists, where each list = subdict.keys()
        # right column: stacked lists, where each list = subdict.values()
        self.wRight = Qw.QWidget()
        self.settingsLayout = Qw.QHBoxLayout()
        self.settingsLayout.setSpacing(0)
        self.settingsLayout.setContentsMargins(0,0,0,0)

        self.wSettingsKey = Qw.QStackedWidget()
        self.wSettingsVal = Qw.QStackedWidget()
        self.lSetKeys = []
        self.lSetVals = []
        for v in self.config.values():
            lsetKeys = []
            rsetKeys = []
            for k,x in v.items():
                if '__' not in k:
                    lsetKeys.append(k)
                    if isinstance(x,list):
                        rsetKeys.append(f'[ {", ".join(x)}]')
                    elif isinstance(x,str):
                        rsetKeys.append(x)
                    elif isinstance(x,bool):
                        rsetKeys.append(str(x))
            leftList = Qw.QListWidget()
            leftList.addItems(lsetKeys)
            self.lSetKeys.append(leftList)
            self.wSettingsKey.addWidget(leftList)

            rightList = Qw.QListWidget()
            rightList.addItems(rsetKeys)
            self.lSetVals.append(rightList)
            self.wSettingsVal.addWidget(rightList)

        self.settingsLayout.addWidget(self.wSettingsKey,1)
        self.settingsLayout.addWidget(self.wSettingsVal,3)
        self.wRight.setLayout(self.settingsLayout)
        self.mainLayout.addWidget(self.wRight,3)

        self.wMain.setLayout(self.mainLayout)
        self.setCentralWidget(self.wMain)
        self.show()

    def show_subsettings(self,i):
        self.currentSubsettingIndex = i
        self.wSettingsVal.setCurrentIndex(i)
        self.wSettingsKey.setCurrentIndex(i)


class ConfigWindow(Qw.QDialog):
    '''
    for each setting, we need to show current values and allow them to update
    those values
    '''
    def __init__(self,config,key):
        super().__init__()
        self.subconfig = config[key]
        self.setWindowTitle(f'{config[key]["__label__"]}')
        self.groupBox = Qw.QGroupBox(key)

        layout = Qw.QFormLayout()
        # loop through subconfig, create widgets to add to groupBox
        for k,v in self.subconfig.items():
            if '__' not in k:
                if isinstance(v,list):
                    listWidget = Qw.QListWidget(self)
                    listWidget.addItems(v)
                    layout.addRow(Qw.QLabel(k,self),listWidget)
                elif isinstance(v,str):
                    layout.addRow(Qw.QLabel(k,self),Qw.QLineEdit(v,self))
                elif isinstance(v,bool):
                    comboBox = Qw.QComboBox(self)
                    comboBox.addItems(["True","False"])
                    comboBox.setCurrentText(str(v))
                    layout.addRow(Qw.QLabel(k,self),comboBox)
                print(k,v)

        self.savePushButton = Qw.QPushButton('Save')
        self.resetPushButton = Qw.QPushButton('Reset')
        self.cancelPushButton = Qw.QPushButton('Cancel')
        layout.addRow(self.savePushButton,self.resetPushButton)
        self.setLayout(layout)
        self.show()


if __name__ == '__main__':
    with open('./config/sm_config.json','r') as x:
        config = json.load(x)
    app = Qw.QApplication(sys.argv)
    main = MainWindow(config)
    sys.exit(app.exec_())









    #
    #
    #     self.formGroupBox = QGroupBox("Form layout")
    #     self.ageSpinBar = QSpinBox()
    #     self.countryComboBox = QComboBox()
    #     self.countryComboBox.addItems(["Pakistan", "USA", "UAE"])
    #     self.nameLineEdit = QLineEdit()
    #     self.createFormGroupBox()
    #
    #     self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
    #     self.buttonBox.accepted.connect(self.getInfo)
    #     #        buttonBox.accepted.connect(self.getInfo)
    #     self.buttonBox.rejected.connect(self.reject)
    #
    #     mainLayout = QVBoxLayout()
    #     mainLayout.addWidget(self.formGroupBox)
    #     mainLayout.addWidget(self.buttonBox)
    #     self.setLayout(mainLayout)
    #
    #     self.setWindowTitle("Form Layout - pythonspot.com")
    #
    # def getInfo(self):
    #     print("Person Name : {0}".format(self.nameLineEdit.text()))
    #     print("Country : {0}".format(self.countryComboBox.currentText()))
    #     print("Age : {0}".format(self.ageSpinBar.text()))
    #     self.close()
    #
    # def createFormGroupBox(self):
    #     layout = QFormLayout()
    #     layout.addRow(QLabel("Name"), self.nameLineEdit)
    #     layout.addRow( QLabel("Country"),self.countryComboBox)
    #     layout.addRow( QLabel("Age"), self.ageSpinBar)
    #     self.formGroupBox.setLayout(layout)
