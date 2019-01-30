import IFV101_driver
import time
from PIL import Image


def pErr(errCode, errMess):
    print str(errCode) + " " + errMess

IFV101_driver.regErrCallback(pErr)



# --- process image ----
im = Image.open('test.png') # Can be many different formats.

if im.size[0] != 832:
	scale = float(832)/im.size[0]
	im = im.resize((832,int(im.size[1]*scale)))
	
im = im.convert(mode="1")  # convert to black and white + dither
pix = im.load()

width = im.size[0]
height = im.size[1]
img_enc = bytearray(b'\x00') * (width * height / 8)

x = 0
y = 0

for i in range(len(img_enc)):
	for k in range(8):
		if x == width:
			x = 0
			y += 1
		if pix[width-x-1,height-y-1] < 255:
			img_enc[i] = img_enc[i] | (1<<k)
		x += 1
		
		
# --- print image ---
IFV101_driver.printImg(img_enc)

while True:
   time.sleep(1)
