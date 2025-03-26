from django.shortcuts import render, redirect
import django.contrib.auth as auth
from django.contrib import messages
from .forms import *
from django.db.models import Q 
from django.http import JsonResponse
import datetime
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .decorators import *


# Constanti
USER_TYPE_CLIENTE = "Cliente"
USER_TYPE_ALBERGATORE = "Albergatore"


'''
Gestisce la registrazione di un cliente.

Reindirizza alla pagina di login se la registrazione è valida, altrimenti 
renderizza la pagina di registrazione con il form.
'''
def registerCliente(request):
    form = RegisterForm()
    
    if(request.method == "POST"):
        form = RegisterForm(request.POST)
        
        # se il form è valido imposta isAlbergatore su false e salva le informazioni
        if(form.is_valid()):
            user = form.save(commit=False)
            user.set_isAlbergatore(False)
            user.save()
            return redirect("login")
    
    context = {
        'registerFormCliente' : form, 
        "actor" : USER_TYPE_CLIENTE
    }
    
    return render(request, 'register.html', context)



'''
Gestisce la registrazione di un albergatore.

Reindirizza alla pagina di login se la registrazione è valida, altrimenti 
renderizza la pagina di registrazione con il form.
'''
def registerAlbergatore(request):
    form = RegisterForm()
    
    if(request.method == "POST"):
        form = RegisterForm(request.POST)
        
        # se il form è valido imposta isAlbergatore su true e salva le informazioni
        if(form.is_valid()):
            user = form.save(commit=False)
            user.set_isAlbergatore(True)
            user.save()
            return redirect("login")  
    
    context = {
        'registerFormAlbergatore' : form,
        "actor" : USER_TYPE_ALBERGATORE
    }
    
    return render(request, 'register.html', context)



'''
Valida se l'utente corrisponde al tipo di utente specificato.
'''
def is_valid_user_type(user, user_type):
    if user_type == USER_TYPE_CLIENTE:
        return not user.is_albergatore() or user.is_Staff()
    elif user_type == USER_TYPE_ALBERGATORE:
        return user.is_albergatore() or user.is_Staff()
    return False



'''
Gestisce il processo di login dell'utente in base al tipo di utente.
'''
def login_user(request, user_type):
    form = LoginForm(data=request.POST)
    
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = auth.authenticate(request, username=username, password=password)
        
        if user:
            if is_valid_user_type(user, user_type):                    
                auth.login(request, user)
                return True, form
            else:
                form.add_error(None, f"Credenziali non valide: Non sei un {user_type}")
        else:
            form.add_error(None, "Username o password non validi.")
    
    return False, form



'''
Gestisce il login sia di un cliente che di un albergatore.

Reindirizza alla home se il login è valido, altrimenti
renderizza la pagina di login con i form.
'''
def login(request):
    formCliente = LoginForm()
    formAlbergatore = LoginForm()
    
    if(request.method == "POST"):
        # gestione login cliente
        if("buttonCliente" in request.POST):
            flag, formCliente = login_user(request, USER_TYPE_CLIENTE)
            if(flag):
                request.session["button"] = "buttonCliente"
                return redirect("home")
        
        # gestione login albergatore
        if("buttonAlbergatore" in request.POST):
            flag, formAlbergatore = login_user(request, USER_TYPE_ALBERGATORE)
            if(flag):
                request.session["button"] = "buttonAlbergatore"
                return redirect("home")
                
    context = {
        "loginFormCliente" : formCliente,
        "loginFormAlbergatore" : formAlbergatore
    }
    
    return render(request, 'login.html', context)



'''
Visualizza la pagina per effettuare il recupero della password.
'''
def passwordDimenticata(request):   
    return render(request, 'passwordDimenticata.html')



'''
Esegue il logout dell'utente.

L'utente deve essere autenticato.
'''
@login_required
def logout(request):
    if(request.user.is_active):
        auth.logout(request)
        return redirect("login") 



'''
Visualizza la home per l'utente loggato.

L'utente deve essere autenticato
'''
@login_required
def home(request):
    user = request.user
    aggiorna_prenotazioni_attive()
    
    if(user.is_Staff()):
        if("buttonCliente" in request.session["button"]):
            user.set_isAlbergatore(False)
        elif("buttonAlbergatore" in request.session["button"]):
            user.set_isAlbergatore(True)
        
    
    # Filtra gli alberghi dell'albergatore con almeno una camera
    alberghi = Albergo.objects.filter(albergatore=user).annotate(num_camere=Count('camera')).filter(num_camere__gt=0)
    
    # Filtra le camere degli alberghi dell'albergatore
    camere = Camera.objects.filter(albergo__in=alberghi)
    
    # Trovo le prenotazioni legate alle camere e le ordino in ordine crescente 
    prenotazioni_albergatore = Prenotazione.objects.filter(camera__in=camere).order_by('-dataPrenotazione')
    
    prenotazioni_attive_cliente = Prenotazione.objects.filter(cliente=user, isAttiva=True).order_by('-dataPrenotazione')
    
    
    if not user.is_albergatore():      
        context = {
            "user" : user,
            "prenotazioni_attive" : prenotazioni_attive_cliente
        }
    else:
        context = {
            "user" : user,
            "prenotazioni" : prenotazioni_albergatore
        }
    
    return render(request, "home.html", context)



'''
Visualizza la pagina per effettuare nuove prenotazioni per l'utente loggato.

L'utente deve essere autenticato e deve essere un cliente
'''
@cliente_required
def ricercaPrenotazione(request):
    form = NewPrenotazioneForm()
    queryResult = None
    queryFlag = False
    data_inizio = datetime.date.today
    data_fine = datetime.date.today
    numeroPersone = None 
    
    if(request.method == "POST"):
        form = NewPrenotazioneForm(request.POST)
    
        if form.is_valid():
            localita = form.cleaned_data.get('localita')
            numeroPersone = form.cleaned_data.get('numeroPersone')
            data_inizio = form.cleaned_data.get('dataInizio')
            data_fine = form.cleaned_data.get('dataFine')
            
            # Filtra gli alberghi per località
            alberghi = Albergo.objects.filter(localita__icontains=localita)
            
            # Filtra le camere per alberghi e numero posti letto che saranno maggiori uguali alle persone che alloggierrano 
            # tenendo conto del limite 
            camere = Camera.objects.filter(albergo__in=alberghi, postiLetto__gte=numeroPersone).order_by('postiLetto')
            
            # Trova le camere con prenotazioni attive
            camere_prenotate = Prenotazione.objects.filter(camera__in=camere, isAttiva=True).order_by('-dataPrenotazione')
    
            
            # Esclude le camere con prenotazioni attive che rispettano i casi precedenti
            camere_disponibili = camere.exclude(id__in=camere_prenotate.values_list("camera_id", flat=True))
            
            queryFlag = True  
            
            if(camere_disponibili is not None):
                queryResult = camere_disponibili
            else:
                queryResult = None
            
    context = {
        "prenotazioneForm" : form,
        "queryResult" : queryResult,
        "queryFlag" : queryFlag,
        "dataInizio": data_inizio,
        "dataFine": data_fine,
        "numeroPersone": numeroPersone
    }
    
    return render(request, "nuovaPrenotazione.html", context)



'''
Permette all'utente di effettuare una nuova prenotazione

L'utente deve essere autenticato e deve essere un cliente
'''
@cliente_required
def nuovaPrenotazione(request):
    if request.method == "POST":
        camera_id = request.POST.get('camera_id')
        dataInizio = request.POST.get('dataInizio')
        dataFine = request.POST.get('dataFine')
        numeroPersone = request.POST.get('numeroPersone')
        
        camera = Camera.objects.get(id = camera_id)
        
        prenotazione = Prenotazione.objects.create(
            dataInizio=datetime.datetime.strptime(dataInizio, "%Y-%m-%d").date(),
            dataFine=datetime.datetime.strptime(dataFine, "%Y-%m-%d").date(),
            dataCancellazione=timezone.now().date(),
            isAttiva=True,
            totale=0.0,
            numPersone=numeroPersone,
            cliente=request.user, 
            camera=camera
        )
        
        # Calcola il totale della prenotazione
        prenotazione.calcolo_totale()
        
        # Calcola della data di cancellazione
        prenotazione.calcolo_dataCancellazione()
        
        # Salva la prenotazione nel database
        prenotazione.save()
        
        messages.success(request, "Camera prenotata con successo")
    
    return redirect("home") 



'''
Vengono aggiornate le prenotazioni
'''
def aggiorna_prenotazioni_attive():
    prenotazioni_attive = Prenotazione.objects.filter(isAttiva=True)
    for prenotazione in prenotazioni_attive:
        prenotazione.aggiornaPrenotazione()



'''
Permette all'utente di visualizzare le proprie prenotazioni sia attive che passate

L'utente deve essere autenticato e deve essere un cliente
'''
@cliente_required
def prenotazioniCliente(request):   
    aggiorna_prenotazioni_attive()   
    
    utente = request.user

    # Filtra le prenotazioni attive
    prenotazioni_attive = Prenotazione.objects.filter(cliente=utente, isAttiva=True, dataCancellazione__lt= timezone.now().date()).order_by('-dataPrenotazione')
    
    # filtra le prenotazioni attive annullabili
    prenotazioni_attive_annullabili = Prenotazione.objects.filter(cliente=utente, isAttiva=True, dataCancellazione__gte= timezone.now().date()).order_by('-dataPrenotazione')
    
    # filra le prenotazioni passate
    prenotazioni_passate = Prenotazione.objects.filter(cliente=utente, isAttiva=False).order_by('-dataPrenotazione')
    

    context = {
        'prenotazioni_attive': prenotazioni_attive,
        'prenotazioni_attive_annullabili': prenotazioni_attive_annullabili,
        'prenotazioni_passate': prenotazioni_passate
    }
    
    return render(request, "prenotazioniCliente.html", context)



'''
Visualizza la pagina per vedere le camere dell'albergatore.

L'utente deve essere autenticato e deve essere un albergatore
'''
@albergatore_required
def camereAlbergatore(request):
    #prendo solo gli alberghi che hanno camere di un certo utente 
    alberghi = Albergo.objects.filter(albergatore=request.user).annotate(num_camere=Count('camera')).filter(num_camere__gt=0)
    camere = Camera.objects.filter(albergo__albergatore=request.user).order_by('postiLetto')
    
    context = {
        'alberghi': alberghi,
        'camere': camere
    }
    
    return render(request, 'camereAlbergatore.html', context)



'''
Permette all'utente di gestire le proprie prenotazioni

L'utente deve essere autenticato e deve essere un albergatore
'''
@albergatore_required
def gestisciPrenotazioni(request): 
    aggiorna_prenotazioni_attive()
    
    utente = request.user

    # Filtra gli alberghi dell'albergatore con almeno una camera
    alberghi = Albergo.objects.filter(albergatore=utente).annotate(num_camere=Count('camera')).filter(num_camere__gt=0)

    # Filtra le camere degli alberghi dell'albergatore
    camere = Camera.objects.filter(albergo__in=alberghi)

    # Filtra le prenotazioni attive con data di cancellazione maggiore di quella odierna
    prenotazioni_attive = Prenotazione.objects.filter(camera__in=camere, isAttiva=True, dataCancellazione__gte= timezone.now().date()).order_by('-dataPrenotazione')
    
    
    
    context = {
        'prenotazioni_attive' : prenotazioni_attive
    }
    
    return render(request, 'gestisciPrenotazioni.html', context)



'''
Permette all'utente di cancellare una propria prenotazione attiva

L'utente deve essere autenticato
'''
@login_required
def annullaPrenotazione(request): 
    if request.method == "POST":
        prenotazione_id = request.POST.get('prenotazione_id')
        
        #prendo il primo risultato della ricerca delle prenotazioni
        prenotazione = Prenotazione.objects.filter(id=prenotazione_id).first()
        
        prenotazione.delete()
        messages.success(request, 'Prenotazione annullata con successo.')
    
    if(request.user.isAlbergatore):
        return redirect('gestisciPrenotazioni')

    return redirect("prenotazioniCliente")
    



'''
Permette all'utente di aggiungere una nuova camera ad un albergo

L'utente deve essere autenticato e deve essere un albergatore
'''
@albergatore_required
def aggiungiCamera(request):
    form = NewCameraForm(user=request.user)
    
    if request.method == 'POST':
        form = NewCameraForm(user=request.user, data=request.POST, files=request.FILES)
        
        if form.is_valid():
            camera = form.save(commit=False)
            camera.save()
            messages.success(request, 'Camera aggiunta con successo!')
            
            return redirect('camereAlbergatore')          

    context = {
        "form" : form
    }
    
    return render(request, 'aggiungiCamera.html', context)



'''
Permette all'utente di aggiungere un nuovo albergo vuoto

L'utente deve essere autenticato e deve essere un albergatore
'''
@albergatore_required
def aggiungiAlbergo(request):
    form = NewAlbergoForm()

    if request.method == 'POST':
        form = NewAlbergoForm(request.POST)
        
        if form.is_valid():
            albergo = form.save(commit=False)        
            albergo.albergatore = request.user
            albergo.save()
            
            messages.success(request, 'Albergo aggiunto con successo!')
            
            return redirect('camereAlbergatore')  
        
    context = {
        "form" : form
    }      

    return render(request, 'aggiungiAlbergo.html', context)



'''
Permette all'utente di cancellare una camera da un albergo se essa non ha prenotazioni attive

L'utente deve essere autenticato e deve essere un albergatore
'''
@albergatore_required
def cancellaCamera(request):  
    camera_id = request.POST.get('camera_id') 
    
    #prendo il primo risultato della ricerca delle camere
    camera = Camera.objects.filter(id=camera_id).first()
    
    prenotazioni_attive = Prenotazione.objects.filter(camera=camera, isAttiva=True).order_by('-dataPrenotazione')
    
            
    if prenotazioni_attive.exists():
        messages.error(request, 'Non puoi eliminare questa camera perché ha prenotazioni attive.')
        
    else:
        camera.delete()
        messages.success(request, 'Camera eliminata con successo.')
    
    return redirect('camereAlbergatore')



'''
Permette all'utente di cancellare un albergo se non ha camere con prenotazioni attive

L'utente deve essere autenticato e deve essere un albergatore
'''
@albergatore_required
def cancellaAlbergo(request):
    albergo_id = request.POST.get('albergo_id')
     
    #prendo il primo risultato della ricerca degli alberghi   
    albergo = Albergo.objects.filter(id=albergo_id).first()
    
    camere = Camera.objects.filter(albergo=albergo)
    
    prenotazioni_attive = Prenotazione.objects.filter(camera__in=camere, isAttiva=True).order_by('-dataPrenotazione')
    
            
    if prenotazioni_attive.exists():
        messages.error(request, 'Non puoi eliminare questo albergo perché una o più camere hanno prenotazioni attive.')
        
    else:
        # Elimina tutte le camere associate e l'albergo
        camere.delete()
        albergo.delete()
        messages.success(request, 'Albergo eliminato con successo.')
       
    return redirect('camereAlbergatore')



'''
Verifica se l'email inserita è presente o meno nel database
'''
def verifica_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        if Utente.objects.filter(email=email).exists():
            return JsonResponse({'exists': True})
        else:
            return JsonResponse({'exists': False})

    return JsonResponse({'error': 'Metodo non consentito'}, status=405)



'''
Permette all'utente di visualizzare lo storico delle sue prenotazioni (sia attive che passate)

L'utente deve essere autenticato e deve essere un albergatore
'''
@albergatore_required
def storicoPrenotazioni(request):
    aggiorna_prenotazioni_attive()
        
    utente = request.user

    # Filtra gli alberghi dell'albergatore con almeno una camera
    alberghi = Albergo.objects.filter(albergatore=utente).annotate(num_camere=Count('camera')).filter(num_camere__gt=0)

    # Filtra le camere degli alberghi dell'albergatore
    camere = Camera.objects.filter(albergo__in=alberghi)

    # Filtra le prenotazioni attive e passate delle camere trovate
    prenotazioni_attive = Prenotazione.objects.filter(camera__in=camere, isAttiva=True).order_by('-dataPrenotazione')
    
    prenotazioni_passate = Prenotazione.objects.filter(camera__in=camere, isAttiva=False).order_by('-dataPrenotazione')


    context = {
        'prenotazioni_attive': prenotazioni_attive,
        'prenotazioni_passate': prenotazioni_passate
    }

    return render(request, 'storicoPrenotazioni.html', context)