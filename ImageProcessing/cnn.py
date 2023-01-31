import sys

sys.path.append('../')

from plugins.mdc_self.ImageProcessing.hog import face_center as hog_face_center


def face_center(filename, model):
    return hog_face_center(filename, model)
