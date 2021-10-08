import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import pandas
from giaodien import Ui_MainWindow
import random
from ppadb.client import Client as AdbClient
import os
from PyQt5.QtCore import QMutex,QObject, QRunnable, QThread, Qt, QThreadPool, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
import time
import uiautomator2 as u2
import outlook
import requests
import pandas as pd
import emoji
import re
from unidecode import unidecode
import json

def getDevice(serialNumber):
    adb = AdbClient(host="127.0.0.1", port=5037)

    listDevice = adb.devices()

    for device in listDevice:
        if (device.serial == serialNumber):
            return device


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:
    - finished: No data
    - error:`tuple` (exctype, value, traceback.format_exc() )
    - result: `object` data returned from processing, anything
    - progress: `tuple` indicating progress metadata
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(dict)
    progress = pyqtSignal(tuple)


class Worker(QObject):
    finished = pyqtSignal()
    updatedBalance = pyqtSignal()

    def runViewPhone(self, cmd):
        os.system(cmd)
        self.finished.emit()
        time.sleep(2)

# 1. Subclass QRunnable


class Runnable(QRunnable):

    result = pyqtSignal(int)
    resultAccount = pyqtSignal()

    def __init__(self, cmd, serialNumber):
        super().__init__()
        self.signals = WorkerSignals()
        self.cmd = cmd
        self.serialNumber = serialNumber

    def runViewPhone(self):

        result = {
            "serialNumber": self.serialNumber,
            "status": "Đã mở scrcpy",
        }
        self.signals.result.emit(result)

        os.system(self.cmd)


class Remote(QThread):

    resultAccount = pyqtSignal()
    def __init__(self, deviceName,passLZD,versionAppLZD, parent = None):
        super().__init__()
        self.signals = WorkerSignals()
   
        
        self.LZD = ""
        self.passLZD = passLZD
        self.uid = ""
        self.passFB = ""
        self.mail = ""
        self.passMail = ""
        self.isGet = False
        self.isRegFB = False
        self.isRegLZD = False
        self.deviceName = deviceName
        self.status = ""
        self.versionAppLZD = versionAppLZD
        self.twoFA= ""
        self.code2FA = ""
        
        self.phoneNumber = ""
        self.otpFB = ""
        self.last_name = ""
        self.first_name = ""
        self.address = ""
        
        #uiautomator
        self.d = ""
        
        #mutex
        self.mutex = QMutex()
        self.proxy = ""
        
    def getProxy(self):
        
        fileProxy = open("./Config/listProxy.txt", "r")
        allProxy = fileProxy.readlines()

        proxy = allProxy[0]
        del allProxy[0]

        
        self.proxy = proxy

        newFileProxy = open("./Config/listProxy.txt", "w+")

        for proxy in allProxy:
            newFileProxy.write(proxy)

        newFileProxy.close()    

    def buyHotMailMaxClone(self):
        listType = ["AU","AT", "BE", "BR","CZ","CL","DK","FR","GR","DE","HU","IN","ID","IE","IL","JP","KR","LV","PT","SG","SK","ES","TH"]
        listVip = ["ES","JP","FR","ES","ID","BR"]
        randomIndex = random.randrange(0,len(listType)-1)
        urlBuyHotMail = "http://api.maxclone.vn/api/portal/buyaccount?key=3ba2190bb4d44b8381f484670620c2276c39d1fe7a974cf88719752b0a5b4d5b&type=OUTLOOKDOMAIN&quantity=1"
        
        response = requests.get(urlBuyHotMail)
        jsonData = response.json()
        self.mail = jsonData["Data"][0]["Username"]
        self.passMail = jsonData["Data"][0]["Password"]
        print("Mail moi mua " + listType[randomIndex] + " --- "+ str(self.deviceName) + " : " + self.mail + "|" + self.passMail)
        
    def getOTPHotMailFacebook(self):
        print("Get OTP Api")
        url = "https://fbvip.org/api/ordercode.php?apiKey=b067a1a04de0947856c044f493b3ca1c&type=1&user="+self.mail+"&pass="+self.passMail
        print(url)
        response = requests.get(url)
        jsonData = response.json()
        
        if (jsonData["success"] == 1):
            self.idAPIMail = jsonData["id"]
        time.sleep(7)    
        # doc mail
        urlAPIDocMail = "https://fbvip.org/api/getcode.php?apiKey=b067a1a04de0947856c044f493b3ca1c&id=" + str(self.idAPIMail)
        print(urlAPIDocMail)
        respOTPCode = requests.get(urlAPIDocMail)
        jsonDataOTPCode = respOTPCode.json()
        
        if (jsonDataOTPCode["code"] != ""):
            self.otpFB = jsonDataOTPCode["code"]
            print("OTP Code -- " + str(self.deviceName) + " : "+self.otpFB)
        else:
            dem = 0
            while (dem <= 10):
                time.sleep(5)
                self.idAPIMail1 = ""
                url = "https://fbvip.org/api/ordercode.php?apiKey=b067a1a04de0947856c044f493b3ca1c&type=1&user="+self.mail+"&pass="+self.passMail
                print(url)
                response = requests.get(url)
                jsonData = response.json()
                
                
                if (jsonData["success"] == 1):
                    self.idAPIMail1 = jsonData["id"]
                time.sleep(7)
                urlAPIDocMail1 = "https://fbvip.org/api/getcode.php?apiKey=b067a1a04de0947856c044f493b3ca1c&id=" + str(self.idAPIMail1)
                print(urlAPIDocMail)
                respOTPCode = requests.get(urlAPIDocMail1)
                jsonDataOTPCode = respOTPCode.json()
                print(jsonDataOTPCode)
                
                if (jsonDataOTPCode["code"] != ""):
                    self.otpFB = jsonDataOTPCode["code"]
                    print("OTP Code: "+self.otpFB)
                    break
                print("Cho 2s de get otp")
                dem = dem + 1


    def goCaiDatAPK(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Đang gỡ app Facebook và LZD.........",
        }
        self.signals.result.emit(result)

        device = getDevice(self.deviceName)
        print(device)
        unistallFacebook = device.uninstall("com.facebook.katana")
        unistallLazada = device.uninstall("com.lazada.android")
        
        # unistallCollaseProxy = device.uninstall("com.cell47.College_Proxy")
        if (unistallFacebook == True and unistallLazada == True):
            result["status"] = "Đã gỡ cài đặt Facebook và Lazada"
            self.signals.result.emit(result)

    def caiDatFileAPK(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Đang cài Facebook và LZD.........",
        }
        self.signals.result.emit(result)

        device = getDevice(self.deviceName)
        print(device)
        #installFacebook = device.install("./APK/facebook.apk")
        cmdInstallFB = "adb -s " + self.deviceName + " install -r " + "./APK/facebook.apk"
        os.system(cmdInstallFB)
        time.sleep(1)
        
        # cmdInstallProxyV6 = "adb -s " + self.deviceName + " install -r " + "./APK/proxyv6.apk"
        # os.system(cmdInstallProxyV6)
        # time.sleep(1)
        
        print( self.versionAppLZD)
        
        fileLZD = "./APK/" + self.versionAppLZD
        #fileLZD = "./APK/lazada_6801.apk"
        cmdInstallLZD = "adb -s " + self.deviceName + " install -r " + fileLZD
        os.system(cmdInstallLZD)
        
        
        result["status"] = "Đã cài đặt xong LZD Và Facebook APK"
        self.signals.result.emit(result)
        
    def goVaCaiAppLZD(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Đang gỡ app LZD.........",
        }
        self.signals.result.emit(result)

        device = getDevice(self.deviceName)
        
        unistallLazada = device.uninstall("com.lazada.android")
        
        if (unistallLazada == True):
            result["status"] = "Đã gỡ cài đặt Lazada"
            self.signals.result.emit(result)
            device.shell("settings put system screen_off_timeout 1800000")

            device.shell("settings put global airplane_mode_on 1")
            device.shell("am broadcast -a android.intent.action.AIRPLANE_MODE")

            result["status"] = "Chờ 3s"
            self.signals.result.emit(result)
            time.sleep(3)

            # turn off may bay
            result["status"] = "Tắt máy bay"
            self.signals.result.emit(result)
            print("Tắt máy bay")
            device.shell("settings put global airplane_mode_on 0")
            device.shell("am broadcast -a android.intent.action.AIRPLANE_MODE")

            result["status"] = "Chờ 4s"
            self.signals.result.emit(result)
            print("Chờ 4s")
            time.sleep(2)
            
        result["status"] =  self.versionAppLZD
        self.signals.result.emit(result)
        
        fileLZD = "./APK/" + self.versionAppLZD
        
        #cmdInstallLZD = "adb -s " + self.deviceName + " install -d " + fileLZD
        #os.system(cmdInstallLZD)
        installLazada = device.install(fileLZD)
        
        
        
        result["status"] = "Đã cài đặt xong LZD Và Facebook APK"
        self.signals.result.emit(result)
    
    def moAppLZD(self):
        # uiautomator init
        result = {
            "serialNumber": self.deviceName,
            "status": "Mở App Lazada.........",
        }
        self.signals.result.emit(result)
        
        self.d = u2.connect(self.deviceName)

        self.d.app_start("com.lazada.android", use_monkey=True)

        # click bo qua
        find_boQua = self.d(resourceId="com.lazada.android:id/intro_skip_btn")
        self.d.implicitly_wait(2)
        if (find_boQua.wait(2)):
            result["status"] = "Click bỏ qua"
            self.signals.result.emit(result)

            find_boQua.click()
            time.sleep(1)
        else:
            self.d.implicitly_wait(1)
            find_ViewFullScreen = self.d(resourceId="android:id/immersive_cling_description")
            if (find_ViewFullScreen.wait(1)):
                result["status"] = "Click Got It"
                self.signals.result.emit(result)
                
                find_GotIt = self.d(resourceId="android:id/ok")
                if (find_GotIt.wait(1)):
                    find_GotIt.click()
                else:
                    self.d.click(0.765,0.28)

            time.sleep(1)
            find_BoQuaNew = self.d(resourceId="com.lazada.android:id/welcome_skip_btn")
            if (find_BoQuaNew.wait(1)):
                result["status"] = "Click bỏ qua"
                self.signals.result.emit(result)

                find_BoQuaNew.click()
                time.sleep(1)
        
        result["status"] = "[Xong] !!!"
        self.signals.result.emit(result)
    
    def goVaCaiApp(self):
        self.d = u2.connect(self.deviceName)
        
        self.goVaCaiAppLZD()
        
        #self.fakeDevice()
        self.moAppLZD()
        
    def clickTatHopQua(self):
        self.d = u2.connect(self.deviceName)
        self.d.click(0.497, 0.637)
    

               
    def doiIP4G(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "",
        }
        device = getDevice(self.deviceName)

        # turn on may bay
        result["status"] = "Bật máy bay"
        self.signals.result.emit(result)
        
        device.shell("settings put system screen_off_timeout 1800000")

        device.shell("settings put global airplane_mode_on 1")
        device.shell("am broadcast -a android.intent.action.AIRPLANE_MODE")

        result["status"] = "Chờ 3s"
        self.signals.result.emit(result)
        time.sleep(3)

        # turn off may bay
        result["status"] = "Tắt máy bay"
        self.signals.result.emit(result)
        print("Tắt máy bay")
        device.shell("settings put global airplane_mode_on 0")
        device.shell("am broadcast -a android.intent.action.AIRPLANE_MODE")

        result["status"] = "Chờ 4s"
        self.signals.result.emit(result)
        print("Chờ 4s")
        time.sleep(4)

        result["status"] = "Đã đổi ip xong"
        self.signals.result.emit(result)

    def wipeSachMay(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "",
        }
        
        newDevice = getDevice(self.deviceName)
        # vao che do fastboot
        resultCommand = newDevice.shell("reboot fastboot")
        time.sleep(2)

        result["status"] = "Vào chế độ Fastboot"
        self.signals.result.emit(result)
        
        try:
            cmdWipe = "fastboot -s " + self.deviceName + " -w"
            os.system(cmdWipe)
            time.sleep(4)
            result["status"] = "Wipe Cache và Wipe Userdata"
            self.signals.result.emit(result)
            print("Wipe Cache và Wipe Userdata")
        except:
            cmdWipe = "fastboot -s " + self.deviceName + " -w"
            os.system(cmdWipe)
            time.sleep(4)
            result["status"] = "Wipe Cache và Wipe Userdata Lần 2"
            self.signals.result.emit(result)
            print("Wipe Cache và Wipe Userdata")
        
        try:
            # reboot
            cmdReboot = "fastboot -s " + self.deviceName + " reboot"
            os.system(cmdReboot)
            print("Reboot......")
            result["status"] = "Rebooting...... Wait"
            self.signals.result.emit(result)
            time.sleep(35)
        except:
            # reboot
            cmdReboot = "fastboot -s " + self.deviceName + " reboot"
            os.system(cmdReboot)
            print("Reboot......")
            result["status"] = "Rebooting...... Wait"
            self.signals.result.emit(result)
            time.sleep(35)
        

        checkHomeScreen = newDevice.shell(
            "getprop sys.boot_completed | tr -d '\r'")

        i = 1
        while (checkHomeScreen != "1\n"):
            time.sleep(1)
            print("Wipe Recovery ... " + str(i))
            result["status"] = "Wipe Recovery ... " + str(i)
            self.signals.result.emit(result)
            i = i + 1
            checkHomeScreen = newDevice.shell(
                "getprop sys.boot_completed | tr -d '\r'")

        if (checkHomeScreen == "1\n"):
            
            print("Wipe Done...")
            result["status"] = "Đã Wipe Sạch Máy"
            self.signals.result.emit(result)
            # set timeout display 30 minitues
            newDevice.shell("settings put system screen_off_timeout 1800000")
            time.sleep(1)
            newDevice.shell("settings put system accelerometer_rotation 0")
            
            try:
                cmdInitAutomator = "python -m uiautomator2 init"
                os.system(cmdInitAutomator)
                time.sleep(1)
                
                result["status"] = "Khoi tao UI Automator2"
                self.signals.result.emit(result)
                print("Khoi tao UI Automator")
                self.d = u2.connect(self.deviceName)
                time.sleep(6)
            except:
                print("Khoi tao UI Automator Lan 2")
                self.d = u2.connect(self.deviceName)
                time.sleep(6)
            
            result["status"] = "Wipe Xong !!!"
            self.signals.result.emit(result)

    def getDuLieuCSV(self):
           # #pass LZD
           # passLZD = self.lineEdit_DefaultPassLZD.text()

           # #list App LZD
           # listFileAPKLZD = os.listdir('./APK/')
           # listFileAPKLZD.pop(0)

        df = pandas.read_csv("./Config/napDuLieu.csv", skipinitialspace=True,
                             keep_default_na=False, encoding='utf-8-sig')
        row_count, column_count = df.shape

        dataResult = {
            "LZD": "",
            "passLZD": "",
            "uid": "",
            "passFB": "",
            "mail": "",
            "passMail": "",
            "isRegFB": "",
            "isRegLZD": "",
            "isGet": "",
            "deviceName": "",
            "status": "",
            "versionAppLZD": "",
            "twoFA": ""
        }

        for i in range(row_count):

            splitFacebook = df["Facebook"][i].split('|')
            splitMail = df["Mail"][i].split('|')
            twoFA = ""
            
            uid = splitFacebook[0]
            passFB = splitFacebook[1]
            if (len(splitFacebook) > 2):
                twoFA = splitFacebook[2]
            mail = splitMail[0]
            passMail = splitMail[1]
            deviceName = df["deviceName"][i]
            isGet = df["isGet"][i]

            isRegFB = df["isRegFB"][i]
            isRegLZD = df["isRegLZD"][i]
            status = df["status"][i]

            if (isGet == "" and isRegFB == ""):
                self.LZD = mail
                self.uid = uid
                self.passFB = passFB
                if (twoFA != ""):
                    self.twoFA = twoFA
                self.mail = mail
                self.passMail = passMail
                self.isGet = True
                self.isRegFB = False
                self.isRegLZD = False
                self.status = "da lay du lieu"

                break

        self.updateDataCSV()      

    def updateDataCSV(self):
        df = pandas.read_csv("./Config/napDuLieu.csv", skipinitialspace=True,
                             keep_default_na=False, encoding='utf-8')
        row_count, column_count = df.shape
        print(self.mail)
        for i in range(row_count):

            splitFacebook = df["Facebook"][i].split('|')
            splitMail = df["Mail"][i].split('|')

            uid = splitFacebook[0]
            mail = splitMail[0]
            
            
            if (mail == self.mail):
                
                if (self.LZD != ''):
                    df["LZD"][i] = self.LZD

                if (self.passLZD != ''):
                    df["passLZD"][i] = self.passLZD

                df["deviceName"][i] = self.deviceName
                df["isGet"][i] = self.isGet
                df["isRegFB"][i] = self.isRegFB
                df["isRegLZD"][i] = self.isRegLZD
                df["status"][i] = self.status
                df["versionAppLZD"][i] = self.versionAppLZD
                

        df.to_csv("./Config/napDuLieu.csv", index=False, encoding='utf-8')

    def getLaiDuLieuCSV(self):

        df = pandas.read_csv("./Config/napDuLieu.csv", skipinitialspace=True,
                             keep_default_na=False, encoding='utf-8-sig')
        row_count, column_count = df.shape

        dataResult = {
            "LZD": "",
            "passLZD": "",
            "uid": "",
            "passFB": "",
            "mail": "",
            "passMail": "",
            "isRegFB": "",
            "isRegLZD": "",
            "isGet": "",
            "deviceName": "",
            "status": "",
            'versionAppLZD': "",
            "twoFA": "",
        }

        arrayData = []

        for i in range(row_count):

            splitFacebook = df["Facebook"][i].split('|')
            splitMail = df["Mail"][i].split('|')
            twoFA = ""
            
            uid = splitFacebook[0]
            passFB = splitFacebook[1]
            if (len(splitFacebook) > 2):
                twoFA = splitFacebook[2]
            mail = splitMail[0]
            passMail = splitMail[1]
            deviceName = df["deviceName"][i]
            isGet = df["isGet"][i]
            

            LZD = df["LZD"][i]
            passLZD = df["passLZD"][i]
            deviceName = df["deviceName"][i]
           
            
            isRegFB = df["isRegFB"][i]
            isRegLZD = df["isRegLZD"][i]
            status = df["status"][i]
            versionAppLZD = df["versionAppLZD"][i]

            if ( deviceName == self.deviceName):
                dataResult['LZD'] = LZD
                dataResult['passLZD'] = passLZD
                dataResult['uid'] = uid
                dataResult['passFB'] = passFB
                if (twoFA != ""):
                    dataResult['twoFA'] = twoFA
                dataResult['mail'] = mail
                dataResult['passMail'] = passMail
                dataResult['isGet'] = True
                dataResult['isRegFB'] = False
                dataResult['isRegLZD'] = False
                dataResult['deviceName'] = deviceName
                dataResult['status'] = status
                dataResult['versionAppLZD'] = versionAppLZD
                print(dataResult)

                arrayData.append(dataResult)
        print(arrayData)
        dataFinal = arrayData[len(arrayData)-1]
        # set data
        self.LZD = dataFinal["LZD"]
        self.passLZD = dataFinal["passLZD"]
        self.uid = dataFinal["uid"]
        self.passFB = dataFinal["passFB"]
        self.twoFA = dataResult['twoFA']
        self.mail = dataFinal["mail"]
        self.passMail = dataFinal["passMail"]
        self.isGet = dataFinal["isGet"]
        self.isRegFB = dataFinal["isRegFB"]
        self.isRegLZD = dataFinal["isRegLZD"]
        self.deviceName = dataFinal["deviceName"]
        self.status = dataFinal["status"]
        self.versionAppLZD = dataFinal["versionAppLZD"]

    def addAccountVaoServer(self):
        dataPost = {
            'isLoginFB': self.isRegFB,
            'isRegLZD': self.isRegLZD,
            'deviceName': self.deviceName,
            'owner': "admin",
            'mail': self.mail,
            'username': self.mail,
            'passwordLZD': self.passLZD,
            'passMail': self.passMail,
            'status': self.status
        }
        # create response
        response = requests.post(
            'http://lzd420.me/API/addAccountLZD', dataPost)
        jsonData = response.json()
        if (jsonData["success"] == True):
            print("Đã cập nhật data acc vào server")
    def luuAccVaoFile(self,fileName,data):
        df = pd.DataFrame(data)
        print(df)
        df.to_csv("./Config/" + fileName, encoding='utf-8-sig', mode='a', index = False, header=False)

    def getCode2Fa(self):
        url = "http://2fa.live/tok/" + self.twoFA
        result = requests.get(url)
        jsonData = result.json()
        
        if (jsonData != ""):
            self.code2FA = jsonData["token"]

    def dangNhapFacebook(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện quy trình đăng nhập facebook",
        }
        self.signals.result.emit(result)
        # init
        # device = getDevice(self.deviceName)
        # dataAccount = DataAccountModel.DataAccount(serialNumber)
        # dataAccount.getData()

        if (self.mail == ""):
            self.getLaiDuLieuCSV()
            
        time.sleep(1)

        # uiautomator init
        self.d = u2.connect(self.deviceName)
        time.sleep(2)
        self.d.unlock()
        time.sleep(1)
        
        result["status"] = "Mở App Facebook -"
        self.signals.result.emit(result)

        self.d.app_start("com.facebook.katana", use_monkey=True)

        # input uid
        self.d.implicitly_wait(10.0)
        find_inputUID = self.d(text="Phone or email")
        if (find_inputUID.wait(5)):
            time.sleep(1)
            find_inputUID.click()
            result["status"] = "FB - Input UID: " + self.uid
            self.signals.result.emit(result)
            time.sleep(1)
            self.d.send_keys(self.uid)
            time.sleep(1)
        else:
            result["status"] = "Fail - Test Lai"
            self.signals.result.emit(result)

        # input password
        find_inputPassword = self.d(text="Password")
        if (find_inputPassword.wait(5)):
            find_inputPassword.click()
            result["status"] = "FB - Input Pass: " + self.passFB
            self.signals.result.emit(result)
            time.sleep(1)
            self.d.send_keys(self.passFB)
            time.sleep(1)
        else:
            print("Fail")

        # click DangNhap
        find_DangNhap = self.d(description="Log In",
                          className="android.view.ViewGroup")
        if (find_DangNhap.wait(5)):
            find_DangNhap.click()
            result["status"] = "Click Đăng Nhập"
            self.signals.result.emit(result)
            time.sleep(5)
        else:
            print("Fail")
            
        if (self.twoFA != ""):
            self.d.implicitly_wait(5)
            find_LoginCodeRequired = self.d(text="Login Code Required")
            if (find_LoginCodeRequired.wait(5)):
                result["status"] = "Acc 2FA"
                self.signals.result.emit(result)
                find_OK = self.d(text= "OK")
                if (find_OK.wait(5)):
                    find_OK.click()
                    time.sleep(2)
                    
                    find_LoginCode = self.d(text="Login Code")
                    if (find_LoginCode.wait(5)):
                        result["status"] = "Lấy Code 2FA"
                        self.signals.result.emit(result)
                        #get token 2fa
                        self.getCode2Fa()
                        time.sleep(1)
                        result["status"] = "Code 2FA: " + self.code2FA
                        self.signals.result.emit(result)
                        
                        find_LoginCode.click()
                        time.sleep(1)
                        
                        self.d.send_keys(self.code2FA)
                        time.sleep(1)
                        
                        find_Continue = self.d(description="Continue")
                        if (find_Continue.wait(5)):
                            result["status"] = "Click continue"
                            self.signals.result.emit(result)
                            
                            find_Continue.click()
                            time.sleep(3)
            

        # Skip
        self.d.implicitly_wait(3)
        find_Skip = self.d.xpath(
            '//android.view.ViewGroup/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').wait(3)
        if (find_Skip != None):
            print("Click bo qua")
            result["status"] = "Click Bỏ Qua"
            self.signals.result.emit(result)
            find_Skip.click()

            time.sleep(1)

        # Skip 2
        self.d.implicitly_wait(2)
        find_Skip2 = self.d.xpath(
            '//android.view.ViewGroup/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').wait(2)
        if (find_Skip2 != None):
            result["status"] = "Click Skip"
            self.signals.result.emit(result)
            find_Skip2.click()
            time.sleep(1)
        else:
            find_Skip22 = self.d.xpath(
                '//*[@resource-id="android:id/content"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.view.ViewGroup[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').wait(2)
            if (find_Skip22 != None):
                result["status"] = "Click Skip 22"
                self.signals.result.emit(result)
                find_Skip22.click()
                time.sleep(1)

        # click Skip3
        self.d.implicitly_wait(2)
        find_Skip3 = self.d(text="SKIP")
        if (find_Skip3.wait(2)):
            result["status"] = "Click Skip 3"
            self.signals.result.emit(result)
            find_Skip3.click()
            time.sleep(2)
        else:
            print("Fail")

        # click NotNow
        fint_NotNow = self.d(text="Not Now")
        if (fint_NotNow.wait(5)):
            result["status"] = "Click Not Now"
            self.signals.result.emit(result)
            fint_NotNow.click()
            time.sleep(2)
        else:
            find_Skip4 = self.d.xpath(
                '//android.view.ViewGroup/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').wait(3)
            if (find_Skip4 != None):
                find_Skip4.click()
                time.sleep(1)

        # find deny
        find_Deny = self.d(description="Deny")
        if (find_Deny.wait(5)):
            result["status"] = "Click Deny"
            self.signals.result.emit(result)
            find_Deny.click()
            time.sleep(1)

        # check Login Done
        find_CheckLogin = self.d.xpath(
            '//android.widget.FrameLayout[2]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.ImageView[1]').wait(3)
        if (find_CheckLogin != None):
            result["status"] = "Đăng nhập Facebook Thành Công"
            self.signals.result.emit(result)

        self.isRegFB = True
        self.updateDataCSV()

    def dangNhapLZD(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện quy trình Lazada",
        }
        self.signals.result.emit(result)
        # init
        device = getDevice(self.deviceName)
        if (self.mail == ""):
            self.getLaiDuLieuCSV()

        # uiautomator init
        self.d = u2.connect(self.deviceName)

        result["status"] = "Mở App Lazada"
        self.signals.result.emit(result)

        self.d.app_start("com.lazada.android", use_monkey=True)

        # click bo qua
        find_boQua = self.d(resourceId="com.lazada.android:id/intro_skip_btn")
        self.d.implicitly_wait(4)
        if (find_boQua.wait(3)):
            result["status"] = "Click bỏ qua"
            self.signals.result.emit(result)

            find_boQua.click()
            time.sleep(0.5)
        else:
            self.d.implicitly_wait(1)
            find_BoQuaNew = self.d(resourceId="com.lazada.android:id/welcome_skip_btn")
            if (find_BoQuaNew.wait(1)):
                result["status"] = "Click bỏ qua"
                self.signals.result.emit(result)

                find_BoQuaNew.click()
                time.sleep(1)

        
        self.moLinkMGG()
        time.sleep(2)
        
        #find Dang Nhap
        #self.d.click(0.279, 0.658)
        #time.sleep(2)
        self.d.implicitly_wait(5)
        find_ThuThapFreeShip = self.d.xpath('//*[@resource-id="4208652060"]/android.view.View[1]/android.view.View[2]/android.view.View[1]/android.view.View[1]/android.view.View[2]/android.view.View[2]/android.view.View[1]').wait(5)
        if (find_ThuThapFreeShip != None):
            result["status"] = "Click Thu Thập Mã Freeship"
            self.signals.result.emit(result)
            
            find_ThuThapFreeShip.click()
            time.sleep(1)
        
        # self.d.implicitly_wait(10)
        # find_dangNhap = self.d(text="Đăng Nhập")
        # if (find_dangNhap.wait(10)):
        #     result["status"] = "Click Đăng Nhập"
        #     self.signals.result.emit(result)
        #     time.sleep(1)
        #     find_dangNhap.click()
        #     time.sleep(1)

        # click icon FB
        find_iconFB = self.d(resourceId="com.lazada.android:id/iv_facebook")
        if (find_iconFB.wait(5)):
            result["status"] = "Click icon facebook"
            self.signals.result.emit(result)
            time.sleep(1)
            find_iconFB.click()
            time.sleep(2)

            # click dong y
            find_dongY = self.d(resourceId="com.lazada.android:id/tv_agree")
            if (find_dongY.wait(5)):
                result["status"] = "Click đồng ý"
                self.signals.result.emit(result)
                find_dongY.click()
                time.sleep(2)

            # find editInfo
            find_editInfo = self.d(text="Edit the info you provide")
            if (find_editInfo.wait(5)):
                result["status"] = "Click edit"
                self.signals.result.emit(result)
                find_editInfo.click()
                time.sleep(3)

            # tat mail
            find_tatMail = self.d.xpath(
                '//androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[3]/android.widget.FrameLayout[1]').wait(5)
            if (find_tatMail != None):
                result["status"] = "Click tắt mail"
                self.signals.result.emit(result)

                find_tatMail.click()
                time.sleep(3)

            # click button continue
            find_btnContinue = self.d.xpath(
                '//androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[4]/android.widget.Button[1]').wait(5)
            if (find_btnContinue != None):
                result["status"] = "Click continue ...."
                self.signals.result.emit(result)
                find_btnContinue.click()
                time.sleep(10)

            # click dien sau
            find_dienSau = self.d.xpath(
                '//android.webkit.WebView/android.view.View[1]/android.view.View[2]/android.view.View[1]').wait(20)
            if (find_dienSau != None):
                result["status"] = "Click điền sau....."
                self.signals.result.emit(result)
                find_dienSau.click()
                time.sleep(2)

        else:
            find_iconFB = self.d(
                resourceId="com.lazada.android:id/icf_login_app_auth_facebook")
            if (find_iconFB.wait(5)):
                result["status"] = "Click icon facebook"
                self.signals.result.emit(result)
                find_iconFB.click()
                time.sleep(2)
                # click dong y
            find_dongY = self.d(resourceId="android:id/button1")
            if (find_dongY.wait(5)):
                result["status"] = "Click đồng ý"
                self.signals.result.emit(result)
                find_dongY.click()
                time.sleep(2)

            # find editInfo
            find_editInfo = self.d(text="Edit the info you provide")
            if (find_editInfo.wait(5)):
                result["status"] = "Click edit"
                self.signals.result.emit(result)
                find_editInfo.click()
                time.sleep(3)
            # tat mail
            find_tatMail = self.d.xpath(
                '//androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[3]/android.widget.FrameLayout[1]').wait(5)
            if (find_tatMail != None):
                result["status"] = "Click tắt mail"
                self.signals.result.emit(result)
                find_tatMail.click()
                time.sleep(3)

            # click button continue
            find_btnContinue = self.d.xpath(
                '//androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[4]/android.widget.Button[1]').wait(5)
            if (find_btnContinue != None):
                result["status"] = "Click continue ...."
                self.signals.result.emit(result)
                find_btnContinue.click()
                time.sleep(10)
                result["status"] = "Chờ 10 giây...."
                self.signals.result.emit(result)
                find_btnContinue.click()

            # click dien sau
            find_dienSau = self.d(text="Điền Sau")
            if (find_dienSau.wait(5)):
                result["status"] = "Click điền sau....."
                self.signals.result.emit(result)
                find_dienSau.click()
                time.sleep(2)

    def napAcc(self): 
        linkAPI = "http://lzd420.me/api/getKhoDatHang&deviceName=" + self.deviceName  + "&owner=admin"
        response = requests.get(linkAPI)
        jsonData = response.json()
        if (jsonData["status"] == 'success'):
        
            dataAcc = jsonData["data"]
            
            dataPost = {
                "username": dataAcc["username"],
                "password": dataAcc["password"],
                "phoneNumber":dataAcc["phoneNumber"],
                "deviceName":dataAcc["deviceName"],
                "address":dataAcc["address"],
                "link":"",
                "owner":"admin"
            }
            
            print(dataPost)
            response = requests.post("http://lzd420.me/API/setinfo", dataPost)
            print(response.json())
            
            result = {
            "serialNumber": self.deviceName,
            "status": "Nạp Acc Thành Công",
            }
            self.signals.result.emit(result)
            
        elif (jsonData["status"] == 'fail'):
            
            result = {
            "serialNumber": self.deviceName,
            "status": "Đã Hết Acc Trong Kho",
            }
            self.signals.result.emit(result)

    def getDataAcc(self):
        linkAPI = "http://lzd420.me/api/getinfo&deviceName=" + self.deviceName  + "&owner=admin"
        response = requests.get(linkAPI)
        jsonData = response.json()
        if (jsonData["status"] == 'success'):
        
            dataAcc = jsonData["data"]
            self.LZD = dataAcc["username"]
            self.passLZD = dataAcc["password"]
            self.full_name = dataAcc["fullName"]
            self.phoneNumber = dataAcc["phoneNumber"]
            self.address = dataAcc["address"]
            
            time.sleep(0.5)
            print(self.LZD)
            
            result = {
            "serialNumber": self.deviceName,
            "status": "Đã Lấy Được Dữ Liệu: " + self.LZD,
            }
            self.signals.result.emit(result)

    def dangNhapLZDBangMatKhau(self, isInstallApp):
        # uiautomator init
        self.d = u2.connect(self.deviceName)
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện quy trình Lazada - Bằng Mật Khẩu",
        }
        self.signals.result.emit(result)
        # nap app
        self.napAcc()
        
        if (isInstallApp == True):
            self.caiDatFileAPK()
            self.doiIP4G()
            time.sleep(1)
        
            result["status"] = "Mở App Lazada"
            self.signals.result.emit(result)

            self.d.app_start("com.lazada.android", use_monkey=True)

            # click bo qua
            find_boQua = self.d(resourceId="com.lazada.android:id/intro_skip_btn")
            self.d.implicitly_wait(2)
            if (find_boQua.wait(2)):
                result["status"] = "Click bỏ qua"
                self.signals.result.emit(result)

                find_boQua.click()
                
            else:
                self.d.implicitly_wait(1)
                find_BoQuaNew = self.d(resourceId="com.lazada.android:id/welcome_skip_btn")
                if (find_BoQuaNew.wait(1)):
                    result["status"] = "Click bỏ qua"
                    self.signals.result.emit(result)

                    find_BoQuaNew.click()
                    
            #tat hop qua thu thap
            self.d.implicitly_wait(1)
            find_TatHopQuaThuThap = self.d(text="O1CN01wDnGi51lWoUAxpKMR_!!6000000004827-2-tps-32-33")
            if (find_TatHopQuaThuThap.wait(1)):
                find_TatHopQuaThuThap.click()
                time.sleep(1)
            
            #tat hop qua bat ngo
            self.d.implicitly_wait(1)
            find_TatHopQuaBatNgo = self.d(resourceId="com.lazada.android:id/close_button")
            if (find_TatHopQuaBatNgo.wait(1)):
                find_TatHopQuaBatNgo.click()
                time.sleep(1)
            
            self.d.implicitly_wait(2)
            find_DangNhapNgay = self.d(resourceId="com.lazada.android:id/hp_login_button")
            if (find_DangNhapNgay.wait(2)):
                find_DangNhapNgay.click()
                time.sleep(1)
        else:
            print("OK")
            
        #get acc
        self.getDataAcc()
        #dang nhap tai khoan
        self.d.implicitly_wait(8)
        find_DangNhapTaiKhoan = self.d(resourceId="com.lazada.android:id/tv_signin")
        if (find_DangNhapTaiKhoan.wait(8)):
            result["status"] = "Click Đăng Nhập Tài Khoản"
            self.signals.result.emit(result)
            
            find_DangNhapTaiKhoan.click()
            time.sleep(1)
            
            #input tai khoan
            self.d.implicitly_wait(5)
            find_InputUsername = self.d(text="Số điện thoại/Email")
            if (find_InputUsername.wait(5)):
                result["status"] = "Tài khoản: " + self.LZD
                self.signals.result.emit(result)
                
                find_InputUsername.click()
                time.sleep(0.5)
                
                self.d.send_keys(self.LZD)
                time.sleep(1)
                
                #input password
                self.d.implicitly_wait(5)
                find_Password = self.d(text="Mật khẩu")
                if (find_Password.wait(5)):
                    result["status"] = "Mật Khẩu: " + self.passLZD
                    self.signals.result.emit(result)
                    
                    find_Password.click()
                    time.sleep(1)
                    
                    self.d.send_keys(self.passLZD)
                    time.sleep(1)
                    
                    #click dang nhap
                    self.d.implicitly_wait(5)
                    find_DangNhap = self.d(resourceId="com.lazada.android:id/btn_next")
                    if (find_DangNhap.wait(5)):
                        result["status"] = "Click Đăng Nhập"
                        self.signals.result.emit(result)
                        
                        find_DangNhap.click()
                        time.sleep(1)
        
        result["status"] = "Kết Thúc Đăng Nhập LZD"
        self.signals.result.emit(result)                
    
    
    def dangNhapLai(self):
        # uiautomator init
        self.d = u2.connect(self.deviceName)
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện quy trình Lazada - Bằng Mật Khẩu",
        }
        self.signals.result.emit(result)
        
        self.getDataAcc()
        #dang nhap tai khoan
        self.d.implicitly_wait(8)
        find_DangNhapTaiKhoan = self.d(resourceId="com.lazada.android:id/tv_signin")
        if (find_DangNhapTaiKhoan.wait(8)):
            result["status"] = "Click Đăng Nhập Tài Khoản"
            self.signals.result.emit(result)
            
            find_DangNhapTaiKhoan.click()
            time.sleep(1)
            
            #input tai khoan
            self.d.implicitly_wait(5)
            find_InputUsername = self.d(text="Số điện thoại/Email")
            if (find_InputUsername.wait(5)):
                result["status"] = "Tài khoản: " + self.LZD
                self.signals.result.emit(result)
                
                find_InputUsername.click()
                time.sleep(0.5)
                
                self.d.send_keys(self.LZD)
                time.sleep(1)
                
                #input password
                self.d.implicitly_wait(5)
                find_Password = self.d(text="Mật khẩu")
                if (find_Password.wait(5)):
                    result["status"] = "Mật Khẩu: " + self.passLZD
                    self.signals.result.emit(result)
                    
                    find_Password.click()
                    time.sleep(1)
                    
                    self.d.send_keys(self.passLZD)
                    time.sleep(2)
                    
                    #click dang nhap
                    self.d.implicitly_wait(5)
                    find_DangNhap = self.d(resourceId="com.lazada.android:id/btn_next")
                    if (find_DangNhap.wait(5)):
                        result["status"] = "Click Đăng Nhập"
                        self.signals.result.emit(result)
                        
                        find_DangNhap.click()
                        time.sleep(1)
        
        result["status"] = "Kết Thúc Đăng Nhập LZD"
        self.signals.result.emit(result)     
        
    def moLinkMGG(self):
        
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện Mở Link MGG",
        }
        self.signals.result.emit(result)

        d = u2.connect(self.deviceName)
        newDevice = getDevice(self.deviceName)

        link = "https://pages.lazada.vn/wow/gcp/route/lazada/vn/upr_1000345_lazada/channel/vn/upr-router/vn?spm=a2o4n.home.feature_nav.2.19056afe9EOzcJ&hybrid=1&data_prefetch=true&wh_pid=/lazada/channel/vn/voucher/claimvoucher&scm=1003.4.icms-zebra-5000379-2586391.OTHER_6042140477_7211275"
        shellCMD = "am start -a android.intent.action.VIEW -d '" + link + "'"

        # shell Link
        resultShell = newDevice.shell(shellCMD)
        time.sleep(1)
        result["status"] = "Đang vào link"
        self.signals.result.emit(result)

        d.implicitly_wait(5)
        find_Lazada = d(resourceId="android:id/text1", text="Lazada")
        if (find_Lazada.wait(5)):
            result["status"] = "Click icon LZD"
            self.signals.result.emit(result)
            find_Lazada.click()
            time.sleep(1)

            find_JustOnce = d(resourceId="android:id/button_once")
            if (find_JustOnce.wait(5)):
                result["status"] = "Click Just Once"
                self.signals.result.emit(result)

                print("Click Just Once")
                find_JustOnce.click()
                time.sleep(2)

        else:
            find_JustOnce = d(resourceId="android:id/button_once")
            if (find_JustOnce.wait(5)):
                result["status"] = "Click Just Once"
                self.signals.result.emit(result)
                find_JustOnce.click()
                time.sleep(2)
    
    def moLinkSanPham(self, duongDan):
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện Mở Link Test",
        }
        self.signals.result.emit(result)

        
        newDevice = getDevice(self.deviceName)

        link = duongDan
        shellCMD = "am start -a android.intent.action.VIEW -d '" + link + "'"

        # shell Link
        resultShell = newDevice.shell(shellCMD)
        time.sleep(1)
        result["status"] = "Đang vào link"
        self.signals.result.emit(result)

        self.d = u2.connect(self.deviceName)
        self.d.implicitly_wait(4)
        find_Lazada = self.d(resourceId="android:id/text1", text="Lazada")
        if (find_Lazada.wait(4)):
            result["status"] = "Click icon LZD"
            self.signals.result.emit(result)
            find_Lazada.click()
            time.sleep(1)

            find_JustOnce = self.d(resourceId="android:id/button_once")
            if (find_JustOnce.wait(5)):
                result["status"] = "Click Just Once"
                self.signals.result.emit(result)

                print("Click Just Once")
                find_JustOnce.click()
                time.sleep(2)

        else:
            self.d.implicitly_wait(2)
            find_JustOnce = self.d(resourceId="android:id/button_once")
            if (find_JustOnce.wait(2)):
                result["status"] = "Click Just Once"
                self.signals.result.emit(result)
                find_JustOnce.click()
                time.sleep(2)

    def addMailLazada(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện Add Mail Lazada",
        }
        self.signals.result.emit(result)
        # init
        device = getDevice(self.deviceName)
        if (self.mail == ""):
            self.getLaiDuLieuCSV()

            # uiautomator init
        self.d = u2.connect(self.deviceName)

         # click 3 dam
        find_dau3Cham = self.d(description="Tùy chọn khác")
        if (find_dau3Cham.wait(3)):
            print("Click dau 3 cham")
            result["status"] = "Click dấu 3 chấm"
            self.signals.result.emit(result)
            find_dau3Cham.click()
            time.sleep(0.5)

        # click tai khoan cua toi
        find_taiKhoanCuaToi = self.d.xpath(
            '//android.widget.ListView/android.widget.LinearLayout[3]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[1]').wait(5)
        if (find_taiKhoanCuaToi != None):
            result["status"] = "Click tài khoản của tôi..."
            self.signals.result.emit(result)
            find_taiKhoanCuaToi.click()
            time.sleep(1)

        # guide Content
        self.d.implicitly_wait(2)
        find_guideContent = self.d(
            resourceId="com.lazada.android:id/btn_guide_content")
        if (find_guideContent.wait(2)):
            result["status"] = "Click OK !!!"
            self.signals.result.emit(result)
            find_guideContent.click()
            time.sleep(0.5)
        else:
            self.d.implicitly_wait(1)
            find_daHieu = self.d(resourceId="com.lazada.android:id/txt_gotit")
            if (find_daHieu.wait(1)):
                result["status"] = "Click Đã Hiểu"
                self.signals.result.emit(result)
                find_daHieu.click()
                time.sleep(0.5)
        # setting
        self.d.implicitly_wait(2)
        find_setting = self.d(resourceId="com.lazada.android:id/iv_settings")
        if (find_setting.wait(2)):
            result["status"] = "Click SETTING"
            self.signals.result.emit(result)
            find_setting.click()
            time.sleep(1)
        else:
            find_settingVer580 = self.d(
                resourceId="com.lazada.android:id/tv_settings")
            if (find_settingVer580.wait(2)):
                result["status"] = "Click Setting Ver 580"
                self.signals.result.emit(result)
                find_settingVer580.click()
                time.sleep(1)
        # thong tin tai khoan
        time.sleep(1)
        find_thongTinTaiKhoan = self.d(
            resourceId="com.lazada.android:id/setting_account_information_container")
        if (find_thongTinTaiKhoan.wait(5)):
            result["status"] = "Click thông tin tài khoản"
            self.signals.result.emit(result)
            find_thongTinTaiKhoan.click()
            time.sleep(1)

        # them email
        self.d.implicitly_wait(5)
        find_themEmail = self.d(description="Thêm email")
        if (find_themEmail.wait(5)):
            result["status"] = "Click thêm mail"
            self.signals.result.emit(result)
            find_themEmail.click()
            time.sleep(1)
        # input mail
        self.d.implicitly_wait(10)
        find_inputMail = self.d.xpath('//android.widget.EditText').wait(10)
        if (find_inputMail != None):
            result["status"] = "Click input mail: " + self.mail
            self.signals.result.emit(result)
            find_inputMail.click()
            time.sleep(1)
            self.d.send_keys(self.mail)
            time.sleep(1)

        # btn gui ma
        self.d.implicitly_wait(5)
        find_guiMa = self.d.xpath('//*[@resource-id="com.lazada.android:id/weex_render_view"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]').wait(5)
        if (find_guiMa != None):
            result["status"] = "Click Gửi Mã"
            self.signals.result.emit(result)
            find_guiMa.click()
            time.sleep(7)
            result["status"] = "API OTP HotMail by HTN"
            self.signals.result.emit(result)
            otpTempLZD = outlook.apiOTPLZD(self.mail, self.passMail)
            
            while (otpTempLZD == ""):
                result["status"] = "Lấy OTP Lần Nữa"
                self.signals.result.emit(result)
                
                otpTempLZD = outlook.apiOTPLZD(self.mail, self.passMail)
                if (otpTempLZD != ""):
                    result["status"] = "Lấy Được OTP: " + otpTempLZD
                    self.signals.result.emit(result)
                    break

            # input otp
            find_inputOTP = self.d.xpath('//*[@resource-id="com.lazada.android:id/weex_render_view"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.EditText[1]')
            if (find_inputOTP.exists):
                find_inputOTP.click()
                result["status"] = "OTP Code mail: " + otpTempLZD
                self.signals.result.emit(result)
                time.sleep(1)
                self.d.send_keys(otpTempLZD)
                time.sleep(1)
                # click them email
                self.d.implicitly_wait(5)
                find_btnThemEmail = self.d(description="Thêm email")
                if (find_btnThemEmail.wait(5)):
                    result["status"] = "Click thêm mail"
                    self.signals.result.emit(result)
                    find_btnThemEmail.click()
                    time.sleep(3)
                    
            # read file json
            f = open('./Config/listName.json', encoding="utf8")
            # load data
            data = json.load(f)
            
            randomIndex = random.randrange(1, len(data))
            self.full_name = data[randomIndex]["full_name"]
            
            result["status"] = "Đổi Tên: " + self.full_name
            self.signals.result.emit(result)
            
            self.d.implicitly_wait(5)
            find_Ten = self.d(description="Tên")
            if (find_Ten.wait(5)):
                find_Ten.click()
                time.sleep(3)
                
                self.d.implicitly_wait(5)
                find_XoaHet = self.d.xpath('//android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').wait(5)
                if (find_XoaHet != None):
                    find_XoaHet.click()
                    time.sleep(1.5)
                    
                    self.d.send_keys(self.full_name)
                    time.sleep(2)
                    
                    self.d.implicitly_wait(5)
                    find_Luu = self.d(description="Lưu")
                    if (find_Luu.wait(5)):
                        find_Luu.click()
                        time.sleep(2)
                
                else:
                    self.d.click(0.479,0.738)
                    time.sleep(1)
                    self.d.clear_text()
                    time.sleep(1)
                    
                    self.d.send_keys(self.full_name)
                    time.sleep(2)
                    
                    self.d.implicitly_wait(5)
                    find_Luu = self.d(description="Lưu")
                    if (find_Luu.wait(5)):
                        find_Luu.click()
                        time.sleep(2)
                    
                    
            
              
                    
            # dau 3 cham
            time.sleep(2)
            find_dau3Cham = self.d(description="Tùy chọn khác")
            if (find_dau3Cham.wait(5)):
                result["status"] = "Click Tùy Chọn Khác"
                self.signals.result.emit(result)
                find_dau3Cham.click()
                time.sleep(1)

            # tai khoan cua toi
            find_taiKhoanCuaToi = self.d.xpath(
                '//android.widget.ListView/android.widget.LinearLayout[3]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[1]').wait(5)
            if (find_taiKhoanCuaToi != None):
                result["status"] = "Click Tài Khoản Của Tôi"
                self.signals.result.emit(result)
                find_taiKhoanCuaToi.click()
                time.sleep(0.5)

            # guide Content
            self.d.implicitly_wait(3)
            find_guideContent = self.d(
                resourceId="com.lazada.android:id/btn_guide_content")
            if (find_guideContent.wait(3)):
                result["status"] = "Click OK"
                self.signals.result.emit(result)
                find_guideContent.click()
                time.sleep(0.5)

            # setting
            self.d.implicitly_wait(2)
            find_setting = self.d(
                resourceId="com.lazada.android:id/iv_settings")
            if (find_setting.wait(2)):
                result["status"] = "Click Setting"
                self.signals.result.emit(result)
                find_setting.click()
                time.sleep(1)
            else:
                find_settingVer580 = self.d(
                    resourceId="com.lazada.android:id/tv_settings")
                if (find_settingVer580.wait(2)):
                    result["status"] = "Click Setting Ver 580"
                    self.signals.result.emit(result)
                    find_settingVer580.click()
                    time.sleep(1)

            # dang xuat
            find_dangXuat = self.d(text="Đăng xuất")
            if (find_dangXuat.wait(5)):
                result["status"] = "Click Đăng Xuất"
                self.signals.result.emit(result)
                find_dangXuat.click()
                time.sleep(0.5)

            # button dang xuat
            find_btnDangXuat = self.d(resourceId="android:id/button1")
            if (find_btnDangXuat.wait(5)):
                result["status"] = "Click Đăng Xuất"
                self.signals.result.emit(result)
                find_btnDangXuat.click()
                time.sleep(0.5)

    def truot(self):
        d = u2.connect(self.deviceName)
        xStart = 0.1
        yStart = 0.256
        resultPointX = []
        resultPointY = []

        xTemp = xStart
        resultPointX.append(xTemp)
        resultPointY.append(yStart)

        while (xTemp < 1.2):
            randomThapPham = round(random.uniform(0.07, 0.22), 3)
            if (xTemp > 0.7):
                xTemp = xTemp + 0.04
            else:
                xTemp = xTemp + randomThapPham
            resultPointX.append(round(xTemp, 3))
            resultPointY.append(yStart)

        XY = zip(resultPointX, resultPointY)
        listXY = list(XY)

        d.swipe_points(listXY, 0.2)

    def layLatMatKhauLazada(self):
        # init
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện lấy lại mật khẩu Lazada",
        }
        self.signals.result.emit(result)
        # init
        device = getDevice(self.deviceName)
        if (self.mail == ""):
            self.getLaiDuLieuCSV()

        # uiautomator init
        d = u2.connect(self.deviceName)

        # button dang nhap
        d.implicitly_wait(3)
        find_btnDangNhap = d(resourceId="com.lazada.android:id/tv_signup")
        if (find_btnDangNhap.wait(3)):
            result["status"] = "Click Đăng Nhập"
            self.signals.result.emit(result)
            print("Click dang nhap")
            find_btnDangNhap.click()
            time.sleep(2)
        else:
            find_btnDangNhapVer580 = d(
                resourceId="com.lazada.android:id/txt_login_signup")
            if (find_btnDangNhapVer580.wait(3)):
                result["status"] = "Click Đăng nhập Version 580"
                self.signals.result.emit(result)
                find_btnDangNhapVer580.click()
                time.sleep(2)

        # dang nhap bang tai khoan khac
        d.implicitly_wait(2)
        find_switchAccount = d(
            resourceId="com.lazada.android:id/tv_switch_account")
        if (find_switchAccount.wait(2)):
            print("Click dang nhap bang tai khoan khac")
            result["status"] = "Click dang nhap bang tai khoan khac"
            self.signals.result.emit(result)
            find_switchAccount.click()
            time.sleep(1)

        # btn sign in
        find_btnSignIn = d(resourceId="com.lazada.android:id/tv_signin")
        if (find_btnSignIn.wait(5)):
            result["status"] = "Click dang nhap"
            self.signals.result.emit(result)
            find_btnSignIn.click()
            time.sleep(1)

        # btn Forget password
        d.implicitly_wait(10.0)
        find_btnForgetPassword = d(
            resourceId="com.lazada.android:id/tv_forget_pwd")
        if (find_btnForgetPassword.wait(5)):
            result["status"] = "Click quên mật khẩu"
            self.signals.result.emit(result)
            find_btnForgetPassword.click()
            time.sleep(1.5)

        # input mail
        find_btnInputMail = d(resourceId="com.lazada.android:id/et_input_text")
        if (find_btnInputMail.wait(5)):
            result["status"] = "LZD - Input Mail: " + self.mail
            self.signals.result.emit(result)
            find_btnInputMail.click()
            time.sleep(1)
            d.send_keys(self.mail)

        # btn TiepTuc
        find_btnTiepTuc = d(resourceId="com.lazada.android:id/btn_next")
        if (find_btnTiepTuc.wait(5)):
            result["status"] = "Click button tiếp tục"
            self.signals.result.emit(result)
            find_btnTiepTuc.click()
            time.sleep(2)
        # find truot
        find_Truot = d.xpath(
            '//*[@resource-id="nc_1-stage-1"]/android.view.View[1]/android.view.View[2]').wait(10)
        if (find_Truot != None):
            result["status"] = "Trượt ......"
            self.signals.result.emit(result)
            self.truot()
            time.sleep(1)

        # find xac minh qua email
        find_xacMinhQuaMail = d(text="Xác minh qua email")
        if (find_xacMinhQuaMail.wait(5)):
            result["status"] = "Click Xác minh qua Email"
            self.signals.result.emit(result)
            find_xacMinhQuaMail.click()
            time.sleep(1.5)

        # btn gui ma
        find_btnGuiMa = d.xpath(
            '//*[@resource-id="send-btn"]/android.view.View[1]').wait(10)
        if (find_btnGuiMa != None):
            result["status"] = "Click Gửi Mã"
            self.signals.result.emit(result)
            find_btnGuiMa.click()
            time.sleep(10)

            result["status"] = "API Get OTP Hotmail By HTN"
            self.signals.result.emit(result)
            otpTempLZD = outlook.apiOTPLZD(self.mail, self.passMail)
            
            while (otpTempLZD == ""):
                result["status"] = "Lấy OTP Lần Nữa"
                self.signals.result.emit(result)
                
                otpTempLZD = outlook.apiOTPLZD(self.mail, self.passMail)
                if (otpTempLZD != ""):
                    result["status"] = "Lấy Được OTP: " + otpTempLZD
                    self.signals.result.emit(result)
                    break

            # input OTP
            find_inputOTP = d(resourceId="number")
            if (find_inputOTP.wait(5)):
                result["status"] = "OTP Code: " + otpTempLZD
                self.signals.result.emit(result)

                find_inputOTP.click()
                d.send_keys(otpTempLZD)

            # click button xac minh ma
            find_btnXacMinhMa = d(resourceId="main-btn")
            if (find_btnXacMinhMa.wait(5)):
                result["status"] = "Click xác minh mã"
                self.signals.result.emit(result)
                find_btnXacMinhMa.click()
                time.sleep(2)

        # dien mat khau
        find_inputPWD = d.xpath(
            '//*[@resource-id="com.lazada.android:id/input_laz_reset_password"]/android.widget.RelativeLayout[1]/android.widget.EditText[1]').wait(10)
        if (find_inputPWD != None):
            result["status"] = "Điền mật khẩu: " + self.passLZD
            self.signals.result.emit(result)
            find_inputPWD.click()
            time.sleep(1)
            d.send_keys(self.passLZD)
            time.sleep(1)

        find_inputAgainPWD = d.xpath(
            '//*[@resource-id="com.lazada.android:id/input_laz_reset_password_again"]/android.widget.RelativeLayout[1]/android.widget.EditText[1]').wait(5)
        if (find_inputAgainPWD != None):
            find_inputAgainPWD.click()
            time.sleep(1)
            d.send_keys(self.passLZD)
            time.sleep(1)

        # btn Dat Lai Mat Khau
        find_btnDatLaiMatKhau = d(
            resourceId="com.lazada.android:id/btn_laz_form_supply_complete")
        if (find_btnDatLaiMatKhau.wait(5)):
            find_btnDatLaiMatKhau.click()

            # cap nhat du lieu len server
            result["status"] = "Reg Acc Thành Công"
            self.signals.result.emit(result)
            self.isRegLZD = True
            self.isRegFB = True
            self.status = "true"
            self.updateDataCSV()
            #self.addAccountVaoServer()
            #them acc vao file

            # xuat ra file excel
            data = {
                "Username": [],
                "PassLZD": [],
                "PassGmail": [],
                "deviceName": [],
                "Status": [],
            }
            
            data["Username"].append(str(self.mail))
            data["PassLZD"].append(str(self.passLZD))
            data["PassGmail"].append(str(self.passMail))
            data["deviceName"].append(str(self.deviceName))
            data["Status"].append(str("Tạo Tài Khoản Lazada Thành Công"))

            
            self.luuAccVaoFile("accLazadaThanhCong.csv",data)
        

    def HuyLienKetFacebook(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Hủy liên kết Facebook.........",
        }
        self.signals.result.emit(result)

        d = u2.connect(self.deviceName)
        # setting
        d.implicitly_wait(2)
        find_setting = d(resourceId="com.lazada.android:id/iv_settings")
        if (find_setting.wait(2)):
            result["status"] = "Click setting"
            self.signals.result.emit(result)

            find_setting.click()
            time.sleep(1)
        else:
            find_settingVer580 = d(
                resourceId="com.lazada.android:id/tv_settings")
            if (find_settingVer580.wait(2)):
                result["status"] = "Click setting ver 580"
                self.signals.result.emit(result)
                find_settingVer580.click()
                time.sleep(1)
        # thong tin tai khoan
        find_thongTinTaiKhoan = d(
            resourceId="com.lazada.android:id/setting_account_information_container")
        if (find_thongTinTaiKhoan.wait(5)):
            result["status"] = "Click thông tin tài khoản"
            self.signals.result.emit(result)
            find_thongTinTaiKhoan.click()
            time.sleep(2)

        # find tai khoan mang xa hoi
        find_taiKhoanMangXaHoi = d(description="Tài khoản mạng xã hội")
        if (find_taiKhoanMangXaHoi.wait(5)):
            result["status"] = "Click tài khoản mạng xã hội"
            self.signals.result.emit(result)
            find_taiKhoanMangXaHoi.click()
            time.sleep(2)

        d.implicitly_wait(10.0)
        find_iconFB = d.xpath('//*[@resource-id="com.lazada.android:id/weex_render_view"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').wait(10)
        if (find_iconFB != None):
            result["status"] = "Click icon facebook"
            self.signals.result.emit(result)
            find_iconFB.click()
            time.sleep(1)

        # find huy lien ket
        d.implicitly_wait(5)
        find_huyLienKet = d(description="Hủy liên kết")
        if (find_huyLienKet.wait(5)):
            result["status"] = "Click hủy liên kết"
            self.signals.result.emit(result)
            find_huyLienKet.click()
            time.sleep(3)

        # find btn xac nhan
        result["status"] = "Click xác nhận"
        self.signals.result.emit(result)
        d.click(0.668, 0.611)

    def runFullWipe(self):
        
        #print(self.passFB)
        self.wipeSachMay()
        
        for i in range(1,5):
            os.system('adb devices')
            time.sleep(1)
        
        self.caiDatFileAPK()
        self.doiIP4G()
        
        self.getDuLieuCSV()
        self.dangNhapFacebook()
        self.dangNhapLZD()
            # self.addMailLazada()
            # self.layLatMatKhauLazada()
            # self.HuyLienKetFacebook()
        result = {
            "serialNumber": self.deviceName,
            "status": "Hoàn Thành Công Việc Chủ Giao",
        }
        self.signals.result.emit(result)

    def runKhongWipe(self):
        
        
        #self.goCaiDatAPK()
        #self.caiDatFileAPK()
        self.d = u2.connect(self.deviceName)
        time.sleep(5)
        
        self.goCaiDatAPK()
        self.caiDatFileAPK()
        #self.fakeDevice()
        self.doiIP4G()
        
        self.getDuLieuCSV()
        time.sleep(2)
        self.dangNhapFacebook()
        self.dangNhapLZD()

        result = {
            "serialNumber": self.deviceName,
            "status": "Hoàn Thành Công Việc Chủ Giao",
        }
        self.signals.result.emit(result)

    def runLayLaiMatKhau(self):

        self.addMailLazada()
        self.layLatMatKhauLazada()
        self.resultAccount.emit()
        self.HuyLienKetFacebook()
        result = {
            "serialNumber": self.deviceName,
            "status": "Hoàn Thành Công Việc Chủ Giao",
        }
        self.signals.result.emit(result)
        
    def runLayLaiMatKhau_2(self):

        self.layLatMatKhauLazada()
        self.resultAccount.emit()
        self.HuyLienKetFacebook()
        result = {
            "serialNumber": self.deviceName,
            "status": "Hoàn Thành Công Việc Chủ Giao",
        }
        self.signals.result.emit(result)   

    def khoiTaoUIAutomator2(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Khởi Tạo ATX",
        }
        self.signals.result.emit(result)
       

        # uiautomator init
        self.d = u2.connect(self.deviceName)
        time.sleep(2)
        self.d.unlock()
        time.sleep(1)
        
        result["status"] = "Connected: " + self.d.device_info["udid"]
        self.signals.result.emit(result)
        

    def setHoTen(self):
        # read file json
        f = open('./Config/listName.json', encoding="utf8")
        # load data
        data = json.load(f)
        
        randomIndex = random.randrange(1, len(data))
        self.last_name = unidecode(data[randomIndex]["last_name"])
        self.first_name = unidecode(data[randomIndex]["first_name"])

        # ki tu !@#$%^&
        listKiTu = ['!', '@', '#', '$', '%', '^', '&']
        self.passFB = unidecode(data[randomIndex]["last_name_group"] + data[randomIndex]["first_name"] + str(random.randrange(
            1000, 99999))).lower().replace(" ", "") + listKiTu[random.randrange(0, len(listKiTu))] + listKiTu[random.randrange(0, len(listKiTu))]
        # self.passFB = (self.last_name + self.first_name + str(random.randrange(1000,99999))).lower().replace(" ", "") + listKiTu[random.randrange(0,len(listKiTu))]
        self.passFB = self.passFB[:1].upper() + self.passFB[1:]

    def thueSimUS(self):
        url = 'https://otpmmo.online/textnow/api.php?apikey=ZJRATFS7Q8HXWCV61629390261&type=getphone&qty=1' 
        result = requests.get(url)
        print(result.text)
        
        if (result.text != ""):
            self.phoneNumber = result.text
        print("Phone US Thue: " + self.phoneNumber)
        
    def layOTPUS(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Lấy OTP US",
        }
        self.signals.result.emit(result)
        dem = 0
        while (dem <= 7):
            
            url = 'https://otpmmo.online/textnow/api.php?apikey=ZJRATFS7Q8HXWCV61629390261&type=getotp&sdt=' + self.phoneNumber
            response = requests.get(url)
            dataAPI = response.text
            
            otpFB = re.findall(r"\b\d{5}\b", dataAPI) 
            if (len(otpFB) > 0):
                self.otpFB = otpFB[0]
                print("OTP Code -- " + str(self.deviceName) + " : "+self.otpFB)
                result["status"] = "OTP Code -- " + str(self.deviceName) + " : "+self.otpFB
                self.signals.result.emit(result)
                break
            elif (len(otpFB) == 0):
                print("Lay OTP Lan Nua")
                result["status"] = "Lay OTP Lan Nua " + str(dem)
                self.signals.result.emit(result)
            
            dem = dem + 1
            time.sleep(10)
    
    def getCookieAndToken(self):
        self.d = u2.connect(self.deviceName)
        tenFile = self.deviceName + ".txt"
        self.d.pull("/data/data/com.facebook.katana/app_light_prefs/com.facebook.katana/authentication","./Data/" + tenFile)
        time.sleep(1)

        file = open('./Data/' + tenFile ,mode='r',errors="ignore")

        # read all lines 
        allData =file.read()
        token = re.findall("EAA[a-z,A-Z,0-9]{0,}",allData)
        token = token[0]
        sualines = allData.replace("\""," ")

        allValues = re.findall("value : [a-z,A-z,0-9,.,:,-]{0,}",sualines)
        print("uid:" + allValues[0].replace("value : ",""))
        uid = allValues[0].replace("value : ","")

        c_user = "c_user" + allValues[0].replace("value : ","=")
        xs = ";xs" + allValues[1].replace("value : ","=")
        fr = ";fr" +  allValues[2].replace("value : ","=")
        datr = ";datr" + allValues[3].replace("value : ","=")
        
        fullCookie = c_user + xs + fr+ datr
        print(fullCookie)
        
        file1 = open("./Config/accFBLive.txt", "a")
        contentData = uid+ "|" + self.passFB + "|" + fullCookie + "|" + token
        
        file1.write(contentData)
        file1.write("\n")
        file1.close()
        
    
    def regAccFacebook(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Reg Acc Facebook.........",
        }
        self.signals.result.emit(result)
        
        self.d = u2.connect(self.deviceName)
        
        result["status"] = "Connected: " + self.d.device_info["udid"]
        self.signals.result.emit(result)
        
        self.d.app_start("com.facebook.katana",use_monkey=True)
        time.sleep(2)
        
        self.setHoTen()
        
        #More Languages
        self.d.implicitly_wait(7)
        find_Languages = self.d(description="More languages…")
        if (find_Languages.wait(7)):
            result["status"] = "Click More Languages"
            self.signals.result.emit(result)
            time.sleep(1)
            
            find_Languages.click()
            time.sleep(1)
            
            #Chon Tieng Viet
            self.d.implicitly_wait(10)
            find_TiengViet = self.d(text="Tiếng Việt")
            if (find_TiengViet.wait(10)):
                result["status"] = "Click Tiếng Việt"
                self.signals.result.emit(result)
                time.sleep(1)
                
                find_TiengViet.click()
                time.sleep(1)
                
        #Tao Tai Khoan Moi
        self.d.implicitly_wait(10)
        find_TaoTaiKhoanMoi = self.d(description="Tạo tài khoản Facebook mới")
        if (find_TaoTaiKhoanMoi.wait(10)):
            result["status"] = "Click Tạo Tài Khoản Mới"
            self.signals.result.emit(result)
            time.sleep(1)
            
            find_TaoTaiKhoanMoi.click()
            time.sleep(1)
                    
        #Tham Gia Facebook
        find_ThamGiaFacebook = self.d(text="Tham gia Facebook")
        if (find_ThamGiaFacebook.wait(10)):
            result["status"] = "Tham Gia Facebook"
            self.signals.result.emit(result)
            time.sleep(1)
            
            find_TiepPart1 = self.d(text="Tiếp")
            if (find_TiepPart1.wait(5)):
                result["status"] = "Click Tiếp"
                self.signals.result.emit(result)
                time.sleep(1)
                
                find_TiepPart1.click()
                time.sleep(1)
                
                #Truy Cap Danh Ba
                find_Deny1 = self.d(resourceId="com.android.permissioncontroller:id/permission_deny_button")
                if (find_Deny1.wait(5)):
                    result["status"] = "Click Deny Contact"
                    self.signals.result.emit(result)
                    time.sleep(1)
                    
                    find_Deny1.click()
                    time.sleep(1)
                    
                    #Deny 2
                    find_Deny2 = self.d(resourceId="com.android.permissioncontroller:id/permission_deny_button")
                    if (find_Deny2.wait(5)):
                        result["status"] = "Click Deny Phone"
                        self.signals.result.emit(result)
                        time.sleep(1)
                        
                        find_Deny2.click()
                        time.sleep(1)
                        
        #Ho Va Ten
        self.d.implicitly_wait(10.0)
        find_BanTenGi = self.d(text="Bạn tên gì?")
        if (find_BanTenGi.wait(10)):
            result["status"] = "Điền Họ Tên"
            self.signals.result.emit(result)
            
            
            #input ten
            self.d.click(0.208,0.325)
            time.sleep(1)
            
            result["status"] = "Tên: " + self.first_name
            self.signals.result.emit(result)
            time.sleep(1)
            
            self.d.send_keys(self.first_name)
            time.sleep(2)
            
            #input họ
            self.d.click(0.616,0.372)
            time.sleep(1)
            
            result["status"] = "Họ: " + self.last_name
            self.signals.result.emit(result)
            time.sleep(1)
            
            self.d.send_keys(self.last_name)
            time.sleep(2)
            
            find_TiepPart2 = self.d(text="Tiếp")
            if (find_TiepPart2.wait(5)):
                result["status"] = "Click Tiếp Part 2"
                self.signals.result.emit(result)
                time.sleep(1)
                
                find_TiepPart2.click()
                time.sleep(2)
                
        #Ngay Sinh
        self.d.implicitly_wait(10)
        find_NgaySinh = self.d(text="Ngày sinh")
        if (find_NgaySinh.wait(10)):
            result["status"] = "Ngày Sinh"
            self.signals.result.emit(result)
            
            
            #Chon Năm Sinh
            randomNam = random.randrange(15,35)
            result["status"] = "Năm: " + str(randomNam)
            self.signals.result.emit(result)
            for i in range(randomNam):
                self.d.double_click(0.746, 0.318,0.2)
            time.sleep(1)
            
            #Chọn Tháng Sinh
            randomThang = random.randrange(1,12)
            result["status"] = "Tháng: " + str(randomThang)
            self.signals.result.emit(result)
            for i in range(randomThang):
                self.d.double_click(0.55, 0.316,0.2)
            time.sleep(1)
            
            #Chọn Ngày Sinh
            randomNgay = random.randrange(1,15)
            result["status"] = "Ngày: " + str(randomNgay)
            self.signals.result.emit(result)
            for i in range(randomNgay):
                self.d.double_click(0.37, 0.317,0.2)
            time.sleep(1)
            
            #Click Tiếp
            find_TiepPart3 = self.d(text="Tiếp")
            if (find_TiepPart3.wait(5)):
                result["status"] = "Click Tiếp"
                self.signals.result.emit(result)
                time.sleep(1)
                
                find_TiepPart3.click()
                time.sleep(1)
                
                
        #Chọn Giới Tính
        self.d.implicitly_wait(10)
        find_GioiTinh = self.d(text="Giới tính")
        if (find_GioiTinh.wait(10)):
            result["status"] = "Chọn Giới Tính"
            self.signals.result.emit(result)
            time.sleep(1)
            
            randomGioiTinh = random.randrange(1,3)
            if (randomGioiTinh == 1):
                result["status"] = "Giới Tính: Nữ"
                self.signals.result.emit(result)
                
                find_Nu = self.d(text="Nữ")
                if (find_Nu.wait(5)):
                    find_Nu.click()
                    time.sleep(1)
            elif (randomGioiTinh == 2):
                result["status"] = "Giới Tính: Nam"
                self.signals.result.emit(result)
                
                find_Nam = self.d(text="Nam")
                if (find_Nam.wait(5)):
                    find_Nam.click()
                    time.sleep(1)
                    
            #Click Tiếp
            find_TiepPartGioiTinh = self.d(text="Tiếp")
            if (find_TiepPartGioiTinh.wait(5)):
                result["status"] = "Click Tiếp"
                self.signals.result.emit(result)
                time.sleep(1)
                
                find_TiepPartGioiTinh.click()
                time.sleep(1)
                    
        ################## Số Di Động
        self.d.implicitly_wait(10)
        find_NhapDiDong = self.d( text="Nhập số di động của bạn")
        if (find_NhapDiDong.wait(10)):
            result["status"] = "Số Di Động. Thực Hiện Thuê Phone US"
            self.signals.result.emit(result)
            time.sleep(1)
            
            self.d.click(0.46,0.395)
            time.sleep(1)
            self.d.clear_text()
            
            self.thueSimUS()
            time.sleep(1)
            
            result["status"] = "PhoneNumber: " + self.phoneNumber
            self.signals.result.emit(result)     
            
            self.d.send_keys("+1" + self.phoneNumber)
            time.sleep(2)                
            
            #Click Tiếp
            find_TiepPart4 = self.d(text="Tiếp")
            if (find_TiepPart4.wait(5)):
                find_TiepPart4.click()
                time.sleep(2) 
        
        ######VERY BY HOTMAIL
        # self.d.implicitly_wait(10)
        # find_InputMail = self.d(text="Đăng ký bằng địa chỉ email")
        # if (find_InputMail.wait(10)):
        #     result["status"] = "Click reg by mail"
        #     self.signals.result.emit(result)
            
        #     find_InputMail.click()
        #     time.sleep(2)
            
        #     self.buyHotMailMaxClone()
        #     time.sleep(1)
            
        #     self.d.send_keys(self.mail)
        #     time.sleep(2)
            
        #     find_TiepMail = self.d( text="Tiếp")
        #     if (find_TiepMail.wait(5)):
        #         find_TiepMail.click()
        #         time.sleep(2)
        ##############################
        
        #Chọn Mật Khẩu     
        self.d.implicitly_wait(10)              
        find_ChonMatKhau = self.d(text="Chọn mật khẩu")
        if (find_ChonMatKhau.wait(10)):
            result["status"] = "Mật Khẩu: " + self.passFB
            self.signals.result.emit(result)  
            
            self.d.click(0.353, 0.333)
            time.sleep(1)
            
            self.d.send_keys(self.passFB)
            time.sleep(2)
            
            #Click Tiếp
            find_TiepPart5 = self.d(text="Tiếp")
            if (find_TiepPart5.wait(5)):
                find_TiepPart5.click()
                time.sleep(2) 
            
        #Hoàn Tất Đăng Ký
        self.d.implicitly_wait(10)
        find_HoanTatDangKy = self.d(text="Hoàn tất đăng ký")
        if (find_HoanTatDangKy.wait(10)):
            
            find_DangKy = self.d(text="Đăng ký")
            if (find_DangKy.wait(10)):
                result["status"] = "Click Đăng Ký - Đợi 10s"
                self.signals.result.emit(result)   
                
                find_DangKy.click()
                time.sleep(4)
                
                # self.d.app_start("com.cell47.College_Proxy", use_monkey=True)
                # result["status"] = "Mở App Proxy V6"
                # self.signals.result.emit(result)
                
                # self.d.implicitly_wait(10)
                # find_StopProxy = self.d(resourceId="com.cell47.College_Proxy:id/proxy_start_button")
                # if (find_StopProxy.wait(10)):
                #     find_StopProxy.click()
                #     time.sleep(1)
                    
                # self.d.app_start("com.facebook.katana",use_monkey=True)
                # time.sleep(12)
                
                #Lưu Mật Khẩu
                self.d.implicitly_wait(30)
                find_LuuMatKhau = self.d(text="LƯU MẬT KHẨU")
                if (find_LuuMatKhau.wait(30)):
                    result["status"] = "Lưu Mật Khẩu"
                    self.signals.result.emit(result)
                    
                    time.sleep(1)
                    find_LuuMatKhau.click()
                    time.sleep(2)
                    
                    #OK
                    find_OK = self.d(description="OK")
                    if (find_OK.wait(5)):
                        result["status"] = "Click OK"
                        self.signals.result.emit(result)
                        
                        find_OK.click()
                        time.sleep(2)
                        
                    #Truong Hợp SDT Lỗi
                    self.d.implicitly_wait(3)
                    find_InputSDTLan2 = self.d( text="Số điện thoại di động")
                    if (find_InputSDTLan2.wait(3)):
                        result["status"] = "Cập nhật số US khác"
                        self.signals.result.emit(result)
                        
                        self.thueSimUS()
                        time.sleep(1)
                        
                        result["status"] = "PhoneNumber: " + self.phoneNumber
                        self.signals.result.emit(result)     
                        find_InputSDTLan2.click()
                        time.sleep(1)
                        
                        self.d.send_keys("+1" + self.phoneNumber)
                        time.sleep(2)
                        
                        find_CapNhatSDT = self.d( text="Cập nhật số di động")
                        if (find_CapNhatSDT.wait(5)):
                            find_CapNhatSDT.click()
                            time.sleep(2)
                        
                        
                    #Xác Nhận Tài Khoản
                    self.d.implicitly_wait(10)
                    find_NhapMaSMS = self.d(text="Nhập mã từ SMS của bạn")
                    if (find_NhapMaSMS.wait(10)):
                        
                        self.layOTPUS()
                        
                        if (self.otpFB != ""):
                            find_MaXacNhan = self.d(text="Mã xác nhận")
                            if (find_MaXacNhan.wait(10)):
                                find_MaXacNhan.click()
                                time.sleep(1)
                                
                                #lay otp
                                self.d.send_keys(self.otpFB)
                                time.sleep(1)
                                
                                #Xác nhận
                                find_XacNhan = self.d(text="Xác nhận")
                                if (find_XacNhan.wait(10)):
                                    result["status"] = "Click Xác Nhận"
                                    self.signals.result.emit(result)
                                    
                                    find_XacNhan.click()
                                    time.sleep(5)
                                    
                        else:
                            result["status"] = "Thuê Sim Khác"
                            self.signals.result.emit(result)
                            
                            #Thue Sim Khac
                            self.d.implicitly_wait(10)
                            find_ThayDoiSDT = self.d(description="Thay đổi số điện thoại")
                            if (find_ThayDoiSDT.wait(10)):
                                find_ThayDoiSDT.click()
                                time.sleep(1)

                                find_InputSDT = self.d(text="Số điện thoại di động")
                                if (find_InputSDT.wait(10)):
                                    find_InputSDT.click()
                                    time.sleep(1)
                                    
                                    self.thueSimUS()
                                    time.sleep(1)
                                    
                                    result["status"] = "PhoneNumber: " + self.phoneNumber
                                    self.signals.result.emit(result)     
                                    
                                    self.d.send_keys("1" + self.phoneNumber)
                                    time.sleep(2)
                                    
                                    #check sdt da duoc ok chua
                                    self.d.implicitly_wait(3)
                                    find_CheckSDT = self.d(text="Nhập một số điện thoại di động mới.")
                                    if (find_CheckSDT.wait(3)):
                                        #thue phone khac
                                        print("ABCD")
                                    
                                    
                                    self.d.implicitly_wait(10)
                                    find_MaXacNhan2 = self.d(text="Mã xác nhận")
                                    if (find_MaXacNhan2.wait(10)):
                                        self.layOTPUS()
                                        
                                        find_MaXacNhan2.click()
                                        time.sleep(1)
                                        
                                        #lay otp
                                        self.d.send_keys(self.otpFB)
                                        time.sleep(1)
                                        
                                        #Xác nhận
                                        find_XacNhan = self.d(text="Xác nhận")
                                        if (find_XacNhan.wait(10)):
                                            result["status"] = "Click Xác Nhận"
                                            self.signals.result.emit(result)
                                            
                                            find_XacNhan.click()
                                            time.sleep(5)
                    
                    
                        #Thêm Ảnh Của Bạn
                        self.d.implicitly_wait(10)
                        find_ThemAnhCuaBan = self.d( text="Thêm ảnh của bạn")      
                        if (find_ThemAnhCuaBan.wait(10)):
                            #function push random avatar
                            
                            find_ChonAnhTuThuVien = self.d(text="Chọn từ thư viện") 
                            if (find_ChonAnhTuThuVien.wait(5)):
                                result["status"] = "Click Bỏ Qua"
                                self.signals.result.emit(result)
                                
                                self.d.click(0.898,0.075)
                                time.sleep(1)
                                
                                #get Cookie và Lưu Acc
                                result["status"] = "Lấy Cookie Và Lưu Acc Vào File"
                                self.signals.result.emit(result)
                                self.getCookieAndToken()
                                #Tìm bạn bè
                                self.d.implicitly_wait(10)
                                find_TimBanBe = self.d(text="Tìm bạn bè")
                                if (find_TimBanBe.wait(10)):
                                    result["status"] = "Click Bỏ Qua"
                                    self.signals.result.emit(result)
                                    
                                    self.d.click(0.898,0.075)
                                    time.sleep(1)
                                    
                                    find_BOQUA = self.d(text="BỎ QUA")
                                    if (find_BOQUA.wait(5)):
                                        find_BOQUA.click()
                                        time.sleep(5)
                                        
                                    self.d.click(0.505, 0.895)
                                    time.sleep(2)
                
                else:
                    find_TiepTuc = self.d(description="Tiếp tục")
                    if (find_TiepTuc.wait(5)):
                        result["status"] = "Reg Fail"
                        self.signals.result.emit(result)
                        
    def fakeDevice(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "------ Fake Device ---->",
        }
        self.signals.result.emit(result)
        
        self.d = u2.connect(self.deviceName)
        
        
        self.d.app_start("com.unique.mobilefaker.plus", use_monkey=True)
        result["status"] = "Mở App Mobile Faker"
        self.signals.result.emit(result)
        
        time.sleep(1)
        
        self.d.implicitly_wait(10)
        find_Random = self.d(resourceId="com.unique.mobilefaker.plus:id/button3")
        if (find_Random.wait(10)):
            result["status"] = "Random Device Fake"
            self.signals.result.emit(result)
            find_Random.click()
            time.sleep(1)
            
            self.d.implicitly_wait(5)
            find_Apply = self.d(resourceId="com.unique.mobilefaker.plus:id/button2")
            if (find_Apply.wait(5)):
                result["status"] = "Click Apply"
                self.signals.result.emit(result)
                find_Apply.click()
                time.sleep(2)
                
        self.d.app_start("com.device.emulator.pro", use_monkey=True)
        result["status"] = "Mở App Fake Device Emulator Pro"
        self.signals.result.emit(result)
        time.sleep(1)
        
        self.d.implicitly_wait(10)
        find_RandomAll = self.d(resourceId="com.device.emulator.pro:id/action_randomall")
        if (find_RandomAll.wait(10)):
            result["status"] = "Random Device Emulator Pro"
            self.signals.result.emit(result)
            find_RandomAll.click()
            time.sleep(1)
            
            self.d.implicitly_wait(5)
            find_ActionReboot = self.d(resourceId="com.device.emulator.pro:id/action_fastreboot")
            if (find_ActionReboot.wait(5)):
                result["status"] = "Apply Device Emulator Pro"
                self.signals.result.emit(result)
                find_ActionReboot.click()
                time.sleep(2)
                
                find_OK = self.d(resourceId="android:id/button1")
                if (find_OK.wait(5)):
                    find_OK.click()
                    time.sleep(1)
    
    def addProxy(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "------ Add Proxy V6 ---->",
        }
        self.signals.result.emit(result)
        
        self.d = u2.connect(self.deviceName)
        
        #getProxy
        self.mutex.lock()
        self.getProxy()
        time.sleep(1)
        self.mutex.unlock()
        
        time.sleep(1)
        
        print(self.proxy)
        proxyArray = self.proxy.split(":")
        proxyIP = proxyArray[0]
        proxyPort = proxyArray[1]
        proxyUsername = proxyArray[2]
        proxyPassword = proxyArray[3]
        
        
        self.d.app_start("com.cell47.College_Proxy", use_monkey=True)
        result["status"] = "Mở App Proxy V6"
        self.signals.result.emit(result)
        
        time.sleep(2)
        
        # input proxyip
        self.d.implicitly_wait(10)
        find_inputProxyIP = self.d(resourceId="com.cell47.College_Proxy:id/editText_address")
        if (find_inputProxyIP.wait(10)):
            find_inputProxyIP.click()
            time.sleep(1)
            result["status"] = "Input Proxy: " + str(proxyIP)
            self.signals.result.emit(result)
            self.d.send_keys(proxyIP)
            time.sleep(1)
            
        # input Port
        find_inputPort = self.d(resourceId="com.cell47.College_Proxy:id/editText_port")
        if (find_inputPort.wait(10)):
            find_inputPort.click()
            time.sleep(1)
            result["status"] = "Input Port " + str(proxyPort)
            self.signals.result.emit(result)
            self.d.send_keys(proxyPort)
            time.sleep(1)
        
        # input username
        find_inputUsername = self.d(resourceId="com.cell47.College_Proxy:id/editText_username")
        if (find_inputUsername.wait(10)):
            find_inputUsername.click()
            time.sleep(1)
            self.d.send_keys(proxyUsername)
            time.sleep(1)
            
        # input password
        find_inputPassword = self.d(resourceId="com.cell47.College_Proxy:id/editText_password")
        if (find_inputPassword.wait(10)):
            find_inputPassword.click()
            time.sleep(1)
            self.d.send_keys(proxyPassword)
            time.sleep(1)
        
        # click start proxy service
        self.d.implicitly_wait(10)
        find_btnStart = self.d(resourceId="com.cell47.College_Proxy:id/proxy_start_button")
        if (find_btnStart.wait(10)):
            find_btnStart.click()
            result["status"] = "Start Proxy"
            self.signals.result.emit(result)
            time.sleep(2)
        
            
        # connection request
        self.d.implicitly_wait(3)
        find_Connection = self.d(resourceId="android:id/button1")
        if (find_Connection.wait(3)):
            find_Connection.click()
            time.sleep(3)
    
    def fullWipeDangNhapBangMatKhau(self):
        self.wipeSachMay()
        self.dangNhapLZDBangMatKhau(isInstallApp=True)
        #time.sleep(0.5)
        #self.d.press("back")
        
    def noWipeDangNhapBangMatKhau(self):
        self.goCaiDatAPK()
        self.dangNhapLZDBangMatKhau(isInstallApp=True)
        #time.sleep(0.5)
        #self.d.press("back")
        
    def ChiDangNhapBangMatKhau(self):
        self.dangNhapLZDBangMatKhau(isInstallApp=False)
        
        
    def addDiaChi(self,tenTinh):
        
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện Add Địa Chỉ Lazada",
        }
        self.signals.result.emit(result)
        self.d = u2.connect(self.deviceName)
        
        result["status"] = "Connected: " + self.d.device_info["udid"]
        self.signals.result.emit(result)
        
        #get acc
        self.getDataAcc()
        time.sleep(0.5)
        
        #click tai khoan
        self.d.implicitly_wait(3)
        find_TaiKhoan = self.d(resourceId="com.lazada.android:id/title", text="Tài khoản")
        if (find_TaiKhoan.wait(3)):
            result["status"] = "Click Tài Khoản"
            self.signals.result.emit(result)
            
            find_TaiKhoan.click()
            time.sleep(1)
        else:
            self.d.click(0.895, 0.914)
            time.sleep(1)
            
        # guide Content
        self.d.implicitly_wait(1)
        find_guideContent = self.d(
            resourceId="com.lazada.android:id/btn_guide_content")
        if (find_guideContent.wait(2)):
            
            result["status"] = "Click OK !!!"
            self.signals.result.emit(result)
            time.sleep(1)
            find_guideContent.click()
            time.sleep(1)
        else:
            self.d.implicitly_wait(1)
            find_daHieu = self.d(resourceId="com.lazada.android:id/txt_gotit")
            if (find_daHieu.wait(1)):
                result["status"] = "Click Đã Hiểu"
                self.signals.result.emit(result)
                time.sleep(1)
                find_daHieu.click()
                time.sleep(1)
        # setting
        self.d.implicitly_wait(4)
        find_setting = self.d(resourceId="com.lazada.android:id/iv_settings")
        if (find_setting.wait(2)):
            result["status"] = "Click SETTING"
            self.signals.result.emit(result)
            find_setting.click()
            time.sleep(2)
        else:
            self.d.implicitly_wait(2)
            find_settingVer580 = self.d(
                resourceId="com.lazada.android:id/tv_settings")
            if (find_settingVer580.wait(2)):
                result["status"] = "Click Setting Ver 580"
                self.signals.result.emit(result)
                find_settingVer580.click()
                time.sleep(2)
        # thong tin tai khoan
        self.d.implicitly_wait(10)
        find_thongTinTaiKhoan = self.d(
            resourceId="com.lazada.android:id/setting_account_information_container")
        if (find_thongTinTaiKhoan.wait(10)):
            result["status"] = "Click thông tin tài khoản"
            self.signals.result.emit(result)
            find_thongTinTaiKhoan.click()
            time.sleep(2)
            
            result["status"] = "Đổi Tên: " + self.full_name
            self.signals.result.emit(result)
            
            self.d.implicitly_wait(10)
            find_Ten = self.d(description="Tên")
            if (find_Ten.wait(10)):
                find_Ten.click()
                time.sleep(2)
                
                self.d.implicitly_wait(1)
                find_XoaHet = self.d.xpath('//android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').wait(5)
                if (find_XoaHet != None):
                    result["status"] = "Xóa Hết XPath"
                    self.signals.result.emit(result)
                    find_XoaHet.click()
                    time.sleep(1)
                    
                    self.d.send_keys(self.full_name)
                    time.sleep(1)
                    
                    self.d.implicitly_wait(1)
                    find_Luu = self.d(description="Lưu")
                    if (find_Luu.wait(1)):
                        find_Luu.click()
                        time.sleep(2)
                
                else:
                    result["status"] = "Xóa Hết Else"
                    self.signals.result.emit(result)
                    self.d.click(0.479,0.738)
                    time.sleep(1)
                    self.d.clear_text()
                    time.sleep(0.5)
                    
                    self.d.send_keys(self.full_name)
                    time.sleep(1)
                    
                    self.d.implicitly_wait(1)
                    find_Luu = self.d(description="Lưu")
                    if (find_Luu.wait(1)):
                        find_Luu.click()
                        time.sleep(2)
            
            #back
            self.d.press("back")
            time.sleep(2)
            
            #add dia chi
            self.d.implicitly_wait(5)
            find_SoDiaChi = self.d(text="Sổ địa chỉ")
            if (find_SoDiaChi.wait(5)):
                result["status"] = "Click Sổ Địa Chỉ"
                self.signals.result.emit(result)
                find_SoDiaChi.click()
                time.sleep(2)
                
                #them dia chi moi
                find_ThemDiaChiMoi = self.d(resourceId="com.lazada.android:id/btn_action")
                if (find_ThemDiaChiMoi.wait(3)):
                    result["status"] = "Click Thêm Địa Chỉ Mới"
                    self.signals.result.emit(result)
                    find_ThemDiaChiMoi.click()
                    time.sleep(2)
                    
                    #function add dia chi
                    self.dienThongTinDiaChi()
                    
                    
    def dienThongTinDiaChi(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện Add Địa Chỉ Lazada",
        }
        
        self.d = u2.connect(self.deviceName)
        self.getDataAcc()
        time.sleep(0.5)
        #input ho ten
        self.d.implicitly_wait(5)
        find_HoTen = self.d.xpath('//*[@resource-id="com.lazada.android:id/recyclerview"]/android.widget.RelativeLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]').wait(5)
        if (find_HoTen != None):
            result["status"] = "Họ Tên: " + self.full_name
            self.signals.result.emit(result)
            find_HoTen.click()
            time.sleep(1)
            
            self.d.send_keys(self.full_name)
            time.sleep(2)
            
        #input Dia Chi
        self.d.implicitly_wait(2)
        find_DiaChi = self.d.xpath('//*[@resource-id="com.lazada.android:id/recyclerview"]/android.widget.RelativeLayout[2]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]').wait(2)
        if (find_DiaChi != None):
            result["status"] = "Địa Chỉ: " + self.address
            self.signals.result.emit(result)
            find_DiaChi.click()
            time.sleep(1)
            
            self.d.send_keys(self.address)
            time.sleep(1)
    
                
        #input PhoneNumber
        self.d.implicitly_wait(2)
        find_PhoneNumber = self.d.xpath('//*[@resource-id="com.lazada.android:id/recyclerview"]/android.widget.RelativeLayout[6]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]').wait(2)
        if (find_PhoneNumber != None):
            result["status"] = "Phone : " + self.phoneNumber
            self.signals.result.emit(result)
            find_PhoneNumber.click()
            time.sleep(1)
            
            self.d.send_keys(self.phoneNumber)
            time.sleep(1)
        else:
            self.d.implicitly_wait(2)
            find_PhoneNumberNew = self.d.xpath('//*[@resource-id="com.lazada.android:id/recyclerview"]/android.widget.RelativeLayout[2]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]').wait(2)
            if (find_PhoneNumberNew != None):
                result["status"] = "Phone New: " + self.phoneNumber
                self.signals.result.emit(result)
                find_PhoneNumberNew.click()
                time.sleep(1)
                
                self.d.send_keys(self.phoneNumber)
                time.sleep(1)
                
                result["status"] = "Địa Chỉ New: " + self.address
                self.signals.result.emit(result)
                self.d.click(0.23, 0.379)
                time.sleep(1)
                
                self.d.send_keys(self.address)
                time.sleep(1)
            
        #tinh/thanh pho
        find_TinhTP = self.d.xpath('//*[@resource-id="com.lazada.android:id/recyclerview"]/android.widget.RelativeLayout[3]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]').wait(5)
        if (find_TinhTP != None):
            result["status"] = "Chọn Thành Phố"
            self.signals.result.emit(result)
            find_TinhTP.click()
            time.sleep(2)
            
            self.chonTinh("HaNoi")
            
            result["status"] = "Kết Thúc Add Địa Chỉ"
            self.signals.result.emit(result)
                            
    def chonTinh(self,tenTinh):
        if (tenTinh == "HaNoi"):
            # Ha Noi
            for i in range(3):
                self.d.swipe_ext ( "up" , scale = 0.95 )
                time.sleep(1)
            
            self.d.implicitly_wait(5)
            find_HaNoi = self.d(resourceId="com.lazada.android:id/tv_address_location_tree_name", text="Hà Nội")
            if (find_HaNoi.wait(5)):
                time.sleep(0.5)
                find_HaNoi.click()
                time.sleep(2)
            
                # Thuong tin
                for i in range(2):
                    self.d.swipe_ext ( "up" , scale = 0.95 )
                    time.sleep(1)
                    
                self.d.implicitly_wait(5)
                find_ThuongTin = self.d(resourceId="com.lazada.android:id/tv_address_location_tree_name", text="Huyện Thường Tín")
                if (find_ThuongTin.wait(5)):
                    time.sleep(0.5)
                    find_ThuongTin.click()
                    time.sleep(2)
        elif tenTinh == "HoChiMinh":
            self.d.implicitly_wait(5)
            find_HCM = self.d(resourceId="com.lazada.android:id/tv_address_location_tree_name", text="Hồ Chí Minh")
            if (find_HCM.wait(5)):
                find_HCM.click()
                time.sleep(2)
                
                #Quan 10
                for i in range(2):
                    self.d.swipe_ext ( "up" , scale = 0.95 )
                    time.sleep(1)
                    
                self.d.implicitly_wait(5)
                find_Quan10 = self.d(resourceId="com.lazada.android:id/tv_address_location_tree_name", text="Quận 10")
                if (find_Quan10.wait(5)):
                    find_Quan10.click()
                    time.sleep(2)
                    
                    self.d.swipe_ext ( "up" , scale = 0.95 )
                    time.sleep(1)
                    
                    self.d.implicitly_wait(5)
                    find_Phuong13 = self.d(resourceId="com.lazada.android:id/tv_address_location_tree_name", text="Phường 13")
                    if (find_Phuong13.wait(5)):
                        find_Phuong13.click()
                        time.sleep(1)
                           
    def XemVoucher(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Thực hiện Kiểm Tra Voucher",
        }
        self.signals.result.emit(result)
        
        # self.d.press("back")
        # time.sleep(1)
        self.d = u2.connect(self.deviceName)
        
        self.d.press("back")
        time.sleep(1)
        
        self.d.press("back")
        time.sleep(1)
        
        self.d.swipe_ext ( "up" , scale = 0.95 )
        time.sleep(1)
        
        self.d.implicitly_wait(3)
        find_MaGiamGia = self.d(resourceId="com.lazada.android:id/tv_wallet_type", text="Mã giảm giá")
        if (find_MaGiamGia.wait(3)):
            result["status"] = "Click Xem Voucher"
            self.signals.result.emit(result)
            find_MaGiamGia.click()
            time.sleep(1)
            
            result["status"] = "Kết Thúc Xem Voucher"
            self.signals.result.emit(result)
    
    def ThemGioHang(self):
        result = {
            "serialNumber": self.deviceName,
            "status": "Thêm Giỏ Hàng",
        }
        self.signals.result.emit(result)
        
        self.d = u2.connect(self.deviceName)
        
        #check tha tym
        self.d.implicitly_wait(1)
        find_ThaTim = self.d(resourceId="com.lazada.android:id/like_wrapper_layout")
        if (find_ThaTim.wait(1)):
            find_ThaTim.long_click()
            time.sleep(0.5)
        
        #them voucher freeship
        self.d.implicitly_wait(3)
        find_BamDeNhan = self.d(resourceId="com.lazada.android:id/title", text="Bấm để nhận")
        if (find_BamDeNhan.wait(3)):
            
            find_BamDeNhan.long_click()
            time.sleep(2)
            
            find_Freeship1 = self.d.xpath('//*[@resource-id="com.lazada.android:id/recycler_view"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.RelativeLayout[1]/android.view.ViewGroup[1]/android.widget.TextView[2]').long_click()
            
            time.sleep(3)
            
            find_Freeship2 = self.d.xpath('//*[@resource-id="com.lazada.android:id/recycler_view"]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.view.ViewGroup[1]/android.widget.RelativeLayout[1]/android.view.ViewGroup[1]/android.widget.TextView[2]').long_click()
            
            
            time.sleep(3)
            
            self.d(resourceId="com.lazada.android:id/popup_header_close").click(timeout=5)
            time.sleep(2)
        
        # Them Gio Hang
        self.d.implicitly_wait(3)
        find_ThemGioHang = self.d(resourceId="com.lazada.android:id/main_action")
        if (find_ThemGioHang.wait(3)):
            find_ThemGioHang.long_click()
            time.sleep(1)
            
            #check option color family
            self.d.implicitly_wait(2)
            find_ColorFamily = self.d(resourceId="com.lazada.android:id/title")
            if (find_ColorFamily.wait(2)):
                randomImageIndex = random.randrange(1,2)
                print("Random Image: " + str(randomImageIndex))
                
                if (randomImageIndex == 1):
                    self.d.implicitly_wait(1)
                    find_Image1= self.d.xpath('//*[@resource-id="com.lazada.android:id/flex_box"]/android.widget.RelativeLayout[1]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.RelativeLayout[1]/android.widget.ImageView[1]').wait(1)
                    if (find_Image1 != None):
                        find_Image1.click()
                        time.sleep(1)
                    else:
                        find_Image11 = self.d.xpath('//*[@resource-id="com.lazada.android:id/flex_box"]/android.widget.RelativeLayout[1]/android.widget.RelativeLayout[1]').wait(1)
                        if (find_Image11 != None):
                            find_Image11.click()
                            time.sleep(1)
                            
                elif (randomImageIndex == 2):
                    self.d.implicitly_wait(1)
                    find_Image2 = self.d.xpath('//*[@resource-id="com.lazada.android:id/flex_box"]/android.widget.RelativeLayout[2]/android.view.ViewGroup[1]/android.widget.FrameLayout[1]/android.widget.RelativeLayout[1]/android.widget.ImageView[1]').wait(1)
                    if (find_Image2 != None):
                        find_Image2.click()
                        time.sleep(1)
                    else:
                        find_Image21 = self.d.xpath('//*[@resource-id="com.lazada.android:id/flex_box"]/android.widget.RelativeLayout[2]/android.widget.RelativeLayout[1]').wait(1)
                        if (find_Image21 != None):
                            find_Image21.click()
                            time.sleep(1)
                
                self.d.click(0.483, 0.904)
                time.sleep(2)
                
            #click icon gio hang
            self.d(resourceId="com.lazada.android:id/cart").click(timeout=5)
            
        
        
        
        
                 
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("./bootleggers.jpg"))
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "Tool Điều Khiển Android"))
        
        #SHOW list ip may
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        
        self.showListDevice()
        
        #list file APK
        listFileAPKLZD = os.listdir('./APK/')
        listFileAPKLZD.pop(0)
        self.comboBoxListAppLZD.addItems(listFileAPKLZD)
        
        item = listFileAPKLZD[len(listFileAPKLZD)-1]
        self.comboBoxListAppLZD.setCurrentText(item)
        
       

        self.MyThreads = []
        self.pushButton_Start.clicked.connect(self.Start)
        #self.pushButton.clicked.connect(lambda: self.getDuLieuCSV('32daea2'))
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.contextMenuEvent)
        self.label_CountAccReg.setText(str(self.getCountAccount()))
        self.lineEdit_DefaultPassLZD.setText(str("Sang123"))
        
        self.btngroup1 = QtWidgets.QButtonGroup()
        self.btngroup2 = QtWidgets.QButtonGroup()
        
        #self.radioButton_NgauNhienAppLZD.setChecked(True)
        self.btngroup1.addButton(self.radioButton_NgauNhienAppLZD)
 
        
        self.btngroup2.addButton(self.radioButton_FullWipe)
        self.btngroup2.addButton(self.radioButton_KhongWipe)
        self.btngroup2.addButton(self.radioButton_LayLaiMatKhau)
        self.btngroup2.addButton(self.radioButton_LayLaiMatKhau_2)
        
        self.showDataKhoDatHang()
        
        self.pushButton_RefreshKhoDatHang.clicked.connect(
            self.showDataKhoDatHang)
        
        # button Cap Nhat Trang Thai
        self.pushButton_CapNhatTrangThaiKhoDatHang.clicked.connect(
            self.capNhatTrangThaiKhoDatHang)
        
        # copy tai khoan && mat khau
        self.pushButton_CopyTaiKhoanKhoDatHang.clicked.connect(
            self.copyTaiKhoanKhoDatHang)
        
        # detect selected cell tableWidget_KhoDuLieuDatHang
        self.listAccountSelected = []
        self.tableWidget_KhoDuLieuDatHang.selectionModel(
        ).selectionChanged.connect(self.checkSelectAcc)
    
    def checkSelectAcc(self, selected, deselected):
    
        for ix in selected.indexes():
            value = ix.sibling(ix.row(), ix.column()).data()
            self.listAccountSelected.append(value)

        for ix in deselected.indexes():
            value = ix.sibling(ix.row(), ix.column()).data()
            self.listAccountSelected.remove(value)
            
    def copyTaiKhoanKhoDatHang(self):
        row_number = self.tableWidget_KhoDuLieuDatHang.rowCount()
        print("Tong acc: " + str(row_number))
        data = {
            "username": [],
            "password": [],
            "status": [],
        }
        for i in range(row_number):
            username = (self.tableWidget_KhoDuLieuDatHang.item(i, 0).text())
            password = (self.tableWidget_KhoDuLieuDatHang.item(i, 1).text())
            status = (self.tableWidget_KhoDuLieuDatHang.item(i, 4).text())

            data["username"].append(username)
            data["password"].append(password)
            data["status"].append(status)

        df = pd.DataFrame(data)
        df.to_clipboard(index=False, header=False)
        print(df)

        msg = QMessageBox()
        msg.setText("Đã Copy " + str(row_number) +
                    " Tài Khoản Kho Đặt Hàng Lazada")
        x = msg.exec_()
        
    def showListDevice(self):
        os.system('adb devices')
        time.sleep(1)
        
        client = AdbClient(host="127.0.0.1", port=5037)
        devices = client.devices()
        
        
        file = open("./Config/listDevice.txt", "r", encoding="utf-8")
        allDevice = file.readlines()
        
        for line in allDevice:
            device = line.strip().split("|")
            for item in devices:
                if (item.serial == device[0]):
                    row_number = self.tableWidget.rowCount()
                    self.tableWidget.insertRow(row_number)
                    
                    chkBoxItem = QtWidgets.QTableWidgetItem(str(device[1]))
                    chkBoxItem.setText(str(device[1]))
                    chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    chkBoxItem.setCheckState(QtCore.Qt.Checked)
                    self.tableWidget.setItem(row_number, 0, chkBoxItem)
                    self.tableWidget.setItem(row_number, 1,  QtWidgets.QTableWidgetItem(str(device[0])))
                    self.tableWidget.setItem(row_number, 2,  QtWidgets.QTableWidgetItem(str("Init")))
        
    def showDataCSV(self):
        
        self.tableWidget_2.setRowCount(0)
        
        df = pandas.read_csv("./Config/napDuLieu.csv",skipinitialspace=True,keep_default_na=False)
    
        row_count, column_count = df.shape
        for i in range(row_count):
            
            row_number = self.tableWidget_2.rowCount()
            self.tableWidget_2.insertRow(row_number)
            
            splitFacebook = df["Facebook"][i].split('|')
            splitMail = df["Mail"][i].split('|')
            
            uid = splitFacebook[0]
            passFB = splitFacebook[1]
            mail = splitMail[0]
            passMail = splitMail[1]
            LZD = df["LZD"][i]
            passLZD = df["passLZD"][i]
            deviceName = df["deviceName"][i]
            isGet = df["isGet"][i]
            
            #isRegFB = df["isRegFB"][i]
            isRegLZD = df["isRegLZD"][i]
            status = df["status"][i]
            if (status == 'true'):
                status = "Reg LZD Done"
           
            versionAppLZD = df["versionAppLZD"][i]
            
            
            self.tableWidget_2.setItem(row_number,0,QtWidgets.QTableWidgetItem(str(LZD)))
            self.tableWidget_2.setItem(row_number,1,QtWidgets.QTableWidgetItem(str(passLZD)))
            self.tableWidget_2.setItem(row_number,2,QtWidgets.QTableWidgetItem(str(uid)))
            self.tableWidget_2.setItem(row_number,3,QtWidgets.QTableWidgetItem(str(passFB)))

            self.tableWidget_2.setItem(row_number,4,QtWidgets.QTableWidgetItem(str(isGet)))
            self.tableWidget_2.setItem(row_number,5,QtWidgets.QTableWidgetItem(str(isRegLZD)))
            self.tableWidget_2.setItem(row_number,6,QtWidgets.QTableWidgetItem(str(versionAppLZD)))

            self.tableWidget_2.setItem(row_number,7,QtWidgets.QTableWidgetItem(str(deviceName)))
            self.tableWidget_2.setItem(row_number,8,QtWidgets.QTableWidgetItem(str(status)))
            # self.tableWidget_2.setItem(row_number,11,QtWidgets.QTableWidgetItem(str(versionAppLZD)))    

    def contextMenuEvent(self, event):
        contextMenu = QtWidgets.QMenu(self)
       
        chonTatCaAction = contextMenu.addAction(emoji.emojize(":check_mark_button: Chọn Tất Cả :check_mark_button:"))
        chonNguocAction = contextMenu.addAction("!!! Chọn Ngược !!!")
        boChonAction = contextMenu.addAction(emoji.emojize(":multiply: Bỏ Chọn :multiply:"))
        viewAction = contextMenu.addAction(emoji.emojize(":mobile_phone: Xem Phone :mobile_phone:"))
        cancelAction = contextMenu.addAction(emoji.emojize(":name_badge: Tắt Xem Phone :name_badge:"))
        wipeAction = contextMenu.addAction(emoji.emojize(":mushroom: 1 - Wipe Máy "))
        caiAppAction = contextMenu.addAction(emoji.emojize(":toolbox: 2 - Gỡ && Cài App LZD"))
        clickHopQuaAction = contextMenu.addAction(emoji.emojize(":last_quarter_moon: 3- Click Hop Qua"))
        onlyDangNhapLZDActionNew = contextMenu.addAction(emoji.emojize(":lady_beetle: 4 - [Only] -- Chỉ Đăng Nhập LZD"))
        
        dangNhapLZDAction = contextMenu.addAction(emoji.emojize(":large_blue_diamond: 5 - [Đăng Nhập Lại LZD]"))
        moLinkSanPhamAction = contextMenu.addAction(emoji.emojize(":laptop: 6 - Mở Link Sản Phẩm"))
        themGioHangAction = contextMenu.addAction(emoji.emojize(":large_orange_diamond: 7 - Thêm Giỏ Hàng"))
        
        diaChiThuongTinAction = contextMenu.addAction(emoji.emojize(":last_quarter_moon: Add Địa Chỉ Hà Nội - Thường Tín"))
        diaChiQuan10Action = contextMenu.addAction(emoji.emojize(":last_quarter_moon: Dien Thong Tin Dia Chi"))
        kiemTraVoucherAction = contextMenu.addAction(emoji.emojize(":laptop: Kiểm Tra Mã Giảm Giá"))
        


        action = contextMenu.exec_(self.mapToGlobal(event))
        
        if action == chonTatCaAction:
            print("Chọn Tất Cả")
            for i in range(self.tableWidget.rowCount()):
                self.tableWidget.item(i, 0).setCheckState(QtCore.Qt.Checked)
        elif action == chonNguocAction:
            print("Chọn Ngược")
            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    self.tableWidget.item(
                        i, 0).setCheckState(QtCore.Qt.Unchecked)
                else:
                    self.tableWidget.item(
                        i, 0).setCheckState(QtCore.Qt.Checked)
        elif action == boChonAction:
            print("Bỏ Chọn Tất Cả")
            for i in range(self.tableWidget.rowCount()):
                self.tableWidget.item(i, 0).setCheckState(QtCore.Qt.Unchecked)
        if action == viewAction:
            # self.startThreads()

            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            windowX = 1635
            index = 0
            for device in checkListDevice:
                
                #calculate sort scrcpy
                x = windowX - 280*index
                cmd = "scrcpy -s " + device + " --max-size 550 --window-x "+ str(x)+ " --window-y 30 --window-title " + device + " --stay-awake"
                index = index + 1
                # 2. Instantiate the subclass of QRunnable
                runnable = Runnable(cmd, device)
                runnable.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(runnable.runViewPhone)
                time.sleep(1)
        elif action == wipeAction:
            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            for device in checkListDevice:
            
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = "", versionAppLZD= "")
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(runnableRemote.wipeSachMay)
                time.sleep(1)
                
        elif action == caiAppAction:
            
            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            for device in checkListDevice:
                
                listFileAPKLZD = os.listdir('./APK/')
                listFileAPKLZD.pop(0)
                if (self.radioButton_NgauNhienAppLZD.isChecked()):
                    versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
                else:
                    versionAppLZD = self.comboBoxListAppLZD.currentText()
                    print("Phien ban app da chon: " + versionAppLZD)

                #ngau nhien app
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = "", versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(runnableRemote.goVaCaiApp)
        
        elif action == clickHopQuaAction:
            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            for device in checkListDevice:
                
                listFileAPKLZD = os.listdir('./APK/')
                listFileAPKLZD.pop(0)
                if (self.radioButton_NgauNhienAppLZD.isChecked()):
                    versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
                else:
                    versionAppLZD = self.comboBoxListAppLZD.currentText()
            
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = "", versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(runnableRemote.clickTatHopQua)
                
        elif action == cancelAction:
            os.system("taskkill /im scrcpy.exe")
            
       
                
                
        elif action == dangNhapLZDAction:
            
            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            for device in checkListDevice:
                
                listFileAPKLZD = os.listdir('./APK/')
                listFileAPKLZD.pop(0)
                if (self.radioButton_NgauNhienAppLZD.isChecked()):
                    versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
                else:
                    versionAppLZD = self.comboBoxListAppLZD.currentText()
            
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = "", versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(runnableRemote.dangNhapLai)
                
        elif action == themGioHangAction:
            
            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            for device in checkListDevice:
                
                listFileAPKLZD = os.listdir('./APK/')
                listFileAPKLZD.pop(0)
                
                if (self.radioButton_NgauNhienAppLZD.isChecked()):
                    versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
                else:
                    versionAppLZD = self.comboBoxListAppLZD.currentText()
                #versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
            
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = "", versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(runnableRemote.ThemGioHang)
                
                
        elif action == onlyDangNhapLZDActionNew:
            
            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            for device in checkListDevice:
                
                listFileAPKLZD = os.listdir('./APK/')
                listFileAPKLZD.pop(0)
                if (self.radioButton_NgauNhienAppLZD.isChecked()):
                    versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
                else:
                    versionAppLZD = self.comboBoxListAppLZD.currentText()
            
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = "", versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(runnableRemote.ChiDangNhapBangMatKhau)
                
        elif action == diaChiThuongTinAction:
            
            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            for device in checkListDevice:
                
                listFileAPKLZD = os.listdir('./APK/')
                listFileAPKLZD.pop(0)
                versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
            
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = "", versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(lambda: runnableRemote.addDiaChi("HaNoi"))
                time.sleep(0.5)
                
        elif action == diaChiQuan10Action:
            
            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            for device in checkListDevice:
                
                listFileAPKLZD = os.listdir('./APK/')
                listFileAPKLZD.pop(0)
                versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
            
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = "", versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(lambda: runnableRemote.dienThongTinDiaChi())
                
        elif action == kiemTraVoucherAction:
            
            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            for device in checkListDevice:
                
                listFileAPKLZD = os.listdir('./APK/')
                listFileAPKLZD.pop(0)
                versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
            
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = "", versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(runnableRemote.XemVoucher)
                
        elif action == moLinkSanPhamAction:
            
            pool = QThreadPool.globalInstance()
            client = AdbClient(host="127.0.0.1", port=5037)

            checkListDevice = []

            for i in range(self.tableWidget.rowCount()):
                if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                    checkListDevice.append(self.tableWidget.item(i, 1).text())

            for device in checkListDevice:
                
                listFileAPKLZD = os.listdir('./APK/')
                listFileAPKLZD.pop(0)
                versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
            
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = "", versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(lambda: runnableRemote.moLinkSanPham(self.lineEdit.text()))
                
    def reloadData(self):
        self.showDataCSV()
        #QtCore.QTimer.singleShot(1000,self.showDataCSV)

    def print_output(self, s):
        #self.reloadData()
        self.UpdateTrangThai(s["serialNumber"], s["status"])

    def Start(self):
        
        self.showDataCSV()
        
        pool = QThreadPool.globalInstance()
        client = AdbClient(host="127.0.0.1", port=5037)

        checkListDevice = []

        for i in range(self.tableWidget.rowCount()):
            if (self.tableWidget.item(i, 0).checkState() == QtCore.Qt.Checked):
                checkListDevice.append(self.tableWidget.item(i, 1).text())

        for device in checkListDevice:
            passLZD = self.lineEdit_DefaultPassLZD.text()
            #list App LZD
            listFileAPKLZD = os.listdir('./APK/')
            listFileAPKLZD.pop(0)
            if (self.radioButton_NgauNhienAppLZD.isChecked()):
                versionAppLZD = listFileAPKLZD[random.randrange(0, len(listFileAPKLZD)-1)]
            else:
                versionAppLZD = self.comboBoxListAppLZD.currentText()
                
            if (self.radioButton_FullWipe.isChecked()):
                # 2. Instantiate the subclass of QRunnable
                runnableRemote = Remote(deviceName = device, passLZD = passLZD, versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(runnableRemote.runFullWipe)
                time.sleep(0.5)

            elif (self.radioButton_KhongWipe.isChecked()):
                runnableRemote = Remote(deviceName = device, passLZD = passLZD, versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                # 3. Call start()
                pool.start(runnableRemote.runKhongWipe)
                time.sleep(0.5)
                
            elif(self.radioButton_LayLaiMatKhau.isChecked()):
                print("Add Mail Full")
                runnableRemote = Remote(deviceName = device, passLZD = passLZD, versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                runnableRemote.resultAccount.connect(self.capNhatSoLuongAcc)
                # 3. Call start()
                pool.start(runnableRemote.runLayLaiMatKhau)
                time.sleep(0.5)
                
            elif(self.radioButton_LayLaiMatKhau_2.isChecked()):
                print("Chi Lay Lai Mat Khau")
                runnableRemote = Remote(deviceName = device, passLZD = passLZD, versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                runnableRemote.resultAccount.connect(self.capNhatSoLuongAcc)
                # 3. Call start()
                pool.start(runnableRemote.runLayLaiMatKhau_2)
                time.sleep(0.5)
            elif(self.radioButton_DiaChiThuongTin.isChecked()):
                
                runnableRemote = Remote(deviceName = device, passLZD = passLZD, versionAppLZD= versionAppLZD)
                runnableRemote.signals.result.connect(self.print_output)
                #runnableRemote.resultAccount.connect(self.capNhatSoLuongAcc)
                # 3. Call start()
                pool.start(runnableRemote.addDiaChi)
                
        self.showDataCSV()       
    
    def capNhatSoLuongAcc(self):
        self.label_CountAccReg.setText(str(self.getCountAccount()))         

    def UpdateTrangThai(self, serialNumber, status):
        column = 0

        for row in range(self.tableWidget.rowCount()):
            item = self.tableWidget.item(row, 1)

            if (item.text() == serialNumber):
                self.tableWidget.item(row, 2).setText(status)
                
    def getCountAccount(self):
        
        df = pandas.read_csv("./Config/accLazadaThanhCong.csv",skipinitialspace=True,keep_default_na=False)
    
        row_count, column_count = df.shape
        
        
        return row_count + 1

    
    def showDataKhoDatHang(self):
        
        header = self.tableWidget_KhoDuLieuDatHang.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.Stretch)

        self.tableWidget_KhoDuLieuDatHang.setRowCount(0)

        apiViewKhoDatHang = "https://lzd420.me/api/getkhodathang"
        response = requests.get(apiViewKhoDatHang)
        jsonData = response.json()["data"]

        if len(jsonData) > 0:
            for account in jsonData:
                row_number = self.tableWidget_KhoDuLieuDatHang.rowCount()
                self.tableWidget_KhoDuLieuDatHang.insertRow(row_number)

                self.tableWidget_KhoDuLieuDatHang.setItem(
                    row_number, 0, QtWidgets.QTableWidgetItem(str(account["username"])))
                self.tableWidget_KhoDuLieuDatHang.setItem(
                    row_number, 1, QtWidgets.QTableWidgetItem(str(account["password"])))
                self.tableWidget_KhoDuLieuDatHang.setItem(
                    row_number, 2, QtWidgets.QTableWidgetItem(str(account["deviceName"])))
                if (account["isGet"] == True):
                    self.tableWidget_KhoDuLieuDatHang.setItem(
                        row_number, 3, QtWidgets.QTableWidgetItem(str("Đã Lấy")))
                else:
                    self.tableWidget_KhoDuLieuDatHang.setItem(
                        row_number, 3, QtWidgets.QTableWidgetItem(str("")))

                self.tableWidget_KhoDuLieuDatHang.setItem(
                    row_number, 4, QtWidgets.QTableWidgetItem(str(account["status"])))
                
    def capNhatTrangThaiKhoDatHang(self):
    
        print(self.listAccountSelected)

        for account in self.listAccountSelected:
            apiUpdateTrangThai = "https://lzd420.me/api/updateTrangThaiKhoDatHang"
            dataPost = {
                "username": account,
                "status": self.lineEdit_Status.text(),
                "owner": "admin"
            }

            jsonData = json.dumps(dataPost)

            response = requests.post(apiUpdateTrangThai, dataPost)
            print(response.json())

        self.showDataKhoDatHang()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
