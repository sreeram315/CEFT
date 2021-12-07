from django.db import models
from datetime import datetime

# Create your models here.

class SaliencyImage(models.Model):
	name 		= models.CharField(null = True, max_length = 256)
	image 		= models.ImageField(null = True, blank = True)
	created_at 	= models.DateTimeField(auto_now_add=True, null = True, blank = True)
	updated_at 	= models.DateTimeField(auto_now=True, null = True, blank = True)

	def __str__(self):
		return self.name