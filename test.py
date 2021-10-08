import time
import uiautomator2 as u2
import outlook
import requests
import pandas as pd
import emoji
import re
from unidecode import unidecode
import json


d = u2.connect("37e9ac95")

#click tai khoan

# Ha Noi
# for i in range(3):
#     d.swipe_ext ( "up" , scale = 0.95 )
#     time.sleep(1)

d.implicitly_wait(2)
find_DiaChiNew = d.xpath('//*[@resource-id="com.lazada.android:id/recyclerview"]/android.widget.RelativeLayout[4]/android.widget.LinearLayout[1]/android.widget.FrameLayout[1]').wait(2)
if (find_DiaChiNew != None):
    d.click(0.271, 0.459)
    time.sleep(1)
    

