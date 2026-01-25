import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt

FILE_PATH = "./   E"
# image (an resolution is fine)
# for tuning using a lower resolution may help
img = cv.imread(FILE_PATH, cv.IMREAD_GRAYSCALE)
assert img is not None, "file could not be read, check with os.path.exists()"
''' First number is the minimum delta for an edge (smaller the more sensitive), second number defines max value.
The gradient output function [the lines] tries to detect the average of these numbers, but will pick up on everything in this range. 
The function will try to minimize noise, so have a range too large will also not work'''
edges = cv.Canny(img,80,150)
plt.subplot(121),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
plt.show()