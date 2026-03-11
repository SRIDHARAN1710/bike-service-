from django.shortcuts import render
from .models import BikeService

def service_form(request):
    if request.method == "POST":
        model = request.POST['model']
        km = int(request.POST['km'])
        last = int(request.POST['lastService'])
        phone = request.POST['phone']
        email = request.POST['email']

        BikeService.objects.create(
            model=model,
            total_km=km,
            last_service_km=last,
            phone=phone,
            email=email
        )

        # SMS logic will come next
        return render(request, 'service.html', {'success': True})

    return render(request, 'service.html')
