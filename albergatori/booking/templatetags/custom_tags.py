# Importo il modulo con le classi per implementare nuovi tag
from django import template

# Creo un nuovo registro di tags
register = template.Library()

'''
@register.simple_tag -> decoratore che permette di registrare un nuovo tag custom che esegue la 
                        funzione specificata in questo file

Input: 
- numero intero

Output:
La funzione ritorna una sequenza di numeri del tipo: [0, limite-1].

Serve per implementare un ciclo while per il quale non esiste un django tag. Con questa funzione
possiamo iterare su una sequenza di numeri.
'''
@register.simple_tag
def while_tag(limite):
    try:
        limite = int(limite)  # Converto limite in un intero
    except ValueError:
        return range(0)  # Ritorna un range vuoto se non può essere convertito
    return range(limite)

'''
@register.filter -> decoratore che permette di registrare la funzione definita come
                    un filtro custom da poter usare nei propri template
                    
name='nometag' -> assegno un nome al tag

Input: 
- la lista delle camere da filtrare
- il nome di un albergo 

Output:
La funzione ritorna tramite la set comprehension l'insieme delle camere
che hanno lo stesso attributo albergo rispetto a quello passato come parametro
'''
@register.filter(name='filtra_camere_per_albergo')
def filtra_camere_per_albergo(camere, albergo):
    return [camera for camera in camere if camera.albergo == albergo]