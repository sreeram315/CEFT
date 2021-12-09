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

from .back_projection import saveBackProjectionData

def topFeatureMark(image_path, download_path, saliencyData):
  import matplotlib.pyplot as plt
  import matplotlib.image as mpimg
  import numpy as np
  image = mpimg.imread(image_path)
  plt.imshow(image)
  mostSalientPoint  = saliencyData['salient_coordinates']
  top10Average    = saliencyData['top10_average_coordinates']
  plt.plot(mostSalientPoint[0], mostSalientPoint[1], "xr", markersize=10)
  plt.plot(top10Average[0], top10Average[1], "xg", markersize=10)
  plt.savefig(download_path, bbox_inches='tight', pad_inches=0)
  plt.close()

def cropSalienctAspects(image_name, image_path):
  # print("CALLED cropSalienctAspects")
  img_path    = Path(image_path)
  bin_path    = Path("utils/candidate_crops")
  model_path  = Path("utils/fastgaze.vxm")

  nameWithoutExtension = image_name
  imageDataPath = f"/home/ubuntu/TaskSchedulingAlgorithm/UI_SOURCE/CEFT/static/saliency_outputs/{nameWithoutExtension}"
  import os 
  os.mkdir(imageDataPath)
  os.mkdir(f"{imageDataPath}/my_crops")
  os.mkdir(f"{imageDataPath}/twitter")

  from .crop_api import ImageSaliencyModel
  model = ImageSaliencyModel(crop_binary_path = bin_path.absolute(), crop_model_path = model_path.absolute())
  saliencyData = model.plot_img_crops(img_path, f"{imageDataPath}/twitter/heat_map.jpeg")
  # print(saliencyData)
  plt.close()
  topFeatureMark(image_path, f"{imageDataPath}/twitter/top_feature.jpeg", saliencyData)


  from fractions import Fraction
  from .utils import cropImage
  absoluteImagePath = str(img_path.absolute())
  aspectRatios = [0.3125, 0.625, 1.0, 1.14, 2]
  salientCoordinates = saliencyData['top10_average_coordinates']
  top_feature = saliencyData['salient_coordinates']
  # print("Aspect Ratios are:")
  for ratio in aspectRatios:
    fraction = Fraction(ratio).limit_denominator(10)
    height = fraction.numerator
    width = fraction.denominator
    # print(f"Aspect Width: {width} Height: {height}")
    cropImage(absoluteImagePath, (width, height), salientCoordinates, top_feature,, f"{imageDataPath}/my_crops/{ratio}")

def generateBackProjectionData(image_name, image_path):
  nameWithoutExtension = image_name
  download_path = f"/home/ubuntu/TaskSchedulingAlgorithm/UI_SOURCE/CEFT/static/saliency_outputs/{nameWithoutExtension}/back_projection"
  import os 
  os.mkdir(f"{download_path}")
  saveBackProjectionData(image_path, download_path)








