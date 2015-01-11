#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User

class Deporte(models.Model):

	nombre = models.CharField(max_length=50)

	def __unicode__(self):
		return self.nombre

class Cancha(models.Model):

	#tupla para manejar los horarios
	hora_opciones=(
		('0','00.00 hs'), ('1','01.00 hs'), ('2','02.00 hs'),
		('3','03.00 hs'), ('4','04.00 hs'), ('5','05.00 hs'),
		('6','06.00 hs'), ('7','07.00 hs'), ('8','08.00 hs'),
		('9','09.00 hs'), ('10','10.00 hs'), ('11','11.00 hs'),
		('12','12.00 hs'), ('13','13.00 hs'), ('14','14.00 hs'),
		('15','15.00 hs'), ('16','16.00 hs'), ('17','17.00 hs'),
		('18','18.00 hs'), ('19','19.00 hs'), ('20','20.00 hs'),
		('21','21.00 hs'), ('22','22.00 hs'), ('23','23.00 hs'),
	)

	nombre = models.CharField(max_length=50)
	direccion = models.CharField(max_length=100)
	latitud = models.FloatField(null=True, blank=True)
	longitud = models.FloatField(null=True, blank=True)
	hora_comienzo_atencion = models.CharField(max_length=4,choices=hora_opciones)
	hora_fin_atencion = models.CharField(max_length=4,choices=hora_opciones)
	precio_por_turno = models.FloatField()
	imagen =  models.ImageField(upload_to='canchas', verbose_name='Imágen')
	deporte = models.ForeignKey(Deporte)
	duenio = models.ForeignKey(User)

	def __unicode__(self):
		return self.nombre


class Reserva(models.Model):

	#tupla para manejar los horarios
	hora_opciones=(
		('0','00.00 hs'), ('1','01.00 hs'), ('2','02.00 hs'),
		('3','03.00 hs'), ('4','04.00 hs'), ('5','05.00 hs'),
		('6','06.00 hs'), ('7','07.00 hs'), ('8','08.00 hs'),
		('9','09.00 hs'), ('10','10.00 hs'), ('11','11.00 hs'),
		('12','12.00 hs'), ('13','13.00 hs'), ('14','14.00 hs'),
		('15','15.00 hs'), ('16','16.00 hs'), ('17','17.00 hs'),
		('18','18.00 hs'), ('19','19.00 hs'), ('20','20.00 hs'),
		('21','21.00 hs'), ('22','22.00 hs'), ('23','23.00 hs'),
	)

	hora = models.CharField(max_length=4,choices=hora_opciones)
	fecha = models.DateField()
	estado = models.CharField(max_length=50)
	cancha = models.ForeignKey(Cancha)
	usuario = models.ForeignKey(User)

	def __unicode__(self):
		return 'Usuario: ' + self.usuario.username + ' - Fecha: ' + self.fecha.strftime("%Y-%m-%d")



