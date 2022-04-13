

from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QImage, QPixmap
from PySide2.QtCore import QFile, Qt
from PySide2.QtUiTools import QUiLoader

import numpy as np
import cv2
import time
import os
from glob import glob

def show_image_from_file(filename, lbl):
    imgInput = cv2.imread(filename)
    show_image(imgInput,lbl)


def show_image(imgInput, lbl):
    img = np.copy(imgInput)

    axis = len(img.shape)
    if axis == 2:
        height, width = img.shape
        channel = 1
        bytesPerLine = channel * width
        dati = np.ascontiguousarray(img.data)
        qImg = QImage(dati, width, height, bytesPerLine, QImage.Format_Grayscale8)
        pixmap01 = QPixmap.fromImage(qImg)
        # pixmap01 = pixmap01.scaled(lbl.width(), lbl.height(), Qt.KeepAspectRatio)
        pixmap01 = pixmap01.scaled(lbl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        lbl.setPixmap(pixmap01)
    if axis == 3:
        height, width, channel = img.shape
        if channel == 3:
            bytesPerLine = channel * width
            dati = np.ascontiguousarray(img.data)
            qImg = QImage(dati, width, height, bytesPerLine, QImage.Format_RGB888)
            qImg = qImg.rgbSwapped()
            pixmap01 = QPixmap.fromImage(qImg)
            pixmap01 = pixmap01.scaled(lbl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl.setPixmap(pixmap01)

        elif channel == 1:
            if img.dtype == np.dtype('uint16'):
                maxval = np.amax(img)
                img = img.astype(np.float32) * (255.0 / maxval)
                img = img.astype('uint8')

            bytesPerLine = channel * width
            dati = np.ascontiguousarray(img.data)
            qImg = QImage(dati, width, height, bytesPerLine, QImage.Format_Grayscale8)

            pixmap01 = QPixmap.fromImage(qImg)
            pixmap01 = pixmap01.scaled(lbl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl.setPixmap(pixmap01)


def conv2rgb(img):
    rgb = img
    axis = len(img.shape)
    if axis == 2:
        if img.dtype == np.dtype('uint16'):
            maxval = np.amax(img)
            img = img * (255.0 / maxval)
            img = img.astype('uint8')
        rgb = cv2.merge((img,img,img))

    if axis == 3:
        height, width, channel = img.shape
        if channel == 3:
            rgb = img

        if channel == 1 and img.dtype == np.dtype('uint16'):
            maxval = np.amax(img)
            img = img * (255.0 / maxval)
            img = img.astype('uint8')
            rgb = np.zeros((height, width, 3), 'uint8')
            rgb[..., 0] = img[..., 0]
            rgb[..., 1] = img[..., 0]
            rgb[..., 2] = img[..., 0]
            # rgb =cv2.cvtColor(img[:,:,0], cv2.CV_GRAY2RGB)

    return rgb

