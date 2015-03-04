#encoding:utf-8
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from website.models import Deporte, Cancha, Reserva, Complejo
from forms import UserForm, CanchaForm, ComplejoForm, RecoveryForm
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group
import time
from datetime import date
from datetime import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login 
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
import string
import random

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
	complejos = Complejo.objects.all()

	return render_to_response('index.html', 
		{'complejos': complejos, 
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

			u = authenticate(username=request.POST['username'],
				password=request.POST['password'])
			login(request, u)

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
@login_required(login_url='/login/')
@user_passes_test(is_client)
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
	messages.info(request, "Tu reserva fue realizada con exito")

	#aqui se envia un mail informando la reserva al propietario
	body = 'Datos de la reserva:' + '\n'
	body = body + 'Complejo: ' + reserva.cancha.complejo.nombre + '\n'
	body = body + 'Deporte: ' + reserva.cancha.deporte.nombre + '\n'
	body = body + 'Cancha: ' + str(reserva.cancha.numero_cancha) + '\n'
	body = body + 'Fecha: ' + reserva.fecha.strftime('%d-%m-%Y')+ '\n'
	body = body + 'Hora: ' + reserva.hora + ':00hs' '\n \n'
	body = body + 'Datos del cliente: ' + '\n'
	body = body + 'Nombre de usuario: ' + reserva.usuario.username + '\n'
	body = body + 'Nombre: ' + reserva.usuario.first_name + '\n'
	body = body + 'Apellido: ' + reserva.usuario.last_name + '\n'
	body = body + 'Correo: ' + reserva.usuario.email + '\n'
	
	propietario = reserva.cancha.complejo.duenio
	email_enviar = EmailMessage(
		subject='¡Tienes una nueva reserva!', 
		body= body, 
		to=[propietario.email])

	email_enviar.send()
	
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
	#constantes de posibilidades de estado
	cancelada = 'Cancelada por el Cliente'
	rechazada = 'Rechazada por Propietario'
	aprobada = 'Aprobada por el propietario'

	if is_client(user) or is_propiertario(user):
		id_reserva = request.POST.get('id_reserva', '-1')
		reserva = get_object_or_404(Reserva, pk=id_reserva)
		reserva.estado = request.POST.get('estado')
		reserva.save()
		messages.info(request, "Haz cambiado el estado de la reserva exitosamente")

		#se envia un mail informando del cambio de estado
		body = 'Datos de la reserva:' + '\n'
		body = body + 'Complejo: ' + reserva.cancha.complejo.nombre + '\n'
		body = body + 'Deporte: ' + reserva.cancha.deporte.nombre + '\n'
		body = body + 'Cancha: ' + str(reserva.cancha.numero_cancha) + '\n'
		body = body + 'Fecha: ' + reserva.fecha.strftime('%d-%m-%Y')+ '\n'
		body = body + 'Hora: ' + reserva.hora + ':00hs' '\n \n'

		subject = 'Reserva ' + reserva.estado

		if reserva.estado == rechazada or reserva.estado == aprobada:
			to = reserva.usuario.email
		else:
			to = reserva.cancha.complejo.duenio.email
			body = body + 'Datos del cliente: ' + '\n'
			body = body + 'Nombre de usuario: ' + reserva.usuario.username + '\n'
			body = body + 'Nombre: ' + reserva.usuario.first_name + '\n'
			body = body + 'Apellido: ' + reserva.usuario.last_name + '\n'
			body = body + 'Correo: ' + reserva.usuario.email + '\n'

		email_enviar = EmailMessage(
			subject=subject, 
			body= body, 
			to=[to])

		email_enviar.send()

	if is_client(user):
		return redirect('/reservas')
	elif is_propiertario(user):
		return redirect('/reservaspropietario')

#muestra las canchas de un propietario
@login_required(login_url='/login/')
@user_passes_test(is_propiertario)
def mis_canchas(request):

	user = request.user
	complejos = Complejo.objects.filter(duenio=user)
	results = Cancha.objects.filter(complejo=complejos).order_by('-id')

	return render_to_response('list_canchas_propietario_1.html',
		{'results': results,
		'complejos': complejos,
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

	if cancha.complejo.duenio == user:
		cancha.delete()

	return redirect('/miscanchas')

#visualizar reservas para un propietario
@login_required(login_url='/login/')
@user_passes_test(is_propiertario)
def my_reserves_propietary(request):
	
	user = request.user
	complejos = Complejo.objects.filter(duenio=request.user)
	canchas_propietario = Cancha.objects.filter(complejo__in=complejos)

	reservas = Reserva.objects.filter(cancha__in=canchas_propietario).order_by('-id')

	return render_to_response('list_reserves_propietario.html',
		{'results': reservas,
		'user': user,
		'today': datetime.now()},
		context_instance=RequestContext(request))


#Creacion canchas
@login_required(login_url='/login/')
@user_passes_test(is_propiertario)
def crear_cancha(request):

	if request.method == 'POST':
		form = CanchaForm(request.POST, request.FILES)
		if form.is_valid():
			c = form.save()
			return HttpResponseRedirect('/')
	else:
		form = CanchaForm()
		form.fields["complejo"].queryset = Complejo.objects.filter(duenio=request.user)	
	
	return render_to_response('create_cancha.html', 
		{'form': form},
		context_instance=RequestContext(request))

@login_required(login_url='/login/')
@user_passes_test(is_propiertario)
def modificar_cancha(request, id_cancha):

	cancha = get_object_or_404(Cancha, pk=id_cancha)

	if request.method == 'POST':
		form = CanchaForm(request.POST, request.FILES, instance=cancha)
		if form.is_valid():
			c = form.save()
			return HttpResponseRedirect('/')
	else:
		form = CanchaForm(instance=cancha)
		form.fields["complejo"].queryset = Complejo.objects.filter(duenio=request.user)	

	
	return render_to_response('edit_cancha.html', 
		{'form': form},
		context_instance=RequestContext(request))


@login_required(login_url='/login/')
@user_passes_test(is_propiertario)
def crear_complejo(request):

	if request.method == 'POST':
		form = ComplejoForm(request.POST)
		if form.is_valid():
			c = form.save()
			return HttpResponseRedirect('/')
	else:
		form = ComplejoForm(initial={'duenio': request.user})		
	
	return render_to_response('create_complejo.html', 
		{'form': form},
		context_instance=RequestContext(request))

def detalle_complejo(request, id_complejo):

	complejo = get_object_or_404(Complejo, pk=id_complejo)
	results = Cancha.objects.filter(complejo=complejo)

	return render_to_response('detalle_complejo.html',
		{'results': results,
		'complejo': complejo, 
		'user': request.user,
		}, 
		context_instance=RequestContext(request))


def recovery(request):

	if request.method == 'POST':
		form = RecoveryForm(request.POST)
		if form.is_valid():
			try:
				user = User.objects.get(username=form.data["usuario"])

			except Exception, e:
				messages.info(request, "El usuario ingresado no existe")
				return HttpResponseRedirect('/recuperar')
			
			new_pass = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
			user.set_password(new_pass)
			user.save()

			body = 'Haz solicitado un cambio de contraseña. Hemos generado una automáticamente. \n \n'
			body = body + 'Tu nueva contraseña es: ' + new_pass

			email_enviar = EmailMessage(
				subject='Cambio de contraseña', 
				body= body, 
				to=[user.email])

			email_enviar.send()
			messages.info(request, "Hemos enviado tu nueva contraseña a tu cuenta de email")
			
			return HttpResponseRedirect('/recuperar')
			
	else:
		form = RecoveryForm()
	
	return render_to_response('recovery.html', 
		{'form': form},
		context_instance=RequestContext(request))