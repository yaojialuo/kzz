import pyautogui
import time
import cv2
import mss
import numpy
import pytesseract
import keyboard
import os
import shutil
import winsound
import  sys
import  traceback
import stat
today=True
oldtx=""
duration=1
interval=0
count=0
srcbase=r"Z:\trade\kzz\detail"
dstbase = r"Z:\trade\kzz\upload"
skipday=3
startdate=""
enddate="20210401"
wait=False

def pause(e):
    global wait
    wait = True
    print(e)
#shift
#handler=keyboard.on_release_key('shift', pause)
# def getdate():
#     #Point(x=174, y=124)
#     #Point(x=276, y=144)
#     mon = {'top': 124, 'left': 174, 'width': 100, 'height': 25}
#     sct= mss.mss()
#     im = numpy.asarray(sct.grab(mon))
#     im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
#     text = pytesseract.image_to_string(im, lang='eng',
#            config='digits')
#
#     #print(text[:10])
#     return text[:10]
#     # cv2.imshow('Image', im)
#     # cv2.waitKey(0)
#
#     # cv2.destroyAllWindows()
def getOne():
    #操作
    pyautogui.press(['space'])
    time.sleep(0.01)
    #点击明细数据
    pyautogui.press(['up'])
    time.sleep(0.01)

    #点击导出
    # pyautogui.moveTo(681, 604,duration)
    # pyautogui.click()
    pyautogui.press(['enter'])
    time.sleep(0.01)
    #keyboard.wait('ctrl')
    #点击确定
    pyautogui.press(['tab'],presses=2,interval=0.01)
    time.sleep(0.01)
    pyautogui.press(['enter'])
    time.sleep(0.1)
    # pyautogui.moveTo(532, 526,duration)
    # pyautogui.click()

    #直接取消
    pyautogui.press(['tab'])
    time.sleep(0.01)
    pyautogui.press(['enter'])
    time.sleep(0.1)

#['\t', '\n', '\r', ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '{', '|', '}', '~', 'accept', 'add', 'alt', 'altleft', 'altright', 'apps', 'backspace', 'browserback', 'browserfavorites', 'browserforward', 'browserhome', 'browserrefresh', 'browsersearch', 'browserstop', 'shift', 'clear', 'convert', 'ctrl', 'ctrlleft', 'ctrlright', 'decimal', 'del', 'delete', 'divide', 'down', 'end', 'enter', 'esc', 'escape', 'execute', 'f1', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17', 'f18', 'f19', 'f2', 'f20', 'f21', 'f22', 'f23', 'f24', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'final', 'fn', 'hanguel', 'hangul', 'hanja', 'help', 'home', 'insert', 'junja', 'kana', 'kanji', 'launchapp1', 'launchapp2', 'launchmail', 'launchmediaselect', 'left', 'modechange', 'multiply', 'nexttrack', 'nonconvert', 'num0', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'num7', 'num8', 'num9', 'numlock', 'pagedown', 'pageup', 'pause', 'pgdn', 'pgup', 'playpause', 'prevtrack', 'print', 'printscreen', 'prntscrn', 'prtsc', 'prtscr', 'return', 'right', 'scrolllock', 'select', 'separator', 'shift', 'shiftleft', 'shiftright', 'sleep', 'space', 'stop', 'subtract', 'tab', 'up', 'volumedown', 'volumemute', 'volumeup', 'win', 'winleft', 'winright', 'yen', 'command', 'option', 'optionleft', 'optionright']

def move(count):
    for root, dirs, files in os.walk(srcbase):
        for file in files:
            prefix = os.path.splitext(file)[0]
            ext = os.path.splitext(file)[1]
            date = prefix[:8]
            id = prefix[9:]
            id=str(count)+"_"+id
            path = os.path.join(dstbase, id)
            if not os.path.isdir(path):
                os.mkdir(path)

            src = os.path.join(srcbase, file)
            dst = os.path.join(dstbase, id, date)

            shutil.move(src, dst)

def getfinish(dirdict):
    dirs = []
    # (root,dirs,files) = os.walk(dstbase)
    dirs = os.listdir(dstbase)

    for dir in dirs:
        count = dir[:-7]
        dirdict[count] = dir
        #print(count)

    for id in dirdict.values():
        path=os.path.join(dstbase , id)
        files = os.listdir(path)

        if files[-1] != enddate:
            print(id, files[0], files[-1])
            print("enddate error")
            # os.remove(os.path.join(path,files[0]))
            # os.removedirs(path)
            exit()

    return dirdict



print("begin")
time.sleep(2)
dirdict = {}
getfinish(dirdict)
# pyautogui.hotkey('alt','f4')
# exit(0)
try:
    while count!=338:
        count=count+1
        last_file_num = -1
        print("count:",count)
        if str(count) in dirdict.keys():

            files = os.listdir(os.path.join(dstbase , dirdict[str(count)]))
            print("startat:",files[0])
            startdate=files[0]
        else:
            files=[]
            startdate=0
        pyautogui.press(['enter'])
        #get all histroy

        pyautogui.press(['down'],presses=10,interval=0.1)
        time.sleep(0.1)
        #today
        pyautogui.press(['right'])
        # for _ in range(skipday):
        #     pyautogui.press(['left'], interval=interval)
        pyautogui.press(['left'])
        pyautogui.press(['enter'])

        #text = getdate()
        #skip to enddate
        # while text.replace("-","")>enddate:
        #     print("skip", text, " until ", enddate)
        #     pyautogui.press(['pageup'], interval=interval)
        #     text = getdate()
        #     print(text)


        #skip to already download
        print("skip:",len(files)+5)
        pyautogui.press(['esc'])
        time.sleep(0.1)
        pyautogui.press(['left'],presses=len(files)+4,interval=0.05)
        time.sleep(5)
        pyautogui.press(['enter'])


        #begin to download
        current_file_num=len(os.listdir(srcbase))
        while last_file_num != current_file_num:
            #
            last_file_num= current_file_num

            getOne()
            current_file_num = len(os.listdir(srcbase))
            print("get:",current_file_num)
            pyautogui.press(['pageup'])

        print("finish:",count)
        move(count)

        pyautogui.press(['esc'],presses=4,interval=0.01)
        pyautogui.press(['down'])



except Exception as e:
    print(e)
    traceback.print_exc()
    while True:
        winsound.Beep(440, 5000)
        time.sleep(1)

while True:
    winsound.Beep(440,5000)
    time.sleep(1)
# pyautogui.click()
# pyautogui.size()
# pyautogui.press(['alt','f'])
# pyautogui.KEY_NAMES
