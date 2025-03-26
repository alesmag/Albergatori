from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# gestione della classe Utente visualizzabile tramite la parte di amministrazione del sito
class UtenteAdmin(UserAdmin):
    model = Utente
    list_display = ('username', 'email', 'nome', 'cognome', 'is_staff', 'is_active', 'isAlbergatore')
    list_filter = ('is_staff', 'is_active', 'isAlbergatore')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Informazioni Personali', {'fields': ('nome', 'cognome', 'telefono')}),
        ('Permessi', {'fields': ('is_staff', 'is_active', 'isAlbergatore', 'is_superuser', 'groups', 'user_permissions')}),
        ('Date Importanti', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'isAlbergatore')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)


admin.site.register(Utente, UtenteAdmin)
admin.site.register(Albergo)
admin.site.register(Camera)
admin.site.register(Prenotazione)
