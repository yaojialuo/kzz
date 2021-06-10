import uiautomation as auto
import time
import os

tdx=auto.WindowControl(searchDepth=1, ClassName='TdxW_MainFrame_Class')
def getKzzList(path=r"Z:\trade\screen_shot\kzzprecision.txt"):
    tdx.SendKeys("kzz{enter}34{enter}", 0.2, 0)
    time.sleep(0.1)
    export=tdx.PaneControl(searchDepth=1,Name="数据导出")
    export.RadioButtonControl(searchDepth=1, Name="报表中所有数据(显示的栏目)").SetFocus()
    export.RadioButtonControl(searchDepth=1, Name="报表中所有数据(显示的栏目)").Click(simulateMove=False)
    export.EditControl().GetValuePattern().SetValue(path)
    export.ButtonControl(searchDepth=1, Name="导出").Click(simulateMove=False)
    while True:
        if tdx.GetChildren()[0].Name == "TdxW":
            tdx.GetChildren()[0].ButtonControl(Name="取消").Click(simulateMove=False)
            break
    time.sleep(0.5)
