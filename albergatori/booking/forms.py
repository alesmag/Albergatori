from django import forms
from .models import *
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
import datetime

'''
form di registrazione utente dinamico
i campi essenziali vengono direttamente ereditati dalla superclasse
possiamo anche specificare dei campi che non si trovano nella superclasse
'''
class RegisterForm(UserCreationForm):
    # formattazione dei campi del form
    username = forms.CharField(max_length=50, label="Username *", required=True)
    nome = forms.CharField(max_length=80, label="Nome *", required=True)
    cognome = forms.CharField(max_length=80, label="Cognome *", required=True)
    email = forms.EmailField(max_length=200, label="E-mail *", required=True)
    telefono = forms.IntegerField(label="Telefono", required=False)
    
    class Meta:
        # prendiamo come model la classe Utente
        model = Utente
        
        # campi visibili del form
        fields = ['username', 'password1', "password2", 'email', 'nome', 'cognome', 'telefono']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        
        # formattazione dei campi di default della superclasse
        self.fields['password1'].label = "Password *"
        self.fields['password2'].label = "Conferma Password *"
        
        for field in ["username", "password1", "password2", "email", "nome", "cognome", "telefono"]:
            self.fields[field].help_text = None
    
    # override dei controlli di django sulla password principale (password1)
    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        
        if(len(password) < 8):
            raise ValidationError("La password deve contenere almeno 8 caratteri")
        
        if(not any(char.isdigit() for char in password)):
            raise ValidationError("La password deve contenere almeno un numero")
        
        if(not any(char.isalpha() for char in password)):
            raise ValidationError("La password deve contenere almeno una lettera")

        return password

    # ovverride dei controlli django sulla password secondaria di conferma (password2)
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if(password1 and password2 and password1 != password2):
            raise ValidationError("Le password non coincidono")

        return password2



'''
form di login utente dinamico
i campi vengono ereditati direttamente dalla superclasse
'''
class LoginForm(AuthenticationForm):
    # formattazione dei campi del form
    username = forms.CharField(label="Username", max_length=50)
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        
        for field in ["username", "password"]:
            self.fields[field].help_text = None
    
    error_messages = {
        "invalid_login": ("Username o password errati"),
        "inactive": ("Questo account è inattivo."),
    }



'''
form dinamico per l'aggiunta di una nuova prenotazione 
'''
class NewPrenotazioneForm(forms.ModelForm):
    # formattazione dei campi del form
    localita = forms.CharField(
        max_length=100, 
        label="Città", 
        required=True, 
        widget = forms.TextInput(
            attrs = {
                'class': 'form-control',
                'placeholder': 'Cerca destinazione',
            }
        )
    )
    
    dataInizio = forms.DateField(
        label="Check-in", 
        required=True,  
        widget = forms.DateInput(
            attrs= {
                'class': 'form-control', 
                'placeholder': 'gg/mm/aaaa', 
                'type': 'date',
                'min': (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
            }
        )
    )
    
    dataFine = forms.DateField(
        label="Check-out", 
        required=True,  
        widget=forms.DateInput(
            attrs = {
                'class': 'form-control', 
                'placeholder': 'gg/mm/aaaa', 
                'type': 'date',
            }
        )
    )
    
    numeroPersone = forms.IntegerField(
        label="Numero persone", 
        required=True,
        widget= forms.TextInput(
            attrs = {
                'class': 'form-control', 
                'type': 'number',
                'placeholder': 'Aggiungi ospiti',
                'min': 1,
                'max': 4,
            }
        )
    )
    
    # campi visibili del form
    class Meta:
        model = Prenotazione
        fields = ['localita', 'dataInizio', 'dataFine', 'numeroPersone']



'''
form dinamico per l'aggiunta di un nuovo albergo
'''
class NewAlbergoForm(forms.ModelForm):
    class Meta:
        model = Albergo
        fields = ['nome', 'localita', 'numStelle']
        labels = {
            'nome': 'Nome',
            'localita': 'Località',
            'numStelle': 'Stelle',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'localita': forms.TextInput(attrs={'class': 'form-control'}),
            'numStelle': forms.NumberInput(attrs={'class': 'form-control'}),
        }



'''
form dinamico per l'aggiunta di una nuova camera
'''
class NewCameraForm(forms.ModelForm):
    tipologia = forms.ChoiceField(
        choices=Tipologia.choices, 
        label="Tipologia",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    albergo = forms.ModelChoiceField(
        queryset=Albergo.objects.none(),  # Inizialmente vuota
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Albergo"
    )
    
    tempoCancellazione = forms.IntegerField(
        label="Tempo di Cancellazione",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    prezzo = forms.FloatField(
        label="Prezzo",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    descrizione = forms.CharField(
        max_length=60,
        label="Descrizione",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    
    numeroCamera = forms.DecimalField(
        label="Numero Camera",
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
    )
    
    immagine = forms.ImageField(
        label="Aggiungi una foto",
        required=False
    )

    class Meta:
        model = Camera
        fields = ['tipologia', 'albergo', 'tempoCancellazione', 'prezzo', 'descrizione', 'numeroCamera', 'immagine']

    def __init__(self, user, *args, **kwargs):
        super(NewCameraForm, self).__init__(*args, **kwargs)
        self.fields['albergo'].queryset = Albergo.objects.filter(albergatore=user) #mostro solo gli alberghi dell'utente che sta creando la camera
