import cv2
import requests
import configparser
import time
from utils_AHT import AHT,geturlFromSrcdef

 # from detectors import TinyFace


class FaceDetector():
    def __init__(self):
        # DET2 = FaceBoxes(device='cuda')
        # self.det = TinyFace(device='cuda')
        pass

    def __containFace(self, image):
        print("check face")
        #cv2.imshow('input',image)
        #cv2.waitKey(1)
        return False

        bboxes = self.det.detect_faces(image, conf_th=0.7, scales=[1])
        for box in bboxes:
            x1, y1, x2, y2, conf = box
            print(" face with conf "+str(conf))
            if conf > 0.9:
                try:
                    #cv2.imshow('face', image[int(y1):int(y2), int(x1):int(x2)])
                    #cv2.waitKey(1)
                    pass
                except:
                    pass

                return True
        return False

    def process(self, filename):

        # convert image to cv2
        image = cv2.imread(filename)

        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # check face
        return self.__containFace(image)


class Processor():

    def __init__(self, logger):
        self.Config = configparser.ConfigParser()
        self.Config.read("gateway.ini")
        self.lastTime = None
        self.interval = float(self.Config.get('General', 'INTERVAL'))

        self.logger=logger
        self.logger.Log("AHT init...")


        self.aht = AHT(self.Config.get('General', 'BASEURL'))
        # print (aht.getListOfServices())
        self.srvdef = self.aht.findService('addfacetofacemaskdb')
        self.urlWebPage = geturlFromSrcdef(self.srvdef)
        print(self.urlWebPage)
        self.logger.Log("AHT service found at " + self.urlWebPage)

        print("Face detector init...")

        self.fd = FaceDetector()


    def process(self, filename):

        # controllo comunque presenza volto
        hasface = self.fd.process(filename)
        if hasface:
            print("Face detected in the image")
        # check time interval
        if self.lastTime is not None:
            ts = time.time()

            if ts - self.lastTime < self.interval:
                # immagine processata da troppo poco tempo
                print("interval not elapsed: face not sent")
                return

        if hasface:
            self.__sendToFaceMask(filename)
            self.lastTime = time.time()

    def __sendToFaceMask(self, filename):

        values = {'Authorization': 'bearer ' + self.Config.get('Authentication', 'BEARERTOKEN')}
        files = {'imgfile': open(filename, 'rb')}

        try:
            test_response = requests.post(self.urlWebPage, files=files, data=values)

            if test_response.ok:
                print("Upload completed successfully!")
                self.logger.Log("Image Upload on the annotation framework completed successfully!")
                print(test_response.text)
            else:
                print("Something went wrong uploading the image!")
                self.logger.Log("Something went wrong uploading the image!")

        except:
            print("Something went wrong uploading the image!")
            self.logger.Log("Something went wrong uploading the image!")




