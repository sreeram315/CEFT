import cv2, sys
import numpy as np

def convert(coordinates, newSize, originalSize):
	width, newWidth, oldWidth = coordinates[0], newSize[0], originalSize[0]
	newWidth = (oldWidth*width)/newWidth
	height, newHeight, oldHeight = coordinates[1], newSize[1], originalSize[1]
	newHeight = (oldHeight*height)/newHeight
	return (newWidth, newHeight)

def backproject(source, target, levels = 2, scale = 1):
	hsv = cv2.cvtColor(source,	cv2.COLOR_BGR2HSV)
	hsvt = cv2.cvtColor(target,	cv2.COLOR_BGR2HSV)
	# calculating object histogram
	roihist = cv2.calcHist([hsv],[0, 1], None, [levels, levels], [0, 180, 0, 256] )

	# normalize histogram and apply backprojection
	cv2.normalize(roihist,roihist,0,255,cv2.NORM_MINMAX)
	dst = cv2.calcBackProject([hsvt],[0,1],roihist,[0,180,0,256], scale)
	return dst

def saliency_by_backprojection(img):
	cv2.pyrMeanShiftFiltering(img, 2, 10, img, 4)

	backproj = np.uint8(backproject(img, img, levels = 2))
	cv2.normalize(backproj,backproj,0,255,cv2.NORM_MINMAX)
	saliencies = [backproj, backproj, backproj]
	saliency = cv2.merge(saliencies)

	cv2.pyrMeanShiftFiltering(saliency, 20, 200, saliency, 2)
	saliency = cv2.cvtColor(saliency, cv2.COLOR_BGR2GRAY)
	cv2.equalizeHist(saliency, saliency)
	return 255-saliency

def saliency_map(img):
	saliency_hsv = saliency_by_backprojection(img * 1)
	saliency = saliency_hsv
	(T, saliency) = cv2.threshold(saliency, 200, 255, cv2.THRESH_BINARY)
	return saliency

def largest_contours_rect(saliency):
	contours, hierarchy = cv2.findContours(saliency * 1,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
	contours = sorted(contours, key = cv2.contourArea)
	return cv2.boundingRect(contours[-1]), contours

def refine_saliency_with_grabcut(img, saliency):
	rect, contours = largest_contours_rect(saliency)
	bgdmodel = np.zeros((1, 65),np.float64)
	fgdmodel = np.zeros((1, 65),np.float64)
	saliency[np.where(saliency > 0)] = cv2.GC_FGD
	mask = saliency
	cv2.grabCut(img, mask, rect, bgdmodel, fgdmodel, 1, cv2.GC_INIT_WITH_RECT)
	mask = np.where((mask==2)|(mask==0),0,1).astype('uint8')
	return mask, contours

def backprojection_saliency(img):
	saliency = saliency_map(img)
	cv2.imwrite("results/contours.jpg", saliency)
	mask, contours = refine_saliency_with_grabcut(img, saliency)
	# cv2.imwrite("refine_saliency_with_grabcut.jpg", mask)
	return mask, contours

def saveBackProjectionData(image_path, download_path):
	import matplotlib.pyplot as plt
	import matplotlib.image as mpimg
	import numpy as np
	img = cv2.imread(image_path, 1)
	# img = cv2.resize(img, (int(640/2), int(480/2)))
	height, width, channels = img.shape
	newSize = (width, height)
	# print (height, width, channels)
	mask, contours = backprojection_saliency(img)
	segmentation = img*mask[:,:,np.newaxis]
	cv2.imwrite(f"{download_path}/contours_result.jpg", segmentation)

	# print(len(contours))
	# contours.sort()
	# print(contours)
	count = 0
	points = []
	# print(contours)
	for contour in contours:
		count += 1
		# print(f"Count: {count} | Size: {len(contour)}")
		x, y, total = 0, 0, len(contour)
		for el in contour:
			x += el[0][0]
			y += el[0][1]
		points.append((x/total, y/total, total))

	points.sort(key = lambda x: x[2], reverse = True)
	# print(points)
	points = points[:4]
	# print(points)

	image = mpimg.imread(image_path)
	height, width, _ = image.shape
	originalSize = (width, height)
	# print(f"Width: {width} Height: {height}")
	pts = np.array([(el[0], el[1]) for el in points])
	plt.imshow(image)

	for p in pts:
		x, y = convert((p[0], p[1]), newSize, originalSize)
		# print("->>", (p[0], p[1]), (x, y))
		plt.plot(x, y, "or", markersize=10)

	# plt.show()
	plt.savefig(f"{download_path}/contours_hotspots.jpeg", bbox_inches='tight', pad_inches=0)
	plt.close()
