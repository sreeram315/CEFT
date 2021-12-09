def isInsideCrop(x, y, crop):
	left, right, top, bottom = crop[0], crop[1], crop[2], crop[3]
	return (x >= left and x <= right and y>=top and y<=bottom)

def cropImage(imagePath, aspectRatio, salientCoordinates, top_feature, outputFileName = "output"):
	from PIL import Image
	originalImage = Image.open(imagePath)
	width, height = originalImage.size
	# print(width, height)

	aspectWidth, aspectHeight = aspectRatio[0], aspectRatio[1]

	if(aspectWidth > aspectHeight):
		finalWidth 	= (0.75 * width)
		left 		= max(0, salientCoordinates[0] - (finalWidth/2))
		right 		= left + finalWidth

		finalHeight = (aspectHeight*finalWidth)/aspectWidth
		top 		= max(0, salientCoordinates[1] - (finalHeight/2))
		bottom 		= min(top + finalHeight, height)
	else:
		finalHeight = (0.75 * width)
		top 		= max(0, salientCoordinates[1] - (finalHeight/2))
		bottom 		= min(top + finalHeight, height)

		finalWidth 	= (aspectWidth*finalHeight)/aspectHeight
		left 		= max(0, salientCoordinates[0] - (finalWidth/2))
		right 		= left + finalWidth

	m1_x, m1_y = top_feature[0], max(0, top_feature[1]-(0.05 * height))
	m2_x, m2_y = top_feature[0], min(top_feature[1]+(0.05 * height), height)
	m3_x, m3_y = max(0, top_feature[0]-(0.05 * width)), top_feature[1]
	m4_x, m4_y = min(top_feature[0]+(0.05 * width), width), top_feature[1]

	# print("-> ", left, right, top, bottom)
	crop = (left, right, top, bottom)
	if not all([isInsideCrop(m1_x, m1_y, crop), isInsideCrop(m2_x, m2_y, crop), isInsideCrop(m3_x, m3_y, crop), isInsideCrop(m4_x, m4_y, crop)]):
		print(f"Going for top feature for {outputFileName}")
		cropImage(imagePath, aspectRatio, top_feature, top_feature, outputFileName)
		return
	croppedImage = originalImage.crop((left, top, right, bottom))
	croppedImage.show()
	croppedImage.save(f"{outputFileName}.jpeg")












