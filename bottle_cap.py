# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 15:16:45 2022

@author: User
"""

import cv2 as cv
import numpy as np
import math
from matplotlib import pyplot as plt

def slope(pt1, pt2):
    return (pt2[1]-pt1[1])/(pt2[0]-pt1[0])

def intersect(A, B, C, D):
    # Line AB represented as a1x + b1y = c1
    a1 = B[1] - A[1]
    b1 = A[0] - B[0]
    c1 = a1*(A[0]) + b1*(A[1])
 
    # Line CD represented as a2x + b2y = c2
    a2 = D[1] - C[1]
    b2 = C[0] - D[0]
    c2 = a2*(C[0]) + b2*(C[1])
 
    determinant = a1*b2 - a2*b1
 
    if (determinant == 0):
        # The lines are parallel. This is simplified
        # by returning a pair of FLT_MAX
        return (10**9, 10**9)
    else:
        x = (b2*c1 - b1*c2)/determinant
        y = (a1*c2 - a2*c1)/determinant
        return (x, y)
    
img = cv.imread('images/img01.png')

scale_percent = 2 # percent of original size
width = int(img.shape[1] * scale_percent)
height = int(img.shape[0] * scale_percent)
dim = (width, height)
img = cv.resize(img, dim, interpolation = cv.INTER_AREA)
img2 = img.copy()
img3 = img.copy()

blur = cv.GaussianBlur(img,(3,3),0)

gray = cv.cvtColor(blur, cv.COLOR_RGB2GRAY)

edges = cv.Canny(gray, 50, 200)

center_lines = []
isFault = False

lines = cv.HoughLines(edges, 1, np.pi / 180, 50, None, 0, 0)
if lines is not None:
        for i in range(0, len(lines)):
            rho = lines[i][0][0]
            theta = lines[i][0][1]
            a = math.cos(theta)
            b = math.sin(theta)
            x0 = a * rho
            y0 = b * rho
            pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
            pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))
            if (pt2[0]-pt1[0]) == 0:
                continue
            elif slope(pt1, pt2) >= 0.05 or slope(pt1, pt2) <= -0.05:
                continue
            
            cv.line(img2, pt1, pt2, (0,0,255), 1, cv.LINE_AA)
            (ix, iy) = intersect(pt1, pt2, (width/2, 0), (width/2, height))
            center_lines.append((round(ix), round(iy)))
            cv.circle(img2, (round(ix), round(iy)), radius=5, color=(0, 255, 0), thickness=-1)

center_lines.sort()
tmp = center_lines.copy()
# Upper partition
up_part = []
if center_lines is not None:
    up_part.append(center_lines[0])
    center_lines[0] = 0
    for i in range(1, len(center_lines)-1):
        if(center_lines[i][1] - tmp[i-1][1] < 25):
            up_part.append(center_lines[i])
            center_lines[i] = 0
        else:
            break
        
# Down partition
down_part = []
if center_lines is not None:
    down_part.append(center_lines[len(center_lines)-1])
    center_lines[len(center_lines)-1] = 0
    for i in range(len(center_lines)-2, 0, -1):
        if (center_lines[i-1] == 0):
            down_part.append(center_lines[i])
            center_lines[i] = 0
        elif (tmp[i][1] - center_lines[i-1][1] < 25):
            down_part.append(center_lines[i])
            center_lines[i] = 0
        else:
            break
        
for i in range(0, len(center_lines)):
    if(center_lines[i] != 0):
        isFault = True
        break

if isFault == True :
    print("Bottle is damaged.")
else :
    print("Bottle is okay.")

cv.imshow('original', img)
cv.imshow('edges', edges)
cv.imshow('lines', img2)

cv.waitKey(0)
cv.destroyAllWindows()