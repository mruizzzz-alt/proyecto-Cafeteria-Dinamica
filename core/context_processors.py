from .models import Negocio
from .models import Negocio, Profile
# tienda/context_processors.

def negocio_context(request):
    return {'negocio': Negocio.objects.first()}

def configuracion_tienda(request):
    # Obtenemos el único registro de configuración o creamos uno por defecto si no existe
    config = ConfiguracionTienda.objects.first()
    return {
        'config': config
    }

def negocio_context(request):
    return {
        'negocio': Negocio.objects.first()
    }

def profile_context(request):
    profile = None

    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(user=request.user)

    return {
        'profile': profile
    }
