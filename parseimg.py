import cv2
import numpy as np
import matplotlib.pyplot as plt

#S:>90w or >3000s ==90 or 91
#S:>30w or >1000s == 150
#B:>90w or >3000s == 76 or 77
#B: >30w or >1000s == 146
pixset=set()
arr1  =cv2.imread(r"1.jpg")
print(arr1.shape)
small=cv2.cvtColor(arr1[:,500:700], cv2.COLOR_BGR2GRAY)
# small[ np.where(small>200)]=255
# small[ np.where(small<200)]=0
plt.figure(figsize=(10, 10))
plt.imshow(small)
plt.show()
exit()
gray=cv2.cvtColor(arr1, cv2.COLOR_BGR2GRAY)
plt.imshow(gray)
plt.show()
exit()

# ret,binsmall=cv2.threshold(small,50,255,cv2.THRESH_BINARY)
# for x in range(small.shape[0]):
#     for y in range(small.shape[1]):
#         pixset.add(tuple(small[x][y]))
#
# print(pixset)
plt.subplot(2,2,1),plt.imshow(arr1[:100,:100])
plt.subplot(2,2,2),plt.imshow(small)
plt.subplot(2,2,3),plt.imshow(arr1[:100,:100],'gray')
# plt.imshow(small)
plt.show()
print(np.min(small))
print(len(pixset))
exit()
# cv2.namedWindow("enhanced",0);
# cv2.resizeWindow("enhanced", 640, 640);
cv2.imshow("enhanced",arr1)
print(arr1[:100,:100].shape)
cv2.waitKey()