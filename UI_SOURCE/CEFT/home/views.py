from django.shortcuts import render
import os
from django.views.generic import TemplateView, FormView
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework import viewsets, permissions, exceptions, response
from utils.do import cropSalienctAspects, generateBackProjectionData
from django.views.decorators.csrf import csrf_exempt

from .forms import SaliencyForm
from .utils import get_graph_img
from .serializers import CEFTSerializer
from .models import SaliencyImage
from django.conf.urls.static import static
import json


class MessageView(TemplateView):
	template_name = 'message.html'

class HomeView(TemplateView):
	template_name = 'home.html'

class CEFTTemplateView(TemplateView):
	template_name = 'ceft.html'

class SaliencyTemplateView(FormView):
	template_name = 'saliency.html'
	form_class = SaliencyForm
	var = True

	def form_valid(self, form):
		if form.is_valid():
			obj = form.save()
			if obj.image.name[:-4] != ".jpeg":
				self.var = False
				return super(SaliencyTemplateView, self).form_valid(SaliencyForm)
			obj.save()
			obj.name = ((obj.image.name).split("."))[0]
			obj.save()
			image_path, image_name = obj.image.path, obj.name
			cropSalienctAspects(image_name, image_path, obj)
			generateBackProjectionData(image_name, image_path, obj)
		return super(SaliencyTemplateView, self).form_valid(SaliencyForm)

	def get_success_url(self):
		if not self.var:
			return "/message"
		obj = SaliencyImage.objects.last()
		return f"/saliency-analysis/{obj.id}/"



class SaliencyAnalysisView(TemplateView):
	template_name = 'saliency_analysis.html'

	def get_context_data(self, *args, **kwargs):
		obj = SaliencyImage.objects.get(id = kwargs['imageId'])
		return {"image": obj}



class CEFTApiView(APIView):
	permission_classes = (
        permissions.AllowAny,
    )

	@csrf_exempt
	def post(self, request):
		request_data 	= 	self.request.data
		serializer 		= 	CEFTSerializer(data = request_data)
#		print(serializer.initial_data)
		if not serializer.is_valid():
			raise exceptions.ValidationError(serializer.errors)
		f = open('i.txt', 'w+')
		nprocessors 		= serializer.data['nprocessors']
		ntasks 				= serializer.data['ntasks']
		nedges 				= serializer.data['nedges']
		processing_time 	= serializer.data['processing_time']
		edges 	 			= serializer.data['edges']
		inp 				= f"{nprocessors}\n{ntasks} {nedges}\n"
		for pt in processing_time:
			inp += " ".join([str(t) for t in pt])
			inp += '\n'
		for ed in edges:
			inp += " ".join([str(t) for t in ed])
			inp += '\n'
		f.write(inp)
#		print(inp)
		f.close()
		os.system("g++ -std=c++14 main_ceft.cpp -o kk && ./kk  < i.txt > o.txt") 
		string = open('o.txt', 'r+').readlines()
		string = ''.join(string)
		string = string.replace('\n', '<br/>')
#		print('making image')
		try:
			img  = get_graph_img(ntasks, nedges, edges)
		except:
			img = "w.jpg"
		data = {
			"result": string,
			"image": f"{img}"
		}
		return response.Response(data)









