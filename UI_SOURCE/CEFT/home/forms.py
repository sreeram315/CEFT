from django import forms
from .models import SaliencyImage

class SaliencyForm(forms.ModelForm):
	class Meta:
		model = SaliencyImage
		exclude = ["name"]