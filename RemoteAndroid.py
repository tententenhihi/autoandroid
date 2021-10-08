import uiautomator2 as u2
import os
import io
import time
import outlook
import subprocess
import random
import sys
import requests
from ppadb.client import Client as AdbClient
import pandas as pd
# Default is "127.0.0.1" and 5037


def getDevice(serialNumber):
    os.system('adb devices')
    time.sleep(1)
    
    adb = AdbClient(host="127.0.0.1", port=5037)

    listDevice = adb.devices()

    for device in listDevice:
        if (device.serial == serialNumber):
            return device



def wait(number):
    for x in range(number):
        second = x+1
        print("Chờ " + str(second) + " giây")
        time.sleep(1)
    return True


def caiDatFileAPK(serialNumber, facebookAPK, lazadaAPK):

    print("Đang cài Facebook và LZD.........")
    device = getDevice(serialNumber)
    print(device)
    # installLazada = device.install("./APK/lazada_580.apk")
    installLazada = device.install(facebookAPK)
    installFacebook = device.install(lazadaAPK)

    if (installLazada == True and installFacebook == True):
        print("Đã cài đặt xong LZD Và Facebook APK")


def goCaiDatFileAPK(serialNumber):
    print("Đang gỡ app Facebook và LZD.........")
    device = getDevice(serialNumber)
    unistallFacebook = device.uninstall("com.facebook.katana")
    unistallLazada = device.uninstall("com.lazada.android")
    if (unistallFacebook == True and unistallLazada == True):
        print("Đã gỡ cài đặt Facebook và Lazada")


def wipeSachMay(serialNumber):
    newDevice = getDevice(serialNumber)
    # vao che do fastboot
    result = newDevice.shell("reboot fastboot")
    print(result)

    # wipe sach data may
    os.system("fastboot devices")

    os.system("fastboot -w")
    print("Wipe Cache và Wipe Userdata")

    # reboot
    os.system("fastboot reboot")
    print("Reboot......")
    time.sleep(30)

    checkHomeScreen = newDevice.shell(
        "getprop sys.boot_completed | tr -d '\r'")

    i = 1
    while (checkHomeScreen != "1\n"):
        time.sleep(1)
        print("Wipe Recovery ... " + str(i))
        i = i + 1
        checkHomeScreen = newDevice.shell(
            "getprop sys.boot_completed | tr -d '\r'")

    if (checkHomeScreen == "1\n"):
        d = u2.connect(serialNumber)
        print("Wipe Done...")
        # set timeout display 30 minitues
        newDevice.shell("settings put system screen_off_timeout 1800000")


def doiIP4G(serialNumber):
    device = getDevice(serialNumber)

    # turn on may bay
    print("Bật máy bay")
    device.shell("settings put global airplane_mode_on 1")
    device.shell("am broadcast -a android.intent.action.AIRPLANE_MODE")

    print("Chờ 3s")
    time.sleep(3)

    # turn off may bay
    print("Tắt máy bay")
    device.shell("settings put global airplane_mode_on 0")
    device.shell("am broadcast -a android.intent.action.AIRPLANE_MODE")

    print("Chờ 4s")
    time.sleep(4)


def dangNhapFacebook(serialNumber):
    # init
    device = getDevice(serialNumber)
    dataAccount = DataAccountModel.DataAccount(serialNumber)
    dataAccount.getData()

    # uiautomator init
    d = u2.connect(serialNumber)
    print("Mo App Facebook")
    d.app_start("com.facebook.katana", use_monkey=True)

    # input uid
    d.implicitly_wait(10.0)
    find_inputUID = d(text="Phone or email")
    if (find_inputUID.wait(5)):
        find_inputUID.click()
        time.sleep(0.5)
        d.send_keys(dataAccount.uid)
        time.sleep(0.5)
    else:
        print("Fail")

    # input password
    find_inputPassword = d(text="Password")
    if (find_inputPassword.wait(5)):
        find_inputPassword.click()
        time.sleep(0.5)
        d.send_keys(dataAccount.passwordFB)
        time.sleep(0.5)
    else:
        print("Fail")

    # click DangNhap
    find_DangNhap = d(description="Log In", className="android.view.ViewGroup")
    if (find_DangNhap.wait(5)):
        find_DangNhap.click()
        time.sleep(5)
    else:
        print("Fail")

    # Skip
    find_Skip = d.xpath(
        '//android.view.ViewGroup/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').wait(10)
    if (find_Skip != None):
        print("Click bo qua")
        find_Skip.click()
        time.sleep(1)

    # Skip 2
    find_Skip2 = d.xpath(
        '//android.view.ViewGroup/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').wait(3)
    if (find_Skip2 != None):
        print("Click skip")
        find_Skip2.click()
        time.sleep(1)
    else:
        find_Skip22 = d.xpath('//*[@resource-id="android:id/content"]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]/android.view.ViewGroup[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').wait(3)
        if (find_Skip22 != None):
            find_Skip22.click()
            time.sleep(1)

    # click Skip3
    d.implicitly_wait(10.0)
    find_Skip3 = d(text="SKIP")
    if (find_Skip3.wait(5)):
        find_Skip3.click()
        time.sleep(2)
    else:
        print("Fail")

    # click NotNow
    fint_NotNow = d(text="Not Now")
    if (fint_NotNow.wait(5)):
        fint_NotNow.click()
        time.sleep(2)
    else:
        find_Skip4 = d.xpath(
            '//android.view.ViewGroup/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.LinearLayout[1]').wait(3)
        if (find_Skip4 != None):
            find_Skip4.click()
            time.sleep(1)

    # find deny
    find_Deny = d(description="Deny")
    if (find_Deny.wait(5)):
        find_Deny.click()
        time.sleep(1)

    # check Login Done
    find_CheckLogin = d.xpath(
        '//android.widget.FrameLayout[2]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]/android.widget.LinearLayout[1]/android.widget.ImageView[1]').wait(3)
    if (find_CheckLogin != None):
        print("Dang Nhap Thanh Cong")
    dataAccount.isLoginFB = True
    dataAccount.updateTrangThai()


def dangNhapLZD(serialNumber):
    # init
    device = getDevice(serialNumber)
    dataAccount = DataAccountModel.DataAccount(serialNumber)
    dataAccount.getData()

    # uiautomator init
    d = u2.connect(serialNumber)
    print("Mo App Lazada")
    d.app_start("com.lazada.android", use_monkey=True)

    # click bo qua
    find_boQua = d(resourceId="com.lazada.android:id/intro_skip_btn")
    d.implicitly_wait(4)
    if (find_boQua.wait(4)):
        print("Click bo qua")
        find_boQua.click()
        time.sleep(0.5)
    else:
        print("Fail click bo qua")

    find_tatHopQua = d(resourceId="com.lazada.android:id/close_button")
    d.implicitly_wait(4)
    if (find_tatHopQua.wait(4)):
        print("Click tat hop qua")
        find_tatHopQua.click()
        time.sleep(1)
    else:
        print("Fail tat hop qua 1")

    find_voucherThuThap = d(
        resourceId="com.lazada.android:id/iv_homepage_banner")
    d.implicitly_wait(4)
    if (find_voucherThuThap.wait(4)):
        d.click(0.901, 0.087)
    else:
        print("Fail tat hop qua 2")

    # click dang nhap ngay
    d.implicitly_wait(10.0)
    find_dangNhapNgay = d(resourceId="com.lazada.android:id/hp_login_button")
    if (find_dangNhapNgay.wait(5)):
        print("Click dang nhap ngay")
        find_dangNhapNgay.click()
        time.sleep(0.5)

    # click icon FB
    find_iconFB = d(resourceId="com.lazada.android:id/iv_facebook")
    if (find_iconFB.wait(5)):
        print("Click icon fb")
        find_iconFB.click()
        time.sleep(0.5)

        # click dong y
        find_dongY = d(resourceId="com.lazada.android:id/tv_agree")
        if (find_dongY.wait(5)):
            print("Click dong y")
            find_dongY.click()
            time.sleep(1)

        # find editInfo
        find_editInfo = d(text="Edit the info you provide")
        if (find_editInfo.wait(5)):
            print("Click edit")
            find_editInfo.click()
            time.sleep(2)

        # tat mail
        find_tatMail = d.xpath(
            '//androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[3]/android.widget.FrameLayout[1]').wait(5)
        if (find_tatMail != None):
            print("Click tat mail")
            find_tatMail.click()
            time.sleep(2)

        # click button continue
        find_btnContinue = d.xpath(
            '//androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[4]/android.widget.Button[1]').wait(5)
        if (find_btnContinue != None):
            print("Click continue ..... ")
            find_btnContinue.click()
            time.sleep(10)

        # click dien sau
        find_dienSau = d.xpath(
            '//android.webkit.WebView/android.view.View[1]/android.view.View[2]/android.view.View[1]').wait(20)
        if (find_dienSau != None):
            print("Click dien sau ....")
            find_dienSau.click()
            time.sleep(2)

        # find icon mgg
        find_MaGiamGia = d.xpath(
            '//*[@resource-id="com.lazada.android:id/laz_homepage_channels_horizontal_recycler"]/android.widget.LinearLayout[4]/android.widget.ImageView[1]').wait(10)
        if (find_MaGiamGia != None):
            print("Click ma giam gia .....")
            find_MaGiamGia.click()
            time.sleep(5)

            d.swipe_ext("up", scale=0.8)

            find_thuThapMoMo = d.xpath(
                '//*[@resource-id="8220582590"]/android.view.View[1]/android.view.View[2]/android.view.View[1]/android.view.View[2]/android.view.View[4]/android.view.View[1]').wait(5)
            if (find_thuThapMoMo != None):
                find_thuThapMoMo.click()
                time.sleep(1)
                find_suuTamThanhCong = d(
                    text='Sưu tầm thành công! Vào "Ví Voucher" để xem chi tiết.')
                if (find_suuTamThanhCong.wait(3)):
                    print("Sưu tầm mã thành công. Good Job !!!")
                else:
                    print("Tao acc fail")
                    dataAccount.isRegLZD = False
                    dataAccount.isLoginFB = True
                    sys.exit("Failed !!!!!!!")
            dataAccount.updateTrangThai()

    else:
        find_iconFB = d(
            resourceId="com.lazada.android:id/icf_login_app_auth_facebook")
        if (find_iconFB.wait(5)):
            print("Click icon fb")
            find_iconFB.click()
            time.sleep(0.5)
            # click dong y
        find_dongY = d(resourceId="android:id/button1")
        if (find_dongY.wait(5)):
            print("Click dong y")
            find_dongY.click()
            time.sleep(1)

        # find editInfo
        find_editInfo = d(text="Edit the info you provide")
        if (find_editInfo.wait(5)):
            print("Click edit")
            find_editInfo.click()
            time.sleep(2)
        # tat mail
        find_tatMail = d.xpath(
            '//androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[3]/android.widget.FrameLayout[1]').wait(5)
        if (find_tatMail != None):
            print("Click tat mail")
            find_tatMail.click()
            time.sleep(2)

        # click button continue
        find_btnContinue = d.xpath(
            '//androidx.recyclerview.widget.RecyclerView/android.widget.LinearLayout[4]/android.widget.Button[1]').wait(5)
        if (find_btnContinue != None):
            print("Click continue ..... ")
            find_btnContinue.click()
            time.sleep(10)

        # click dien sau
        find_dienSau = d(text="Điền Sau")
        if (find_dienSau.wait(5)):
            print("Click dien sau ....")
            find_dienSau.click()
            time.sleep(2)

        # find icon mgg
        find_MaGiamGia = d.xpath(
            '//*[@resource-id="com.lazada.android:id/laz_homepage_channels_horizontal_recycler"]/android.widget.LinearLayout[4]/android.widget.ImageView[1]').wait(10)
        if (find_MaGiamGia != None):
            print("Click ma giam gia .....")
            find_MaGiamGia.click()
            time.sleep(5)

            d.swipe_ext("up", scale=0.8)

            find_thuThapMoMo = d.xpath(
                '//*[@resource-id="8220582590"]/android.view.View[1]/android.view.View[2]/android.view.View[1]/android.view.View[2]/android.view.View[4]/android.view.View[1]').wait(5)
            if (find_thuThapMoMo != None):
                find_thuThapMoMo.click()
                time.sleep(1)
                find_suuTamThanhCong = d(
                    text='Sưu tầm thành công! Vào "Ví Voucher" để xem chi tiết.')
                if (find_suuTamThanhCong.wait(3)):
                    print("Sưu tầm mã thành công. Good Job !!!")
                else:
                    print("Tao acc fail")
                    dataAccount.isRegLZD = False
                    dataAccount.isLoginFB = True
                    sys.exit("Failed !!!!!!!")
            dataAccount.updateTrangThai()


def addMailLazada(serialNumber):
    # init
    device = getDevice(serialNumber)
    dataAccount = DataAccountModel.DataAccount(serialNumber)
    dataAccount.getData()

    # uiautomator init
    d = u2.connect(serialNumber)

    # click 3 dam
    find_dau3Cham = d(description="Tùy chọn khác")
    if (find_dau3Cham.wait(3)):
        print("Click dau 3 cham")
        find_dau3Cham.click()
        time.sleep(0.5)

    # click tai khoan cua toi
    find_taiKhoanCuaToi = d.xpath(
        '//android.widget.ListView/android.widget.LinearLayout[3]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[1]').wait(5)
    if (find_taiKhoanCuaToi != None):
        print("Click tai khoan cua toi...")
        find_taiKhoanCuaToi.click()
        time.sleep(1)

    # guide Content
    d.implicitly_wait(2)
    find_guideContent = d(resourceId="com.lazada.android:id/btn_guide_content")
    if (find_guideContent.wait(2)):
        print("Click ok")
        find_guideContent.click()
        time.sleep(0.5)
    else:
        d.implicitly_wait(1)
        find_daHieu = d(resourceId="com.lazada.android:id/txt_gotit")
        if (find_daHieu.wait(1)):
            print("Click da hieu")
            find_daHieu.click()
            time.sleep(0.5)
    # setting
    d.implicitly_wait(2)
    find_setting = d(resourceId="com.lazada.android:id/iv_settings")
    if (find_setting.wait(2)):
        print("Click setting")
        find_setting.click()
        time.sleep(1)
    else:
        find_settingVer580 = d(resourceId="com.lazada.android:id/tv_settings")
        if (find_settingVer580.wait(2)):
            print("Click setting ver 580")
            find_settingVer580.click()
            time.sleep(1)
    # thong tin tai khoan
    find_thongTinTaiKhoan = d(
        resourceId="com.lazada.android:id/setting_account_information_container")
    if (find_thongTinTaiKhoan.wait(5)):
        print("Click thong tin tai khoan")
        find_thongTinTaiKhoan.click()
        time.sleep(0.5)

    # them email
    find_themEmail = d(description="Thêm email")
    if (find_themEmail.wait(5)):
        print("Click them email")
        find_themEmail.click()
        time.sleep(0.5)
    # input mail
    find_inputMail = d.xpath('//android.widget.EditText').wait(10)
    if (find_inputMail != None):
        print("input mail")
        find_inputMail.click()
        time.sleep(1)
        d.send_keys(dataAccount.mail)
        time.sleep(1)

    # btn gui ma
    find_guiMa = d.xpath('//*[@resource-id="com.lazada.android:id/weex_render_view"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]').wait(5)
    if (find_guiMa != None):
        print("Click gui ma")
        find_guiMa.click()
        time.sleep(7)
        print("Get API OTP LZD")
        otpTempLZD = outlook.apiOTPLZD(dataAccount.mail, dataAccount.passMail)
        print(otpTempLZD)

        # input otp
        find_inputOTP = d.xpath('//*[@resource-id="com.lazada.android:id/weex_render_view"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[2]/android.widget.FrameLayout[2]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.EditText[1]')
        if (find_inputOTP.exists):
            find_inputOTP.click()
            time.sleep(1)
            d.send_keys(otpTempLZD)
            time.sleep(0.5)
            # click them email
            find_btnThemEmail = d(description="Thêm email")
            if (find_btnThemEmail.wait(5)):
                print("Click them email")
                find_btnThemEmail.click()
                time.sleep(1)
        # dau 3 cham
        find_dau3Cham = d(description="Tùy chọn khác")
        if (find_dau3Cham.wait(5)):
            print("Click dau 3 cham")
            find_dau3Cham.click()
            time.sleep(1)

        # tai khoan cua toi
        find_taiKhoanCuaToi = d.xpath(
            '//android.widget.ListView/android.widget.LinearLayout[3]/android.widget.LinearLayout[1]/android.widget.RelativeLayout[1]').wait(5)
        if (find_taiKhoanCuaToi != None):
            print("Click tai khoan cua toi")
            find_taiKhoanCuaToi.click()
            time.sleep(0.5)

        # guide Content
        d.implicitly_wait(3)
        find_guideContent = d(
            resourceId="com.lazada.android:id/btn_guide_content")
        if (find_guideContent.wait(3)):
            print("Click ok")
            find_guideContent.click()
            time.sleep(0.5)

        # setting
        d.implicitly_wait(2)
        find_setting = d(resourceId="com.lazada.android:id/iv_settings")
        if (find_setting.wait(2)):
            print("Click setting")
            find_setting.click()
            time.sleep(1)
        else:
            find_settingVer580 = d(
                resourceId="com.lazada.android:id/tv_settings")
            if (find_settingVer580.wait(2)):
                print("Click setting ver 580")
                find_settingVer580.click()
                time.sleep(1)

        # dang xuat
        find_dangXuat = d(text="Đăng xuất")
        if (find_dangXuat.wait(5)):
            print("Click dang xuat")
            find_dangXuat.click()
            time.sleep(0.5)

        # button dang xuat
        find_btnDangXuat = d(resourceId="android:id/button1")
        if (find_btnDangXuat.wait(5)):
            print("Click dang xuat")
            find_btnDangXuat.click()
            time.sleep(0.5)


def truot(serialNumber):
    d = u2.connect(serialNumber)
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
    print(listXY)

    d.swipe_points(listXY, 0.2)


def layLatMatKhauLazada(serialNumber):
    # init
    device = getDevice(serialNumber)
    dataAccount = DataAccountModel.DataAccount(serialNumber)
    dataAccount.getData()

    # uiautomator init
    d = u2.connect(serialNumber)

    # button dang nhap
    d.implicitly_wait(3)
    find_btnDangNhap = d(resourceId="com.lazada.android:id/tv_signup")
    if (find_btnDangNhap.wait(3)):
        print("Click dang nhap")
        find_btnDangNhap.click()
        time.sleep(2)
    else:
        find_btnDangNhapVer580 = d(
            resourceId="com.lazada.android:id/txt_login_signup")
        if (find_btnDangNhapVer580.wait(3)):
            print("Click btn dang nhap ver 580")
            find_btnDangNhapVer580.click()
            time.sleep(2)

    # dang nhap bang tai khoan khac
    d.implicitly_wait(2)
    find_switchAccount = d(
        resourceId="com.lazada.android:id/tv_switch_account")
    if (find_switchAccount.wait(2)):
        print("Click dang nhap bang tai khoan khac")
        find_switchAccount.click()
        time.sleep(1)

    # btn sign in
    find_btnSignIn = d(resourceId="com.lazada.android:id/tv_signin")
    if (find_btnSignIn.wait(5)):
        print("Click dang nhap")
        find_btnSignIn.click()
        time.sleep(1)

    # btn Forget password
    d.implicitly_wait(10.0)
    find_btnForgetPassword = d(
        resourceId="com.lazada.android:id/tv_forget_pwd")
    if (find_btnForgetPassword.wait(5)):
        print("Click quen mat khau")
        find_btnForgetPassword.click()
        time.sleep(1.5)

    # input mail
    find_btnInputMail = d(resourceId="com.lazada.android:id/et_input_text")
    if (find_btnInputMail.wait(5)):
        print("Input mail: " + dataAccount.mail)
        find_btnInputMail.click()
        time.sleep(1)
        d.send_keys(dataAccount.mail)

    # btn TiepTuc
    find_btnTiepTuc = d(resourceId="com.lazada.android:id/btn_next")
    if (find_btnTiepTuc.wait(5)):
        print("Click btn Tiep Tuc")
        find_btnTiepTuc.click()
        time.sleep(2)
    # find truot
    find_Truot = d.xpath(
        '//*[@resource-id="nc_1-stage-1"]/android.view.View[1]/android.view.View[2]').wait(10)
    if (find_Truot != None):
        print("Truot")
        truot(serialNumber)
        time.sleep(1)

    # find xac minh qua email
    find_xacMinhQuaMail = d(text="Xác minh qua email")
    if (find_xacMinhQuaMail.wait(5)):
        print("Click xac minh qua email")
        find_xacMinhQuaMail.click()
        time.sleep(1.5)

    # btn gui ma
    find_btnGuiMa = d.xpath(
        '//*[@resource-id="send-btn"]/android.view.View[1]').wait(10)
    if (find_btnGuiMa != None):
        print("Click gui ma")
        find_btnGuiMa.click()
        time.sleep(10)
        print("Get API OTP LZD")
        otpTempLZD = outlook.apiOTPLZD(dataAccount.mail, dataAccount.passMail)
        print(otpTempLZD)

        # input OTP
        find_inputOTP = d(resourceId="number")
        if (find_inputOTP.wait(5)):
            print("Click input otp: " + otpTempLZD)
            find_inputOTP.click()
            d.send_keys(otpTempLZD)

        # click button xac minh ma
        find_btnXacMinhMa = d(resourceId="main-btn")
        if (find_btnXacMinhMa.wait(5)):
            print("Click xac minh ma")
            find_btnXacMinhMa.click()
            time.sleep(2)

    # dien mat khau
    find_inputPWD = d.xpath(
        '//*[@resource-id="com.lazada.android:id/input_laz_reset_password"]/android.widget.RelativeLayout[1]/android.widget.EditText[1]').wait(10)
    if (find_inputPWD != None):
        print("Click input mat khau")
        find_inputPWD.click()
        time.sleep(1)
        d.send_keys(dataAccount.passwordLZD)
        time.sleep(1)

    find_inputAgainPWD = d.xpath(
        '//*[@resource-id="com.lazada.android:id/input_laz_reset_password_again"]/android.widget.RelativeLayout[1]/android.widget.EditText[1]').wait(5)
    if (find_inputAgainPWD != None):
        find_inputAgainPWD.click()
        time.sleep(1)
        d.send_keys(dataAccount.passwordLZD)
        time.sleep(1)

    # btn Dat Lai Mat Khau
    find_btnDatLaiMatKhau = d(
        resourceId="com.lazada.android:id/btn_laz_form_supply_complete")
    if (find_btnDatLaiMatKhau.wait(5)):
        find_btnDatLaiMatKhau.click()

     # cap nhat du lieu len server
    dataAccount.isRegLZD = True
    dataAccount.isLoginFB = True
    dataAccount.status = "true"
    dataAccount.updateTrangThai()
    dataAccount.addAccountVaoServer()


def HuyLienKetFacebook(serialNumber):

    d = u2.connect(serialNumber)
    # setting
    d.implicitly_wait(2)
    find_setting = d(resourceId="com.lazada.android:id/iv_settings")
    if (find_setting.wait(2)):
        print("Click setting")
        find_setting.click()
        time.sleep(1)
    else:
        find_settingVer580 = d(
            resourceId="com.lazada.android:id/tv_settings")
        if (find_settingVer580.wait(2)):
            print("Click setting ver 580")
            find_settingVer580.click()
            time.sleep(1)
    # thong tin tai khoan
    find_thongTinTaiKhoan = d(
        resourceId="com.lazada.android:id/setting_account_information_container")
    if (find_thongTinTaiKhoan.wait(5)):
        print("Click thong tin tai khoan")
        find_thongTinTaiKhoan.click()
        time.sleep(2)

    # find tai khoan mang xa hoi
    find_taiKhoanMangXaHoi = d(description="Tài khoản mạng xã hội")
    if (find_taiKhoanMangXaHoi.wait(5)):
        print("Click tai khoan mang xa hoi")
        find_taiKhoanMangXaHoi.click()
        time.sleep(2)

    d.implicitly_wait(10.0)
    find_iconFB = d.xpath('//*[@resource-id="com.lazada.android:id/weex_render_view"]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.FrameLayout[1]/android.widget.ImageView[1]').wait(10)
    if (find_iconFB != None):
        print("Click icon fb")
        find_iconFB.click()
        time.sleep(1)

    # find huy lien ket
    d.implicitly_wait(5)
    find_huyLienKet = d(description="Hủy liên kết")
    if (find_huyLienKet.wait(5)):
        print("Click huy lien ket")
        find_huyLienKet.click()
        time.sleep(3)

    # find btn xac nhan
    print("Click xac nhan")
    d.click(0.668, 0.611)


def moLink(serialNumber):
    d = u2.connect(serialNumber)
    newDevice = getDevice(serialNumber)
    link = "https://pages.lazada.vn/wow/i/vn/marketing/lcnclp?hybrid=1&item=838104565,1304846640,978650064&source=homepage_free_buy&spm=a211g0.home.newusercard.product2&scm=1007.27005.189583.0&clickTrackInfo=doubleVoucherABTypeBackend%3A%7Citem_id%3A838104565%7CdiscountPrice%3A18430.00%7CdoubleVoucherABType%3A%7Csku_id%3A2333356189%7Cprogram%3A44288%7Csource%3AHP_FREE%7Cscene%3A20492%7Cabid%3A221972%7CminOrderAmount%3A0.0%7Cpos%3A1%7Cpvid%3A44f7fda7-4f14-4ce5-bcca-c319ae6fed7a%7Cprice%3A69000.00%7Cfilter_cate_id%3A-1%7Cexp_bucket%3A20492%230%23221972%2310_20492%2316185648748315%23137280%23-1_20492%2316168312643731%23119133%23-1_20492%2316203641938168%23129133%23-1_20492%2316203694745843%23129198%23-1_20492%2316203700796101%23129211%23-1_20492%2316209719598916%23131354%23-1_20492%2316218361849460%23134281%23-1_20492%2316218594301418%23134808%23-1%7Cpoolid%3A7%7Cmatch_type%3AHOT%7Cvoucher_amount%3A30000.0%7Cposition%3A1%7Cscm%3A1007.30492.221972.%7CdiscountValue%3A30000.0"
    shellCMD = "am start -a android.intent.action.VIEW -d '" + link + "'"
    print(shellCMD)
    # vao che do fastboot
    
    resultShell = newDevice.shell(shellCMD)
    time.sleep(1)

    d.implicitly_wait(5)
    find_Lazada = d(resourceId="android:id/text1", text="Lazada")
    if (find_Lazada.wait(5)):
        print("Click LZD")
        find_Lazada.click()
        time.sleep(1)

        find_JustOnce = d(resourceId="android:id/button_once")
        if (find_JustOnce.wait(5)):
            print("Click Just Once")
            find_JustOnce.click()
            time.sleep(5)

    else:
        find_JustOnce = d(resourceId="android:id/button_once")
        if (find_JustOnce.wait(5)):
            print("Click Just Once")
            find_JustOnce.click()
            time.sleep(5)
    print("Click Mo")
    d.click(0.661, 0.744)
    time.sleep(2)

    # tapHopHopQua = [{'x': 0.182, 'y': 0.58}, {
    #     'x': 0.498, 'y': 0.581}, {'x': 0.81, 'y': 0.58}]

    # randomClickHopQua = tapHopHopQua[random.randrange(
    #     0, len(tapHopHopQua))]
    # d.click(randomClickHopQua['x'], randomClickHopQua['y'])




class RemoteAndroid:
    usernameLZD = ""
    passwordLZD = ""
    link = ""
    uid = ""
    passwordFB = ""
    mail = ""
    passMail = ""
    passwordLZD = "Sang123"
    phoneNumber = ""
    status = ""
    otpFacebook = ""
    otpLazada = False
    isLoginFB = ""
    isRegLZD = False
    deviceName = ""
    owner = ""

    def getData(self):
        response = requests.get(
            "http://lzd420.me/API/getDataAndroid&devicename=" + self.deviceName + "&owner=admin")
        jsonData = response.json()

        if (jsonData["status"] == "success"):
            self.uid = jsonData["data"]["username"]
            self.passwordFB = jsonData["data"]["password"]
            self.mail = jsonData["data"]["mail"]
            self.passMail = jsonData["data"]["passMail"]
            self.isLoginFB = jsonData["data"]["isLoginFB"]
            self.isRegLZD = jsonData["data"]["isRegLZD"]
            self.owner = jsonData["data"]["owner"]
            print("Đã lấy dữ liệu")

    def updateTrangThai(self):
        
        if (self.isLoginFB == True):
            isLoginFBTemp = "true"
        else:
            isLoginFBTemp = "false"

        if (self.isRegLZD == True):
            isRegLZDTemp = "true"
        else:
            isRegLZDTemp = "false"

        dataPost = {
            'isLoginFB': isLoginFBTemp,
            'isRegLZD': isRegLZDTemp,
            'deviceName': self.deviceName,
            'owner': self.owner,
            'mail': self.mail
        }

        # create response
        response = requests.post(
            'http://lzd420.me/API/updateTrangThaiReg', dataPost)
        jsonData = response.json()
        print(jsonData)
        if (jsonData["success"] == True):
            print("Đã update trạng thái reg")

    def addAccountVaoServer(self):
        dataPost = {
            'isLoginFB': self.isLoginFB,
            'isRegLZD': self.isRegLZD,
            'deviceName': self.deviceName,
            'owner': self.owner,
            'mail': self.mail,
            'username': self.mail,
            'passwordLZD': self.passwordLZD,
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
