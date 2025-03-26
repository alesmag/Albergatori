from django.test import TestCase, LiveServerTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.urls import reverse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from .models import *
from .forms import *
import datetime
import time
import os


# TEST UNITARI

class TestsModelUtenteManager(TestCase):
    # setup dei dati iniziali
    def setUp(self):
        # si utilizza lo stesso modello utente che l'applicazione django utilizza
        self.User = get_user_model()
    
    
    # test di creazione di un nuovo utente con successo
    def test_create_user_success(self):
        user = self.User.objects.create_user(
            username = "testuser",
            email = "test@email.it",
            password = "password"
        )
        
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@email.it")
        self.assertTrue(user.check_password("password"))
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
    
    
    # test di creazione di un utente in caso manchi lo username
    def test_create_user_no_username(self):
        with self.assertRaises(ValueError) as e:
            self.User.objects.create_user(
                username = "",
                email = "test@email.it",
                password = "password"
            )
        
        self.assertEqual(str(e.exception), "Username obbligatorio")


    # test di creazione di un utente in caso manchi l'email
    def test_create_user_no_email(self):
        with self.assertRaises(ValueError) as e:
            self.User.objects.create_user(
                username = "testuser",
                email = "",
                password = "password"
            )
        
        self.assertEqual(str(e.exception), "Email obbligatoria")


    # test di creazione di un utente amministratore con successo
    def test_create_superuser_success(self):
        superuser = self.User.objects.create_superuser(
            username = "testadmin",
            email = "testadmin@email.it",
            password = "password"
        )
        
        self.assertEqual(superuser.username, "testadmin")
        self.assertEqual(superuser.email, "testadmin@email.it")
        self.assertTrue(superuser.email, "testadmin@email.it")
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
    
    
    # test di creazione di un utente amministratore in caso manchi is_staff
    def test_create_superuser_no_is_staff(self):
        with self.assertRaises(ValueError) as e:
            self.User.objects.create_superuser(
                username = "testadmin",
                email = "testadmin@email.it",
                password = "password",
                is_staff = False
            )
            
        self.assertEqual(str(e.exception), "Superuser must have is_staff=True.")
    
    
    # test di creazione di un utente amministratore in caso manchi is_superuser
    def test_create_superuser_no_is_superuser(self):
        with self.assertRaises(ValueError) as e:
            self.User.objects.create_superuser(
                username = "testadmin",
                email = "testadmin@email.it",
                password = "password",
                is_superuser = False
            )
            
        self.assertEqual(str(e.exception), "Superuser must have is_superuser=True.")



class TestsModelUtente(TestCase):
    # setup dei dati iniziali
    def setUp(self):
        # si utilizza lo stesso modello utente che l'applicazione django utilizza
        self.User = get_user_model()
        
        self.user = self.User.objects.create_user(
            username = "testuser",
            email = "test@email.it",
            password = "password",
            nome = "testnome",
            cognome = "testcognome"
        )
    
    # test del metodo __str__
    def test_str_method(self):
        self.assertEqual(str(self.user), self.user.username)
    
    
    # test getters
    def test_getters(self):
        self.assertEqual(self.user.get_username(), self.user.username)
        self.assertEqual(self.user.get_email(), self.user.email)
        self.assertEqual(self.user.get_nome(), self.user.nome)
        self.assertEqual(self.user.get_cognome(), self.user.cognome)
        self.assertIsNone(self.user.get_telefono())
        self.assertFalse(self.user.is_albergatore())
        self.assertFalse(self.user.is_Staff())
        
    
    # test setters
    def test_setters(self):
        self.user.set_isAlbergatore(True)
        self.assertTrue(self.user.is_albergatore())



class TestsModelAlbergo(TestCase):
    # setup dei dati iniziali
    def setUp(self):
        self.albergatore = Utente.objects.create(
            username = "albergatore",
            email = "test@email.it",
            password = "password",
            nome = "nome",
            cognome = "cognome",
            isAlbergatore = True
        )
        
        self.albergo = Albergo.objects.create(
            nome = "test albergo",
            localita = "test",
            numStelle = 5,
            albergatore = self.albergatore
        )
        
    
    # test sulla corretta creazione di un albergo
    def test_albergo_creation(self):
        self.assertEqual(self.albergo.nome, "test albergo")
        self.assertEqual(self.albergo.localita, "test")
        self.assertEqual(self.albergo.numStelle, 5)
        self.assertEqual(self.albergo.albergatore, self.albergatore)
    
    
    # test sulla corretta validazione di numStelle
    def test_numStelle_validation(self):
        invalid_numStelle = [0, 6]
        
        for num in invalid_numStelle:
            with self.assertRaises(ValidationError):
                albergo = Albergo(
                    nome = "albergo",
                    localita = "non test",
                    numStelle = num,
                    albergatore = self.albergatore
                )
                
                # attiva la validazione del model
                albergo.full_clean()
    
    
    # test del metodo __str__
    def test_str_method(self):
        self.assertEqual(str(self.albergo), f"{self.albergo.id} - {self.albergo.nome}")
    
    
    # test getters
    def test_getters(self):
        self.assertEqual(self.albergo.get_id(), self.albergo.id)
        self.assertEqual(self.albergo.get_nome(), self.albergo.nome)
        self.assertEqual(self.albergo.get_localita(), self.albergo.localita)
        self.assertEqual(self.albergo.get_numStelle(), self.albergo.numStelle)
        self.assertEqual(self.albergo.get_albergatore(), self.albergo.albergatore)



class TestsModelTipologia(TestCase):
    # test sulle scelte possibili
    def test_scelte_possibili(self):
        scelte_possibili = {
            ("SINGOLA", "Singola"),
            ("DOPPIA", "Doppia"),
            ("JUNIOR SUITE", "Junior Suite"),
            ("SUITE", "Suite")
        }
        
        self.assertEqual(set(Tipologia.choices), scelte_possibili)



class TestsModelCamera(TestCase):
    # setup dei dati iniziali
    def setUp(self):
        self.albergatore = Utente.objects.create(
            username = "albergatore",
            email = "test@email.it",
            password = "password",
            nome = "nome",
            cognome = "cognome",
            isAlbergatore = True
        )
        
        self.albergo = Albergo.objects.create(
            nome = "test albergo",
            localita = "test",
            numStelle = 5,
            albergatore = self.albergatore
        )
        
        self.camera = Camera.objects.create(
            numeroCamera = 23,
            postiLetto = 2,
            tempoCancellazione = 10,
            prezzo = 172.51,
            tipologia = Tipologia.DOPPIA,
            albergo = self.albergo,
            immagine = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            descrizione = "camera test"
        )
        
    
    # test sulla corretta creazione di una camera
    def test_camera_creation(self):
        self.assertEqual(self.camera.numeroCamera, 23)
        self.assertEqual(self.camera.postiLetto, 2)
        self.assertEqual(self.camera.tempoCancellazione, 10)
        self.assertEqual(self.camera.prezzo, 172.51)
        self.assertEqual(self.camera.tipologia, Tipologia.DOPPIA)
        self.assertEqual(self.camera.albergo, self.albergo)
        self.assertTrue(self.camera.immagine)
        self.assertEqual(self.camera.descrizione, "camera test")
    
    
    # test sul metodo save
    def test_save_method(self):
        self.camera.tipologia = Tipologia.SUITE
        
        # si richiama il metodo save e si dovrebe aggiornare postiLetto al numero corretto
        self.camera.save()
        
        # ricarica l'oggetto dal database
        self.camera.refresh_from_db()
        
        self.assertEqual(self.camera.postiLetto, 4)
    
    
    # test sul metodo __str__
    def test_str_method(self):
        self.assertEqual(str(self.camera), f"{self.camera.numeroCamera} - {self.camera.albergo}")
    
    
    # test getters
    def test_getters(self):
        self.assertEqual(self.camera.get_numeroCamera(), self.camera.numeroCamera)
        self.assertEqual(self.camera.get_postiLetto(), self.camera.postiLetto)
        self.assertEqual(self.camera.get_tempoCancellazione(), self.camera.tempoCancellazione)
        self.assertEqual(self.camera.get_prezzo(), self.camera.prezzo)
        self.assertEqual(self.camera.get_tipologia(), self.camera.tipologia)
        self.assertEqual(self.camera.get_albergo(), self.camera.albergo)
        self.assertTrue(self.camera.get_immagine())
        self.assertEqual(self.camera.get_descrizione(), self.camera.descrizione)
    
    
    # pulizia dei file residui
    def tearDown(self):
        super().tearDown()
        
        # rimuove i file immagine di test salvati
        if(self.camera.immagine and self.camera.immagine.name):
            file_path = os.path.join(settings.MEDIA_ROOT, self.camera.immagine.name)
            
            if os.path.isfile(file_path):
                os.remove(file_path)
                

                
class TestsModelPrenotazione(TestCase):
    # setup dei dati iniziali
    def setUp(self):
        self.cliente = Utente.objects.create(
            username = "cliente",
            email = "cliente@email.it",
            password = "password",
            nome = "nome cliente",
            cognome = "cognome cliente",
        )
        
        self.albergatore = Utente.objects.create(
            username = "albergatore",
            email = "albergatore@email.it",
            password = "password",
            nome = "nome albergatore",
            cognome = "cognome albergatore",
            isAlbergatore = True
        )
        
        self.albergo = Albergo.objects.create(
            nome = "test albergo",
            localita = "test",
            numStelle = 5,
            albergatore = self.albergatore
        )
        
        self.camera = Camera.objects.create(
            numeroCamera = 23,
            postiLetto = 2,
            tempoCancellazione = 10,
            prezzo = 172.51,
            tipologia = Tipologia.DOPPIA,
            albergo = self.albergo,
            immagine = SimpleUploadedFile(name='test_image.jpg', content=b'', content_type='image/jpeg'),
            descrizione = "camera test"
        )
        
        self.prenotazione = Prenotazione.objects.create(
            dataInizio = timezone.now().date() + datetime.timedelta(days=15),
            dataFine = timezone.now().date() + datetime.timedelta(days=20),
            dataPrenotazione = timezone.now().date(),
            dataCancellazione = timezone.now().date() + datetime.timedelta(days=5),
            isAttiva = True,
            totale = 0,
            numPersone = 2,
            cliente = self.cliente,
            camera = self.camera
        )
    
    
    # test sulla corretta creazione di una prenotazione
    def test_prenotazione_creation(self):
        self.assertTrue(self.prenotazione.isAttiva)
        self.assertEqual(self.prenotazione.numPersone, 2)
        self.assertEqual(self.prenotazione.cliente, self.cliente)
        self.assertEqual(self.prenotazione.camera, self.camera)
    
    
    # test sul calcolo del numero di notti di permanenza
    def test_calcola_notti(self):
        # verifica del corretto funzionamento
        notti = (self.prenotazione.dataFine - self.prenotazione.dataInizio).days
        self.assertEqual(self.prenotazione.calcola_notti(), notti)
        
        # verifica nel caso in cui la prenotazione non è attiva
        self.prenotazione.isAttiva = False
        self.assertEqual(self.prenotazione.calcola_notti(), 0)
        
        # verifica nel caso in cui dataFine è prima di dataInizio
        self.prenotazione.dataFine = self.prenotazione.dataInizio - datetime.timedelta(days=1)
        self.assertEqual(self.prenotazione.calcola_notti(), 0)
    
    
    # test sul calcolo del prezzo totale
    def test_calcolo_totale(self):
        # verifica il corretto funzionamento del metodo
        self.prenotazione.calcolo_totale()
        
        # verifica il che il totale sia effettivamente il valore che ci aspettiamo
        totale = self.prenotazione.calcola_notti() * self.camera.prezzo
        self.assertEqual(self.prenotazione.totale, totale)

    
    # test sul calcolo della data di cancellazione
    def test_calcolo_dataCancellazione(self):
        # verifica il corretto funzionamento del metodo
        self.prenotazione.calcolo_dataCancellazione()
        
        # verifica il che il calcolo dia effettivamente il valore che ci aspettiamo
        data_cancellazione = self.prenotazione.dataInizio - datetime.timedelta(days=self.camera.get_tempoCancellazione())
        self.assertEqual(self.prenotazione.dataCancellazione, data_cancellazione)
    
    
    # test sull'aggiornamento della prenotazione
    def test_aggiornaPrenotazione(self):
        self.prenotazione.dataFine = timezone.now().date() - datetime.timedelta(days=1)
        self.prenotazione.aggiornaPrenotazione()
        self.prenotazione.refresh_from_db()
        self.assertEqual(self.prenotazione.isAttiva, False)
    
    
    # test getters
    def test_getters(self):
        self.assertEqual(self.prenotazione.get_id(), self.prenotazione.id)
        self.assertEqual(self.prenotazione.get_dataInizio(), self.prenotazione.dataInizio)
        self.assertEqual(self.prenotazione.get_dataFine(), self.prenotazione.dataFine)
        self.assertEqual(self.prenotazione.get_dataPrenotazione(), self.prenotazione.dataPrenotazione)
        self.assertEqual(self.prenotazione.is_attiva(), self.prenotazione.isAttiva)
        self.assertEqual(self.prenotazione.get_totale(), self.prenotazione.totale)
        self.assertEqual(self.prenotazione.get_numPersona(), self.prenotazione.numPersone)
        self.assertEqual(self.prenotazione.get_cliente(), self.prenotazione.cliente)
        self.assertEqual(self.prenotazione.get_camera(), self.prenotazione.camera)
    
    
    # pulizia dei file residui
    def tearDown(self):
        super().tearDown()
        
        # rimuove i file immagine di test salvati
        if(self.camera.immagine and self.camera.immagine.name):
            file_path = os.path.join(settings.MEDIA_ROOT, self.camera.immagine.name)
            
            if os.path.isfile(file_path):
                os.remove(file_path)



# TEST DI ACCETTAZIONE (SELENIUM)

class AcceptanceTestsRegisterUtente(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)
    
    
    def tearDown(self):
        self.browser.quit()
    
    
    def test_registrazione_cliente(self):
        # naviga nell'url per la registrazione utente cliente
        self.browser.get(self.live_server_url + reverse("registerCliente"))
        
        # ottiene gli elementi del form e manda i valori inseriti
        self.browser.find_element("name", "username").send_keys("testuser")
        self.browser.find_element("name", "password1").send_keys("password123")
        self.browser.find_element("name", "password2").send_keys("password123")
        self.browser.find_element("name", "nome").send_keys("testnome")
        self.browser.find_element("name", "cognome").send_keys("testcognome")
        self.browser.find_element("name", "email").send_keys("test@email.com")
        self.browser.find_element("name", "telefono").send_keys("123456789")
        
        # submit del form
        time.sleep(2)
        self.browser.find_element("name", "regButton").click()
        time.sleep(2)
        
        # verifica che l'utente venga correttamente reindirizzato
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse("login"))
    
    
    def test_registrazione_albergatore(self):
        # naviga nell'url per la registrazione utente albergatore
        self.browser.get(self.live_server_url + reverse("registerAlbergatore"))
        
        # ottiene gli elementi del form e manda i valori inseriti
        self.browser.find_element("name", "username").send_keys("testuser")
        self.browser.find_element("name", "password1").send_keys("password123")
        self.browser.find_element("name", "password2").send_keys("password123")
        self.browser.find_element("name", "nome").send_keys("testnome")
        self.browser.find_element("name", "cognome").send_keys("testcognome")
        self.browser.find_element("name", "email").send_keys("test@email.com")
        self.browser.find_element("name", "telefono").send_keys("123456789")
        
        # submit del form
        time.sleep(2)
        self.browser.find_element("name", "regButton").click()
        time.sleep(2)
        
        # verifica che l'utente venga correttamente reindirizzato
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse("login"))


class AcceptanceTestsLoginUtente(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)
        
        # creazione degli utenti di test
        
        self.cliente = get_user_model().objects.create_user(
            username = "cliente",
            email = "test@email.it",
            password = "password",
            nome = "testnome",
            cognome = "testcognome",
            isAlbergatore = False
        )
        
        self.albergatore = get_user_model().objects.create_user(
            username = "albergatore",
            email = "test@email.it",
            password = "password",
            nome = "testnome",
            cognome = "testcognome",
            isAlbergatore = True
        )
    
    
    def tearDown(self):
        self.browser.quit()


    def test_login_cliente(self):
        # naviga nell'url per il login utente
        self.browser.get(self.live_server_url + reverse("login"))
        
        # otteniamo il form corretto all'interno della pagina
        formCliente = self.browser.find_element("name", "formCliente")
        
        # ottiene gli elementi del form e manda i valori inseriti
        formCliente.find_element("name", "username").send_keys("cliente")
        formCliente.find_element("name", "password").send_keys("password")
        
        # submit del form
        time.sleep(2)
        self.browser.find_element("name", "buttonCliente").click()
        time.sleep(2)
        
        # verifica che l'utente venga correttamente reindirizzato
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse("home"))
        
        
    def test_login_albergatore(self):
        # naviga nell'url per il login utente
        self.browser.get(self.live_server_url + reverse("login"))
        
        # otteniamo il form corretto all'interno della pagina
        formAlbergatore = self.browser.find_element("name", "formAlbergatore")
        
        # ottiene gli elementi del form e manda i valori inseriti
        formAlbergatore.find_element("name", "username").send_keys("albergatore")
        formAlbergatore.find_element("name", "password").send_keys("password")
        
        # submit del form
        time.sleep(2)
        self.browser.find_element("name", "buttonAlbergatore").click()
        time.sleep(2)
        
        # verifica che l'utente venga correttamente reindirizzato
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse("home"))
        
        
class AcceptanceTestsAggiuntaAlbergo(LiveServerTestCase): 
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)
            
        # creazione degli utenti di test
            
        self.albergatore = get_user_model().objects.create_user(
            username = "albergatore",
            email = "test@email.it",
            password = "password",
            nome = "testnome",
            cognome = "testcognome",
            isAlbergatore = True
        )     
            
    def tearDown(self):
        self.browser.quit()
    
    def test_aggiuntaAlbergo(self):
        # l'utente effettua il login
        AcceptanceTestsLoginUtente.test_login_albergatore(self)
        
        # naviga nell'url per l'aggiunta dell'albergo 
        self.browser.get(self.live_server_url + reverse("aggiungiAlbergo"))
        
        # ottiene gli elementi del form e manda i valori inseriti
        self.browser.find_element("name", "nome").send_keys("hotel")
        self.browser.find_element("name", "localita").send_keys("citta")
        
        numStelle = self.browser.find_element("name", "numStelle")
        numStelle.clear()
        numStelle.send_keys(5)
        
        # submit del form
        time.sleep(2)
        self.browser.find_element("name", "buttonAggiungiAlbergo").click()
        time.sleep(2)
        
        # verifica che l'utente venga correttamente reindirizzato
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse("camereAlbergatore"))



class AcceptanceTestsAggiuntaCamera(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)
    
        # Creo un istanza di albergatore
        self.albergatore = get_user_model().objects.create_user(
            username = "albergatore",
            email = "test@email.it",
            password = "password",
            nome = "testnome",
            cognome = "testcognome",
            isAlbergatore = True
        )
        
        # Creo un istanza di Albergo 
        self.albergo = Albergo.objects.create(
            nome="TestAlbergo",
            localita="TestLocalita",
            numStelle=5,
            albergatore=self.albergatore            
        )
    
    def tearDown(self):
        self.browser.quit()
    
    def test_aggiungi_camera(self):
        # L'utente deve prima fare il login 
        AcceptanceTestsLoginUtente.test_login_albergatore(self)
        
        # Navigo verso la url aggiungiCamera
        self.browser.get(self.live_server_url + reverse("aggiungiCamera"))
        
        # Compilo il form
        self.browser.find_element("name", "tipologia").send_keys('DOPPIA')
        
        # seleziona il primo elemento della lista
        self.albergo = Select(self.browser.find_element("name", "albergo"))
        self.albergo.select_by_index(1)

        self.browser.find_element("name", "tempoCancellazione").send_keys('10')
        self.browser.find_element("name", "prezzo").send_keys("500")
        self.browser.find_element("name", "descrizione").send_keys("Camera molto spaziosa, pulita con interni moderni")
        self.browser.find_element("name", "numeroCamera").send_keys("999")
        
        # Invio il form compilato
        time.sleep(2)
        self.browser.find_element("name", "buttonAggiungiCamera").click()
        
        # Aspetto che il form venga inviato correttamente prima di 
        # eseguire altre operazioni
        time.sleep(2)
        
        # Verifico che l'utente venga riportato alla pagina camereAlbergatore
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse('camereAlbergatore'))
        
        

class AcceptanceTestsNuovaPrenotazione(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(10)

        self.cliente = get_user_model().objects.create_user(
            username="cliente",
            email="test@email.it",
            password="password",
            nome="testnome",
            cognome="testcognome"
        )

        self.albergatore = get_user_model().objects.create_user(
            username="albergatore",
            email="test@email.it",
            password="password",
            nome="testnome",
            cognome="testcognome",
            isAlbergatore=True
        )

        self.albergo = Albergo.objects.create(
            nome="Americaland",
            localita="New York",
            numStelle=5,
            albergatore=self.albergatore
        )

        self.camera = Camera.objects.create(
            numeroCamera=0,
            tempoCancellazione=10,
            prezzo=680,
            tipologia="DOPPIA",
            albergo=self.albergo,
            descrizione="Bella camera, ampia, pulita"
        )

    def tearDown(self):
        self.browser.quit()

    def test_nuovaPrenotazione(self):
        # l'utente effettua il login
        AcceptanceTestsLoginUtente.test_login_cliente(self)

        # naviga nell'url per la ricerca di una camera
        self.browser.get(self.live_server_url + reverse("ricercaPrenotazione"))

        # ottiene gli elementi del form trovati e manda i valori inseriti
        self.browser.find_element("name", "localita").send_keys("New York")
        self.browser.find_element("name", "dataInizio").send_keys((timezone.now().date() + datetime.timedelta(days=2)).strftime("%d-%m-%Y"))
        self.browser.find_element("name", "dataFine").send_keys((timezone.now().date() + datetime.timedelta(days=10)).strftime("%d-%m-%Y"))
        self.browser.find_element("name", "numeroPersone").send_keys(2)

        # submit del form di ricerca
        self.browser.find_element("name", "bottoneCerca").click()
        time.sleep(2)
        
        # trova le camere risultanti dalla ricerca e seleziona il bottone prenota per ogni camera
        risultati = self.browser.find_elements("name", "bottonePrenota")
        
        # effettua uno scroll sul primo risultato trovato (tramite javascript)
        self.browser.execute_script("arguments[0].scrollIntoView(true);", risultati[0])
        
        # aspetta fino a che l'elemento non è cliccabile
        WebDriverWait(self.browser, 10).until(EC.element_to_be_clickable(risultati[0]))
        
        # una volta che l'elemento è cliccabile viene premuto il tasto selezionato (tramite javascript)
        self.browser.execute_script("arguments[0].click();", risultati[0])
        time.sleep(2)
        
        # verifica che l'utente venga correttamente reindirizzato
        self.assertEqual(self.browser.current_url, self.live_server_url + reverse("home"))
