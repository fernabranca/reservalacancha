from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from website.models import Deporte, Cancha, Reserva
from forms import UserForm, CanchaForm
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
import time
from datetime import date
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test


#saber si un usuario es cliente
def is_client(user):
    return user.groups.filter(name='Clientes').exists()

def is_propiertario(user):
    return user.groups.filter(name='Propietarios').exists()

#pagina principal
def index(request):

	if is_propiertario(request.user):
		return redirect("/miscanchas")
	user = request.user
	canchas = Cancha.objects.all()

	return render_to_response('index.html', 
		{'canchas': canchas, 
		'user': user},
        context_instance=RequestContext(request))
 
#registro de usuarios
def register(request):

	if request.method == 'POST':
		form = UserForm(request.POST)
		if form.is_valid():
			group = request.POST['group']
			print 'choice ' + group
			u = form.save()
			g = Group.objects.get(name=group) 
			g.user_set.add(u)
			return HttpResponseRedirect('/')
	else:
		form = UserForm()
	
	return render_to_response('register.html', 
		{'form': form},
		context_instance=RequestContext(request))

#listado de canchas de un determinado deporte
def search(request):
	query = request.GET.get('q', '')
	user = request.user
	results = []
	if query:
		deporte = Deporte.objects.filter(nombre__icontains=query).distinct()
		if deporte:
			results = Cancha.objects.filter(deporte=deporte)

	return render_to_response('list_canchas_cliente.html',
		{'results': results, 
		'user': user,
		'q': query}, 
		context_instance=RequestContext(request))


#detalle de una determinada cancha para una determinada fecha
def detail(request):
	user = request.user
	id_cancha = request.GET.get('id', '-1')
	cancha = get_object_or_404(Cancha, pk=id_cancha)
	
	fecha = request.GET.get('date', time.strftime("%Y-%m-%d"))
	fecha_lista = fecha.split('-')

	reservas = Reserva.objects.filter(
		cancha=cancha, 
		fecha__year=fecha_lista[0],
		fecha__month=fecha_lista[1],
		fecha__day=fecha_lista[2]).exclude(
		estado='Cancelada por el Cliente').exclude(
		estado='Rechazada por Propietario')

	horas_abierto = cancha.get_open()
	horas_reservadas = []

	for reserva in reservas:
		horas_reservadas.append(int(reserva.hora))

	horas_disponibles = [item for item in horas_abierto if item not in horas_reservadas]
	
	return render_to_response('detail.html', 
		{'cancha': cancha, 
		'user': user,
		'fecha': fecha,
		'disponibles': horas_disponibles,
		'fecha_actual': time.strftime("%Y-%m-%d")},
        context_instance=RequestContext(request))

#crea reserva a una determinada cancha
@login_required(login_url='/login/')
@user_passes_test(is_client)
def reserve(request):

	fecha = request.POST['fecha'].split('-')
	id_cancha = request.POST['id_cancha']

	hora = request.POST['hora']
	fecha = date(int(fecha[0]), int(fecha[1]), int(fecha[2]))
	estado = 'Pendiente de aprobacion'
	cancha = get_object_or_404(Cancha, pk=id_cancha)
	user = request.user
	
	reserva = Reserva(
		hora=hora,
		fecha=fecha,
		estado=estado,
		cancha=cancha,
		usuario=user
		)
	reserva.save()

	return redirect('/reservas')

#visualizar reservas
@login_required(login_url='/login/')
@user_passes_test(is_client)
def my_reserves_client(request):
	
	user = request.user
	reservas = Reserva.objects.filter(usuario=user).order_by('-id')

	return render_to_response('list_reserves_client.html',
		{'results': reservas,
		'user': user,
		'today': datetime.now()},
		context_instance=RequestContext(request))		


#moderar reservas
@login_required(login_url='/login/')
def moderate_reserve(request):
	
	user = request.user

	if is_client(user) or is_propiertario(user):
		id_reserva = request.POST.get('id_reserva', '-1')
		reserva = get_object_or_404(Reserva, pk=id_reserva)
		reserva.estado = request.POST.get('estado')
		reserva.save()

	if is_client(user):
		return redirect('/reservas')
	elif is_propiertario(user):
		return redirect('/reservaspropietario')

#muestra las canchas de un propietario
@login_required(login_url='/login/')
@user_passes_test(is_propiertario)
def mis_canchas(request):

	user = request.user
	canchas = Cancha.objects.filter(duenio=user).order_by('-id')

	return render_to_response('list_canchas_propietario.html',
		{'results': canchas,
		'user': user,
		'today': datetime.now()},
		context_instance=RequestContext(request))


#elimina la cancha de un propietario		
@login_required(login_url='/login/')
@user_passes_test(is_propiertario)
def eliminar_cancha(request):

	user = request.user
	id_cancha = request.POST.get('id_cancha', '-1')
	cancha = get_object_or_404(Cancha, pk=id_cancha)

	if cancha.duenio == user:
		cancha.delete()

	return redirect('/mis_canchas')

#visualizar reservas para un propietario
@login_required(login_url='/login/')
@user_passes_test(is_propiertario)
def my_reserves_propietary(request):
	
	user = request.user
	canchas_propietario = Cancha.objects.filter(duenio=user)

	reservas = Reserva.objects.filter(cancha__in=canchas_propietario).order_by('-id')

	return render_to_response('list_reserves_propietario.html',
		{'results': reservas,
		'user': user,
		'today': datetime.now()},
		context_instance=RequestContext(request))


#Creacion canchas
def crear_cancha(request):

	if request.method == 'POST':
		form = CanchaForm(request.POST, request.FILES)
		if form.is_valid():
			c = form.save()
			return HttpResponseRedirect('/')
	else:
		form = CanchaForm(initial={'duenio': request.user})
		
	
	return render_to_response('create_cancha.html', 
		{'form': form},
		context_instance=RequestContext(request))
