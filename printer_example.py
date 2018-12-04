import IFV101_driver
import time


def pErr(errCode, errMess):
    print str(errCode) + " " + errMess

IFV101_driver.regErrCallback(pErr)



IFV101_driver.printImg(bytearray(b'\x91') * 104 * 300)
time.sleep(5)
IFV101_driver.printImg(bytearray(b'\x66') * 104 * 500)

while True:
   time.sleep(1)
