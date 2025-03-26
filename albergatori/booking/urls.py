from django.urls import path
from . import views

urlpatterns = [
    # urls generali
    path('login/', views.login, name = "login"),
    path("logout/", views.logout, name = "logout"),
    path("home/", views.home, name = "home"),
    path("passwordDimenticata/", views.passwordDimenticata, name = "passwordDimenticata"),
    path('verificaEmail/', views.verifica_email, name='verifica_email'),
    path('annullaPrenotazione/', views.annullaPrenotazione, name = 'annullaPrenotazione'),
    
    # urls cliente
    path("register/cliente/", views.registerCliente, name = "registerCliente"),
    path("ricercaPrenotazione/", views.ricercaPrenotazione, name = "ricercaPrenotazione"),
    path("prenotazioniCliente/", views.prenotazioniCliente, name = "prenotazioniCliente"),
    path("prenota/", views.nuovaPrenotazione, name = "prenota"),
    
    # urls albergatore
    path("register/albergatore/", views.registerAlbergatore, name = "registerAlbergatore"),
    path("camereAlbergatore/", views.camereAlbergatore, name = "camereAlbergatore"),
    path("gestisciPrenotazioni/", views.gestisciPrenotazioni, name = "gestisciPrenotazioni"),
    path("storicoPrenotazioni/", views.storicoPrenotazioni, name = "storicoPrenotazioni"),
    path("aggiungiCamera/", views.aggiungiCamera, name = "aggiungiCamera"),
    path("aggiungiAlbergo/", views.aggiungiAlbergo, name = "aggiungiAlbergo"),
    path("cancellaCamera/", views.cancellaCamera, name = "cancellaCamera"),
    path("cancellaAlbergo/", views.cancellaAlbergo, name = "cancellaAlbergo"),
]
