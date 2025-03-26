from django.core.exceptions import PermissionDenied

'''
Verifica se l'utente autenticato è un cliente. Se lo è, il sistema può 
eseguire la view associata all'url a cui si statentando di accedere, altrimenti 
viene restituito un errore.
'''
def cliente_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if(request.user.is_authenticated and not request.user.is_albergatore()):
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
        
    return _wrapped_view_func


'''
Verifica se l'utente autenticato è un albergatore. Se lo è, il sistema può 
eseguire la view associata all'url a cui si sta tentando di accedere, altrimenti 
viene restituito un errore.
'''
def albergatore_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if(request.user.is_authenticated and request.user.is_albergatore()):
            return view_func(request, *args, **kwargs)
        else:
            raise PermissionDenied
        
    return _wrapped_view_func