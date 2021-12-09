from django.db import models
from datetime import datetime

# Create your models here.

class SaliencyImage(models.Model):
	name 		= models.CharField(null = True, max_length = 256)
	image 		= models.ImageField(null = True, blank = True)

	topFeature_x 	= models.IntegerField(default = 0, null = True, blank = True)
	topFeature_y 	= models.IntegerField(default = 0, null = True, blank = True)
	mainComponent_x = models.IntegerField(default = 0, null = True, blank = True)
	mainComponent_y = models.IntegerField(default = 0, null = True, blank = True)

	contour1_x = models.IntegerField(default = 0, null = True, blank = True)
	contour1_y = models.IntegerField(default = 0, null = True, blank = True)

	contour2_x = models.IntegerField(default = 0, null = True, blank = True)
	contour2_y = models.IntegerField(default = 0, null = True, blank = True)

	contour3_x = models.IntegerField(default = 0, null = True, blank = True)
	contour3_y = models.IntegerField(default = 0, null = True, blank = True)

	contour4_x = models.IntegerField(default = 0, null = True, blank = True)
	contour4_y = models.IntegerField(default = 0, null = True, blank = True)

	contour1_size = models.IntegerField(default = 0, null = True, blank = True)
	contour2_size = models.IntegerField(default = 0, null = True, blank = True)
	contour3_size = models.IntegerField(default = 0, null = True, blank = True)
	contour4_size = models.IntegerField(default = 0, null = True, blank = True)



	created_at 	= models.DateTimeField(auto_now_add=True, null = True, blank = True)
	updated_at 	= models.DateTimeField(auto_now=True, null = True, blank = True)

	def __str__(self):
		return self.name