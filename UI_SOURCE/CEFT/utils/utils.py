def cropImage(imagePath, aspectRatio, salientCoordinates, outputFileName = "output"):
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

	# print(top, bottom, left, right)
	croppedImage = originalImage.crop((left, top, right, bottom))
	croppedImage.show()
	croppedImage.save(f"{outputFileName}.jpeg")