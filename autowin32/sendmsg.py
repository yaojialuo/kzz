import win32gui,win32con
astring = b'.504' #必须采用字节串，采用字符串会出现乱码
#先手动打开一个记事本
#获取记事本中编辑控件的句柄
# hWndText = win32gui.FindWindow("Notepad",'新建文本文档.txt - 记事本')
hWndEdit = win32gui.FindWindowEx(1573156,None,"Edit",None)
#发送消息

for x in astring: #依次发送字节串中的每个字节
	win32gui.SendMessage(1573156,win32con.WM_CHAR,x,0)