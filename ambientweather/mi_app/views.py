from django.shortcuts import render
from .models import Producto


# Create your views here.
def lista_productos(request):
    productos = Producto.objects.all()  # Obtiene datos de MySQL
    return render(request, 'mi_app/index.html', {'productos': productos})
