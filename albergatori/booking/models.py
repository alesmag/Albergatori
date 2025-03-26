from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MaxValueValidator, MinValueValidator
import datetime

'''
manager di Utente
gestisce le istanze di Utente
'''
class UtenteManager(BaseUserManager):
    # creazione di Utenti normali (clienti e albergatori)
    def create_user(self, username, email, password=None, **extra_fields):
        if(not username):
            raise ValueError("Username obbligatorio")
        
        if(not email):
            raise ValueError("Email obbligatoria")
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    
    # creazione di superusers (amministratori)
    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


'''
il model Utente è impostato come model di autenticazione di django
all'interno viene specificato che gli oggetti di Utente (quindi le sue istanze)
sono gestite tramite UtenteManager
'''
class Utente (AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, primary_key=True) 
    password = models.CharField(max_length=50)
    nome = models.CharField(max_length=80)
    cognome = models.CharField(max_length=80)
    email = models.CharField(max_length=100)
    telefono = models.IntegerField(blank=True, null=True)
    isAlbergatore = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UtenteManager()
    
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "Utente"
        verbose_name_plural = "Utenti"

    def __str__(self):
        return self.username

    def get_username(self):
        return self.username

    def get_nome(self):
        return self.nome

    def get_cognome(self):
        return self.cognome

    def get_email(self):
        return self.email

    def get_telefono(self):
        return self.telefono
    
    def is_albergatore(self):
        return self.isAlbergatore
    
    def is_Staff(self):
        return self.is_staff
    
    def set_isAlbergatore(self, isAlbergatore):
        self.isAlbergatore = isAlbergatore
    
    

class Albergo (models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    localita = models.CharField(max_length=100)
    
    numStelle =  models.IntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    
    albergatore = models.ForeignKey(Utente, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = "Albergo"
        verbose_name_plural = "Alberghi"
    
    def __str__(self):
        return f"{self.id} - {self.nome}"

    def get_id (self):
        return self.id
    
    def get_nome (self):
        return self.nome
    
    def get_localita (self):
        return self.localita
    
    def get_numStelle (self):
        return self.numStelle
    
    def get_albergatore (self):
        return self.albergatore
    
    
'''
Enumerato per la classe Camera
'''
class Tipologia (models.TextChoices):
    SINGOLA = "SINGOLA"
    DOPPIA = "DOPPIA"
    JUNIOR_SUITE = "JUNIOR SUITE"
    SUITE = "SUITE"
    
    
    
class Camera (models.Model):
    numeroCamera = models.IntegerField()
    postiLetto = models.IntegerField(default=1)
    tempoCancellazione = models.IntegerField(default=10)
    prezzo = models.DecimalField(default=0.0, max_digits=6, decimal_places=2)
    tipologia = models.CharField(max_length=20, choices=Tipologia.choices, default=Tipologia.SINGOLA)
    albergo = models.ForeignKey(Albergo, on_delete=models.PROTECT)
    immagine = models.ImageField(blank=True, null=True)
    descrizione = models.TextField(null=True)
    
    class Meta:
        unique_together = (('numeroCamera', 'albergo'))
        verbose_name = "Camera"
        verbose_name_plural = "Camere"
        
    #override del metodo save di django cosi da impostare i numeri di posti letto in automatico
    def save(self, *args, **kwargs):
        tipologia_posti_letto = {
            Tipologia.SINGOLA: 1,
            Tipologia.DOPPIA: 2,
            Tipologia.JUNIOR_SUITE: 3,
            Tipologia.SUITE: 4
        }
        
        self.postiLetto = tipologia_posti_letto.get(self.tipologia, 1)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return  f"{self.numeroCamera} - {self.albergo}"
    
    def get_numeroCamera(self):
        return self.numeroCamera
    
    def get_postiLetto(self):
        return self.postiLetto
    
    def get_tempoCancellazione(self):
        return self.tempoCancellazione
    
    def get_prezzo(self):
        return self.prezzo
    
    def get_tipologia(self):
        return self.tipologia
    
    def get_albergo(self):
        return self.albergo
    
    def get_immagine(self):
        return self.immagine
    
    def get_descrizione(self):
        return self.descrizione
    
    
    
class Prenotazione (models.Model):
    id = models.AutoField(primary_key=True)
    dataInizio = models.DateField(default=timezone.now)
    dataFine = models.DateField(default=timezone.now)
    dataCancellazione = models.DateField(default=timezone.now)
    dataPrenotazione = models.DateField(default=timezone.now)
    isAttiva = models.BooleanField(default=False)
    totale = models.DecimalField(default=0.0, max_digits=8, decimal_places=2)
    numPersone = models.IntegerField(default=1)
    cliente = models.ForeignKey(Utente, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.PROTECT)
    
    class Meta:
        verbose_name = "Prenotazione"
        verbose_name_plural = "Prenotazioni"
    
    def __str__(self):
        return  f"{self.id} - {self.isAttiva}"
    
    def get_id(self):
        return self.id
    
    def get_dataInizio(self):
        return self.dataInizio
    
    def get_dataFine(self):
        return self.dataFine
    
    def get_dataPrenotazione(self):
        return self.dataPrenotazione
    
    def is_attiva(self):
        return self.isAttiva
    
    def get_totale(self):
        return self.totale
    
    def get_numPersona(self):
        return self.numPersone
    
    def get_cliente(self):
        return self.cliente
    
    def get_camera(self):
        return self.camera
    
    def calcola_notti(self):
        if(self.dataFine > self.dataInizio and self.is_attiva()):
            return (self.dataFine - self.dataInizio).days
        else:
            return 0
        
    def calcolo_totale(self):
        if(self.dataFine > self.dataInizio):
            self.totale = self.calcola_notti() * self.camera.get_prezzo()
            
    def calcolo_dataCancellazione(self):
            self.dataCancellazione = self.dataInizio - datetime.timedelta(days=self.camera.get_tempoCancellazione())
            
    def aggiornaPrenotazione(self):
        if self.dataFine < timezone.now().date():
            self.isAttiva = False
            
        self.save()
