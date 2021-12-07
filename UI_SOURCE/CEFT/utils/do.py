import logging
import shlex
import subprocess
import sys
import platform
import shutil
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from collections import namedtuple
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection

def cropSalienctAspects(image_name, image_path):
  # print("CALLED cropSalienctAspects")
  img_path    = Path(image_path)
  bin_path    = Path("utils/candidate_crops")
  model_path  = Path("utils/fastgaze.vxm")

  # print("\n")
  # print(f"Image is at: {str(img_path.absolute())}")
  # print(f"Model is at: {str(model_path)}")
  # print("\n")



  from .crop_api import ImageSaliencyModel
  model = ImageSaliencyModel(crop_binary_path = bin_path.absolute(), crop_model_path = model_path.absolute())
  saliencyData = model.plot_img_crops(img_path)
  # print(saliencyData)


  from fractions import Fraction
  from .utils import cropImage
  import os 
  nameWithoutExtension = image_name.split('.')[0]
  salienctCutsPath = f"/home/ubuntu/TaskSchedulingAlgorithm/UI_SOURCE/CEFT/static/saliency_outputs/{nameWithoutExtension}"
  os.mkdir(salienctCutsPath)
  absoluteImagePath = str(img_path.absolute())
  aspectRatios = [0.3125, 0.625, 1.0, 1.14, 2]
  salientCoordinates = saliencyData['top10_average_coordinates']
  # print("Aspect Ratios are:")
  for ratio in aspectRatios:
    fraction = Fraction(ratio).limit_denominator(10)
    height = fraction.numerator
    width = fraction.denominator
    # print(f"Aspect Width: {width} Height: {height}")
    cropImage(absoluteImagePath, (width, height), salientCoordinates, f"{salienctCutsPath}/{ratio}")










