#!/usr/bin/env python

import time
import serial
from gpiozero import Button
import math
import thread

ser = serial.Serial('/dev/ttyS0', 115200)
sBusy = Button(4,False)
pErr = Button(17,False)
st0 = Button(22,False)
st1 = Button(27,False)
st2 = Button(18,False)

imgBuffer = []
errFunc = None

def regErrCallback(_errFunc):
    global errFunc
    errFunc = _errFunc
    errFunc(0,"function registered")



def checkErr():
    global errFunc
    errCode = 0
    errMess = "Undefined Error"
    #print [pErr.value, st0.value, st1.value, st2.value]

    if pErr.value:
        if(st0.value and not st1.value and st2.value):
            errMess =  "Return-waiting status"
            errCode = 7
        elif(not st0.value and not st1.value and st2.value):
            errMess =  "Print-ready status"
            errCode = 8
    else:
        if(not st0.value and not st1.value and not st2.value):
            errMess =  "Initialize"
            errCode = 1
        elif(st0.value and not st1.value and not st2.value):
            errMess =  "Hardware error"
            errCode = 2
        elif(st0.value and st1.value and st2.value):
            errMess =  "Out-of-paper error"
            errCode = 3
        elif(not st0.value and st1.value and st2.value):
            errMess =  "Platen position error"
            errCode = 4
        elif(st0.value and not st1.value and st2.value):
            errMess =  "Vp voltage error"
            errCode = 5
        elif(not st0.value and not st1.value and st2.value):
            errMess =  "Head temperature error"
            errCode = 6

    if(errFunc != None):
         errFunc(errCode, errMess)


pErr.when_pressed = checkErr
pErr.when_released = checkErr

st0.when_pressed = checkErr
st0.when_released = checkErr

st1.when_pressed = checkErr
st1.when_released = checkErr

st2.when_pressed = checkErr
st2.when_released = checkErr


def sendThread():
   while True:
      #print "waiting"
      #print [pErr.value, st0.value, st1.value, st2.value]
      if(len(imgBuffer) > 0):
         sendImg(imgBuffer[0])
         imgBuffer.pop(0)
         print "sent img"
      time.sleep(0.2)

thread.start_new_thread(sendThread, ())


def sendImg(imgData):
   height = len(imgData) / 104     #  img width = 832, 832/8 = 104

   sBusy.wait_for_release()
   ser.write(bytearray([27,86]))
   ser.write(bytearray([height % 256,height // 256]))

   blockSize = 32
   dataBlockAm = int(math.ceil(len(imgData) / float(blockSize)))    # Up to 32 bytes of input data are guaranteed after the SBUSY signal has
                                                                    # become "High".
   print dataBlockAm

   for x in range(dataBlockAm):
      startPos = x * blockSize
      endPos = min((x + 1) * blockSize, len(imgData))

      sBusy.wait_for_release()
      ser.write(imgData[startPos:endPos])


def printImg(imgData):
   imgBuffer.append(imgData)
   



   


      
      