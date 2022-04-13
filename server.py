import sys
from multiprocessing import Queue
import threading
import numpy as np
import os
from os import path
import socket
import json
import time, cv2
from processor import Processor
from logger import Logger
import configparser
from distutils.util import strtobool
from ahtInterface import AhtInterface, AhtApp


#imgSize = 79056
sizes=[(320,244),(320,256), (320,240)]
imgSizes= [ el[0]*el[1] for el in sizes ]
minsize=min(imgSizes)
buflens=[78500,82000,77000]


#CONFIG

# init queue between tasks and interface



class UDP_Server(threading.Thread):

    def __init__(self, UDP_PORT, PACKETSIZE, queue, logger):
        # Call the Thread class's init function
        threading.Thread.__init__(self)
        self.logger = logger

        print("Server target port:", UDP_PORT, flush=True)
        self.logger.Log("UDP Server listening on target port:" + str(UDP_PORT))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", UDP_PORT))

        # init queue between tasks
        self.q = queue

        self.folder = str(UDP_PORT)
        self.PACKET_LEN = PACKETSIZE
        print("UDP" + self.folder + ": " + "Server ready", flush=True)
        self.stopped = False

        self.chrid = 0

    def Stop(self):
        self.stopped = True

    # Override the run() function of Thread class
    def run(self):
        self.get_from_wifi()



    def print_packets_index(self, buffer):
        strppp = ''
        for i in range(len(buffer)):
            index = self.get_packet_index(buffer[i])
            strppp += str(index) + ', '
        print("UDP" + self.folder + ": " + 'Packets into the buffer: ', strppp, flush=True)

    def find_index_seq(self, a, b):
        # a is the data, b is the sequence
        return [(i, i + len(b)) for i in range(len(a)) if a[i:i + len(b)] == b]

    def resise_jpg_pkt(self, data):
        # check init and end of file
        # init seq
        s = self.find_index_seq(data, [255, 216])
        # end seq
        f = self.find_index_seq(data, [0xff, 0xd9])
        if len(s) == 0:
            data = []
            return data
        if len(f) == 0:
            data = []
            return data
        if s[0][0] != 0:
            data = []
            print()
            return data
        data = data[0:(f[0][1])]
        return data


    def get_from_wifi(self):
        self.sock.settimeout(3)
        data_buffer = []
        next_id = 0

        while not self.stopped:
            try:
                data, addr = self.sock.recvfrom(1024)  # buffer size is 1024 bytes
            except:
                print(".",end='')
                continue

            #print("UDP" + self.folder + ": " + 'Data Packet len: ', len(data), flush=True)
            # print ("UDP" + self.folder + ": " + 'Data Packet: ', str(data), flush=True)

            if len(data) != self.PACKET_LEN:
               print ("UDP" + self.folder + ": " + '[ERROR] Data Packet len: ', len(data), ' instead of max ',
                          self.PACKET_LEN, flush=True)

            index = data[0] + (data[1]) * 256
            packettype = data[2]
            #print('Sync Buffering: {} of type {}'.format(index,packettype))

            if index == 0:
                data_buffer = []
                next_id = 0
                print("New index of data received via UDP...")
            # add current data to buffer
            data_buffer.extend(data[3:])

            try:

                if (index not in [0, 65535, next_id+1]):
                    self.logger.Log("packet out of sequence")

                if index == 65535:
                    # in base al tipo di dato
                    if packettype==1:
                        self.logger.Log("data received via UDP of type {}".format(packettype))
                        mystr=""
                        for car in data_buffer[0:data_buffer.index(0)]:
                            mystr += chr(car)

                        self.logger.Log(str(mystr))
                        continue
                    if packettype==2:
                        self.logger.Log("data received via UDP of type {}".format(packettype))
                        sizewhm = 80
                        sizehhm = 64
                        sizehm = sizewhm * sizehhm

                        imgHM1 = np.array(data_buffer[0:sizehm]).reshape(sizehhm, sizewhm).copy().astype(np.uint8)
                        imgHM2 = np.array(data_buffer[sizehm :2* sizehm]).reshape(sizehhm, sizewhm).copy().astype(np.uint8)
                        imgSZ = np.array(data_buffer[2*sizehm :3*sizehm ]).reshape(sizehhm, sizewhm).copy().astype(np.uint8)

                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
                        result, encimg1 = cv2.imencode('.jpg', imgHM1, encode_param)
                        result, encimg2 = cv2.imencode('.jpg', imgHM2, encode_param)
                        result, encimg3 = cv2.imencode('.jpg', imgSZ, encode_param)

                        # send raw img to JPEG task
                        imgs = []
                        imgs.append(self.folder)
                        imgs.append(encimg1)
                        self.q.put(imgs)
                        imgs = []
                        imgs.append(self.folder)
                        imgs.append(encimg2)
                        self.q.put(imgs)
                        imgs = []
                        imgs.append(self.folder)
                        imgs.append(encimg3)
                        self.q.put(imgs)

                        continue
                    if packettype == 3:
                        self.logger.Log("data received via UDP of type {}".format(packettype))

                        wimg = 320
                        himg = 256

                        imgch1 = np.array(data_buffer[0:wimg * himg]).reshape(himg, wimg).copy().astype(np.uint8)
                        imgch2 = np.array(data_buffer[wimg * himg:wimg * himg*2]).reshape(himg, wimg).copy().astype(np.uint8)
                        imgch3 = np.array(data_buffer[wimg * himg*2:wimg * himg*3]).reshape(himg, wimg).copy().astype(np.uint8)

                        imgRGB = cv2.merge((imgch1,imgch2,imgch3))

                        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]

                        result2, encimg2 = cv2.imencode('.jpg', imgRGB, encode_param)

                        # send raw img to JPEG task
                        imgs = []
                        imgs.append(self.folder)
                        imgs.append(encimg2)
                        self.q.put(imgs)

                        continue

                    # I suppose a new IMG!
                    print ('New Img len: ', len(data_buffer))
                    if len(data_buffer) > 3:
                        # check header type
                        if data_buffer[0:2]==[0xFF,0xD8]:
                            # jpeg received
                            data_buffer = self.resise_jpg_pkt(data_buffer)
                            print("UDP" + self.folder + ": " + 'Img len: ', len(data_buffer), flush=True)
                            imgs = []
                            self.logger.Log("Jpeg Image received via UDP")
                            # send raw img to JPEG task
                            imgs.append(self.folder)
                            imgs.append(data_buffer)
                            self.q.put(imgs)
                        elif len(data_buffer)>=minsize and len(data_buffer) in buflens:
                            # raw image received
                            (imgW,imgH) = sizes[buflens.index(len(data_buffer))]

                            grayImage = np.array(data_buffer[0:imgW*imgH]).reshape(imgH, imgW).copy().astype(np.uint8)

                            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
                            result, encimg = cv2.imencode('.jpg', grayImage, encode_param)
                            print("UDP" + self.folder + ": " + 'Img len: ', len(encimg), flush=True)
                            imgs = []
                            self.logger.Log("Raw image received via UDP of size {}x{}".format(imgW,imgH))
                            # send raw img to JPEG task
                            imgs.append(self.folder)
                            imgs.append(encimg)
                            self.q.put(imgs)
                        else:
                                print("UDP" + self.folder + ": " + 'Error Img corrupted', flush=True)
                    data_buffer = [] # buffer cleaning after end packet

    
                next_id = index
            except:
                #  in caso di eccezione, vuoto tutto il buffer e riparto
                print("ERRORE - ECCEZIONE")
                data_buffer = []  # buffer cleaning after end packet
                next_id = 0





class JPEG_Server(threading.Thread):

    def __init__(self, queue, logger):
        # Call the Thread class's init function
        threading.Thread.__init__(self)
        # init queue between tasks
        self.q = queue
        self.logger = logger
        print("JPEG: Server ready", flush=True)
        self.logger.Log("JPEG: Server ready")

        self.processor = Processor(logger)

        self.stopped = False
    def Stop(self):
        self.stopped = True

    # Override the run() function of Thread class
    def run(self):
        self.WriteJPG()

    def ManageDir(self, dir):
        if path.exists(dir):
            return
        else:
            os.makedirs(dir)
            nfile = {}
            nfile['nfile'] = []
            nfile['nfile'].append({'val': '0'})
            with open(path.join(dir, 'data.txt'), 'w') as outfile:
                json.dump(nfile, outfile)

    def GetFile(self, dir):
        if not os.path.exists(path.join(dir, 'data.txt')):
            nfile = {}
            nfile['nfile'] = []
            nfile['nfile'].append({'val': '0'})
            with open(path.join(dir, 'data.txt'), 'w') as outfile:
                json.dump(nfile, outfile)

        with open(path.join(dir, 'data.txt')) as json_file:
            nfile = json.load(json_file)
            for p in nfile['nfile']:
                return int(p['val'])

    def StoreFile(self, dir, n):
        nfile = {}
        nfile['nfile'] = []
        nfile['nfile'].append({'val': str(n)})
        with open(path.join(dir, 'data.txt'), 'w') as outfile:
            json.dump(nfile, outfile)

    def WriteJPG(self):

        while not self.stopped:
            # Get some data
            try:
                imgs = self.q.get(False, 4)
            except:
                continue
            folder = imgs.pop(0)
            data = imgs.pop(0)

            s_folder = "img_port" + folder
            self.ManageDir(s_folder)
            num_files = self.GetFile(s_folder)

            s = "Img" + str(num_files) + ".jpg"
            filename = path.join(s_folder, s)

            f = open(filename, 'wb')
            f.write(bytes(data))
            num_files = num_files + 1
            f.close()

            self.StoreFile(s_folder, num_files)
            self.logger.Log(filename, type='image')
            self.processor.process(filename)


if __name__ == "__main__":

    Config = configparser.ConfigParser()
    Config.read("gateway.ini")
    USEINTERFACE = bool(strtobool(Config.get('General', 'USEINTERFACE')))
    lg = Logger(USEINTERFACE)

    # Create the shared queue and launch both threads
    q = Queue()
    # start Jpeg thread
    j = JPEG_Server(q, lg)

    print("Starting... JPEG")
    j.start()
    # execute for each device

    UDP_PORT = int(Config.get('UDP', 'UDP_PORT'))
    PACKETSIZE = int(Config.get('UDP', 'PACKETSIZE'))
    HEADERSIZE = int(Config.get('UDP', 'HEADER_BYTES'))

    print("Starting..." + str(UDP_PORT))
    web = UDP_Server(UDP_PORT, PACKETSIZE+HEADERSIZE, q, lg)
    web.start()



    if USEINTERFACE:
        app = AhtApp()
        widget = AhtInterface(lg)
        widget.show()
        app.exec_()

        web.Stop()
        j.Stop()


# wait forever
web.join()
j.join()
