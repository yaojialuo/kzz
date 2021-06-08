import win32gui

#windows下用python3.0操作windows api向记事本里面写入字符--发送ASCII码
import time


hwnd_title = dict()
#clsname = win32gui.GetClassName(hWnd)
# win32gui.GetWindowText(hwnd)
def get_all_hwnd(hwnd, mouse):
    # if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
    hwnd_title.update({hwnd:[win32gui.GetWindowText(hwnd),win32gui.GetClassName(hwnd)] })

# ([1573156], [['通达信金融终端(开心果整合版)V1314.520 - [行情报价-自选股]', 'TdxW_MainFrame_Class']])
#win32gui.EnumChildWindows(1573156,get_all_hwnd,0)
win32gui.EnumWindows(get_all_hwnd, 0)
import win32gui,win32con
astring = b'.504' #必须采用字节串，采用字符串会出现乱码
#先手动打开一个记事本
#获取记事本中编辑控件的句柄
# hWndText = win32gui.FindWindow("Notepad",'新建文本文档.txt - 记事本')
hWndEdit = win32gui.FindWindowEx(1573156,None,"Edit",None)
#发送消息


for h, t in hwnd_title.items():
    if t is not "":
        print(([h], [t]))
        # time.sleep(0.5)
        # for x in astring:  # 依次发送字节串中的每个字节
        #     win32gui.SendMessage(h, win32con.WM_CHAR, x, 0)

