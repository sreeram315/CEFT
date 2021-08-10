from django.shortcuts import render
import os
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from rest_framework import viewsets, permissions, exceptions, response

from .utils import get_graph_img
from .serializers import CEFTSerializer
from django.conf.urls.static import static
import json

class HomeView(TemplateView):
	template_name = 'index.html'

class CEFTApiView(APIView):
	permission_classes = (
        permissions.AllowAny,
    )

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









