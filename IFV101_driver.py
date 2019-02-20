#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import serial
import RPi.GPIO as GPIO
import math
import thread

ser = serial.Serial('/dev/ttyS0', 115200)

GPIO.setmode(GPIO.BOARD)

sBusy_pin = 18
pErr_pin = 16
st0_pin = 11
st1_pin = 13
st2_pin = 15

GPIO.setup(sBusy_pin, GPIO.IN)
GPIO.setup(pErr_pin, GPIO.IN)
GPIO.setup(st0_pin, GPIO.IN)
GPIO.setup(st1_pin, GPIO.IN)
GPIO.setup(st2_pin, GPIO.IN)

imgBuffer = []
errFunc = None


def regErrCallback(_errFunc):
    global errFunc
    errFunc = _errFunc
    errFunc(0, 'function registered')
	checkErr(0)


def checkErr(channel):
    global errFunc
    errCode = 0
    errMess = 'Undefined Error'

    # print [GPIO.input(pErr_pin), GPIO.input(st0_pin), GPIO.input(st1_pin), GPIO.input(st2_pin)]

    if GPIO.input(pErr_pin):
        if GPIO.input(st0_pin) and not GPIO.input(st1_pin) \
            and GPIO.input(st2_pin):
            errMess = 'Return-waiting status'
            errCode = 7
        elif not GPIO.input(st0_pin) and not GPIO.input(st1_pin) \
            and GPIO.input(st2_pin):
            errMess = 'Print-ready status'
            errCode = 8
    else:
        if not GPIO.input(st0_pin) and not GPIO.input(st1_pin) \
            and not GPIO.input(st2_pin):
            errMess = 'Initialize'
            errCode = 1
        elif GPIO.input(st0_pin) and not GPIO.input(st1_pin) \
            and not GPIO.input(st2_pin):
            errMess = 'Hardware error'
            errCode = 2
        elif GPIO.input(st0_pin) and GPIO.input(st1_pin) \
            and GPIO.input(st2_pin):
            errMess = 'Out-of-paper error'
            errCode = 3
        elif not GPIO.input(st0_pin) and GPIO.input(st1_pin) \
            and GPIO.input(st2_pin):
            errMess = 'Platen position error'
            errCode = 4
        elif GPIO.input(st0_pin) and not GPIO.input(st1_pin) \
            and GPIO.input(st2_pin):
            errMess = 'Vp voltage error'
            errCode = 5
        elif not GPIO.input(st0_pin) and not GPIO.input(st1_pin) \
            and GPIO.input(st2_pin):
            errMess = 'Head temperature error'
            errCode = 6

    if errFunc != None:
        errFunc(errCode, errMess)


GPIO.add_event_detect(pErr_pin, GPIO.BOTH, callback=checkErr)
GPIO.add_event_detect(st0_pin, GPIO.BOTH, callback=checkErr)
GPIO.add_event_detect(st1_pin, GPIO.BOTH, callback=checkErr)
GPIO.add_event_detect(st2_pin, GPIO.BOTH, callback=checkErr)


def wait_for_release(channel):
    if GPIO.input(channel):
        GPIO.wait_for_edge(channel, GPIO.FALLING)


def sendThread():
    while True:

      # print "waiting"
      # print [pErr.value, GPIO.input(st0_pin), GPIO.input(st1_pin), GPIO.input(st2_pin)]

        if len(imgBuffer) > 0:
            sendImg(imgBuffer[0])
            imgBuffer.pop(0)
            print 'sent img'
        time.sleep(0.2)


thread.start_new_thread(sendThread, ())


def sendImg(imgData):
    height = len(imgData) / 104  #  img width = 832, 832/8 = 104

    wait_for_release(sBusy_pin)
    ser.write(bytearray([27, 86]))
    ser.write(bytearray([height % 256, height // 256]))

    blockSize = 32
    dataBlockAm = int(math.ceil(len(imgData) / float(blockSize)))  # Up to 32 bytes of input data are guaranteed after the SBUSY signal has

                                                                    # become "High".

    print dataBlockAm

    for x in range(dataBlockAm):
        startPos = x * blockSize
        endPos = min((x + 1) * blockSize, len(imgData))

        time.sleep(0.003)  # wait a moment for the sBusy signal to arrive
        wait_for_release(sBusy_pin)

        ser.write(imgData[startPos:endPos])


def printImg(imgData):
    imgBuffer.append(imgData)
