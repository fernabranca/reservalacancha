from django.shortcuts import render_to_response
from django.template import RequestContext
from website.models import Deporte, Cancha, Reserva

def index(request):

	canchas = Cancha.objects.all()

	return render_to_response('index.html', {'canchas': canchas},
        context_instance=RequestContext(request))
 

def list(request):

	return render_to_response('list.html', 
		context_instance=RequestContext(request))

def detail(request):
	
	return render_to_response('detail.html',
		context_instance=RequestContext(request))

def mis_res(request):
	
	return render_to_response('list_res.html',
		context_instance=RequestContext(request))

def login(request):
	
	return render_to_response('login.html',
		context_instance=RequestContext(request))