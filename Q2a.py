import numpy as np
import cv2
from scipy import signal as sp
import scipy 
import Image
import scipy.ndimage as ndi
import math
from matplotlib import pyplot as plt

class object:
    
    def __init__(self):
        self.l = 0
        self.r = 0
        self.t = 0
        self.b = 0

class minMaxPx:
    
    def __init__(self,val):
        self.min = val
        self.max = val

class regionMerge:
    
    def __init__(self, filename):
        self.filename = filename
        self.preprocess()
        self.defineLabels()
        self.merge()
        self.edge = self.detectEdge()
        self.copyBackEdges()
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.imshow('image',self.img)
        #plt.imshow(self.img)
        #plt.colorbar()
        plt.show()
        
    def preprocess(self):
        self.img = cv2.imread(self.filename,0);
        [self.w,self.h] = self.img.shape
        self.obj = np.array([ object() for x in range(self.h*self.w+1)])
        self.Label = np.array([[ 0 for x in range(self.h)] for y in range(self.w)])
        
    def copyBackEdges(self):
        for i in range(self.w):
            for j in range(self.h):
                if self.edge[i,j] == 255:
                    self.img[i,j] = 255
        
        
    def detectEdge(self):
        self.output = scipy.zeros(self.Label.shape)
        w = self.output.shape[1]
        h = self.output.shape[0]
    
        for y in range(1, h-1 ):
            for x in range(1, w-1 ):
                twoXtwo = self.Label[y-1:y+1, x-1:x+1]
                maxPx = twoXtwo.max()
                minPx = twoXtwo.min()
                Cross = False
                if minPx !=maxPx:
                    Cross = True
                if Cross:
                    self.output[y, x] = 255
        return self.output
                  
    def merge(self):
        change = 1
        iter = 0
        while change == 1:
            iter = iter + 1
            change = 0
            for i in range(self.w):
	        for j in range(self.h):
                    currLabel = self.Label[i,j]
                    for x in range(i,i+2):
                        if x >= self.w:
                            break
                        for y in range(j,j+2):
                            if y >= self.h:
                                break
                            upLevLabel = self.Label[x,y]
                            if upLevLabel == currLabel:
                                continue
                            if (self.obj[upLevLabel].l < self.obj[currLabel].l and self.obj[upLevLabel].r > self.obj[currLabel].r) and \
                                (self.obj[upLevLabel].t < self.obj[currLabel].t and self.obj[upLevLabel].b > self.obj[currLabel].b):
                                self.recurChangeLabel(i,j,upLevLabel,currLabel)
                                change = 1
            plt.imshow(self.Label)
            plt.savefig('recurImage'+str(iter)+'.png')
                    
                    
    def recurChangeLabel(self,i,j,newLabel,oldLabel):
        if i<0 or i>=self.w or j<0 or j>=self.h:
            return
        if self.Label[i,j] != oldLabel:
            return
        self.Label[i,j] = newLabel
        self.recurChangeLabel(i-1,j+1,newLabel,oldLabel)
        self.recurChangeLabel(i,j+1,newLabel,oldLabel)
        self.recurChangeLabel(i+1,j-1,newLabel,oldLabel)
        self.recurChangeLabel(i+1,j,newLabel,oldLabel)
        self.recurChangeLabel(i+1,j+1,newLabel,oldLabel)
                
        
    def defineLabels(self):
        label = 255
        ### visit each pixel and check if the label is not already set . Give the pixel a label and recurse to the neihbours
        for i in range(self.w):
            for j in range(self.h):
                if self.Label[i,j] == 0:
                    label = label - 1
                    currInt = self.img[i,j]
                    self.obj[label].l = i
                    self.obj[label].r = i
                    self.obj[label].t = j
                    self.obj[label].b = j
                    self.recurLabel(i,j,label,currInt);
     
        
    def recurLabel(self,i,j,label,currInt):
        ##return at object boundary conditions
        IntenDiff = 3.8
        if (i < 0 or i >= self.w or j < 0 or j >= self.h) or \
            self.Label[i,j] != 0 or \
            self.img[i,j] < currInt - IntenDiff or self.img[i,j] > currInt + IntenDiff:
            return
        
        currInt = self.img[i,j]
        ## if label already not set and the pixel intensity satisfies homogenity criteria
        ## set Label
        self.Label[i,j] = label
        if self.obj[label].l > i:
            self.obj[label].l = i 
        elif self.obj[label].r < i: 
            self.obj[label].r = i 
        if self.obj[label].t > j:
            self.obj[label].t = j 
        elif self.obj[label].b < j: 
            self.obj[label].b = j
        self.recurLabel(i-1,j+1,label,currInt)
        self.recurLabel(i,j+1,label,currInt)
        self.recurLabel(i+1,j+1,label,currInt)
        self.recurLabel(i+1,j,label,currInt)
        self.recurLabel(i+1,j-1,label,currInt)

if __name__ == "__main__":
    hough = regionMerge('./Peppers.jpg');