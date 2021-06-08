import time

import cv2
import mss
import numpy
import pytesseract
import os
#Point(x=1366, y=-54)
#Point(x=3266, y=995)
print("begin")
# time.sleep(2)
mon = {'top': 11, 'left': 1366, 'width': 1900, 'height': 982}
sct = mss.mss()
import matplotlib.pyplot as plt
start = time.perf_counter()
im = numpy.asarray(sct.grab(mon))
path=r"E:\pycharm\kzz\screen_shot\000002"
os.path.join(path,"1.jpg")
cv2.imwrite(os.path.join(path,"1.jpg"), im)
cv2.imshow("image",im)
# im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

cv2.waitKey(0)
exit()
plt.imshow(im)
plt.show()
# if cv2.waitKey(25) & 0xFF == ord('q'):
#     cv2.destroyAllWindows()

text = pytesseract.image_to_string(im,config='--psm 7 digits')
print("text",text)
print(len(text))
elapsed = (time.perf_counter() - start)
print("Time used:", elapsed)
# Press "q" to quit


# One screenshot per second
time.sleep(1)