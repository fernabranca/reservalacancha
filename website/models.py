#encoding:utf-8
from django.db import models
from django.contrib.auth.models import User

class Deporte(models.Model):

	nombre = models.CharField(max_length=50)

	def __unicode__(self):
		return self.nombre

class Complejo(models.Model):

	nombre = models.CharField(max_length=50)
	direccion = models.CharField(max_length=100)
	latitud = models.FloatField(null=True, blank=True)
	longitud = models.FloatField(null=True, blank=True)
	duenio = models.ForeignKey(User)

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

	hora_comienzo_atencion = models.CharField(max_length=4,choices=hora_opciones)
	hora_fin_atencion = models.CharField(max_length=4,choices=hora_opciones)
	precio_por_turno = models.FloatField()
	imagen =  models.ImageField(upload_to='canchas', verbose_name='Imágen')
	deporte = models.ForeignKey(Deporte)
	complejo = models.ForeignKey(Complejo)
	numero_cancha = models.IntegerField(blank=True, null=True)

	def save(self, *args, **kwargs):

		if not self.pk:
			no = Cancha.objects.filter(complejo=self.complejo, deporte=self.deporte).count()
			if no == None:
				self.numero_cancha = 1
			else:
				self.numero_cancha = no + 1

		super(Cancha, self).save(*args, **kwargs)

	

	def __unicode__(self):
		return 'Complejo: ' + self.complejo.nombre + ' - Deporte: ' + self.deporte.nombre + ' - Cancha: ' + str(self.numero_cancha)

	def get_open(self):

		horas = [0 , 1 , 2 , 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
		inicio = int(self.hora_comienzo_atencion)
		fin = int(self.hora_fin_atencion)

		return horas[inicio:fin]


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
		return 'Usuario: ' + self.usuario.username + ' - Fecha: ' + self.fecha.strftime("%Y-%m-%d") + ' - Cancha: ' + self.cancha.nombre



