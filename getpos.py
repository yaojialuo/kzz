import pyautogui
import time

time.sleep(1)
last_pos=None
while True:
    new_pos=pyautogui.position()
    print(new_pos)
    time.sleep(0.5)