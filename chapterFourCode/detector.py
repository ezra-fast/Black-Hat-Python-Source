'''
This is a brother program to recapper.py and requires images to process, like those outputted from that script.

This script will take a directory of images, a training directory, and a destination directory, and will find and outline faces in images from the directory of images,
placing them in the destination 'faces' directory.

Line 28 specifies the image format to look for; change accordingly

Change the hardcoded file paths as needed

'''
'''
Dependencies:
    - wget http://eclecti.cc/files/2008/03/haarcascade_frontalface_alt.xml
    - apt install libopencv-dev python3-opencv python3-numpy python3-scipy
'''

from random import triangular
import cv2
import os

ROOT = '/home/ezra/blackHatPython/chapterFourCode/test/pictures'
FACES = '/home/ezra/blackHatPython/chapterFourCode/test/faces'
TRAIN = '/home/ezra/blackHatPython/chapterFourCode/test/training'

def detect(srcdir=ROOT, tgtdir=FACES, train_dir=TRAIN):
    for fname in os.listdir(srcdir):                        # iterate over all images in the source directory
        if not fname.upper().endswith('.JPEG'):             # This line specifies the image file type to search for; change accordingly
            continue
        fullname = os.path.join(srcdir, fname)
        newname = os.path.join(tgtdir, fname)
        img = cv2.imread(fullname)                          # read the image using the opencv2 library
        if img in None:
            continue

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        training = os.path.join(train_dir, 'haarcascade_frontalface_alt.xml')       # this classifier can detect faces in the front facing position
        cascade = cv2.CascadeClassifier(training)               # using the detector XML file, we create the cv2 face detector object
        rects = cascade.detectMultiScale(gray, 1.3, 5)
        try:
            if rects.any():                     # if a face is found --> (rects data are in the form: x, y, width, height) --> x and y denote the lower left hand corner
                print('Got a face')             # print to the console
                rects[:, 2:] += rects[:, :2]    # slicing to get more coordinates from the original left corner, width, and height values (cv2.rectangle() requires these values)
        except AttributeError:
            print(f'No faces found in {fname}.')
            continue

        # highlight the faces in the image
        for x1, y1, x2, y2 in rects:
            cv2.rectangle(img, (x1, y1), (x2, y2), (127, 255, 0), 2)            # draw a green border around the face in the image
        cv2.imwrite(newname, img)                                               # write the image to the output directory

if __name__ == "__main__":
    detect()
