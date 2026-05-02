from django.http import JsonResponse
from django.shortcuts import render
from product.models import Category, Product
from .models import Country, City, Area, Zone

def homepage(request):
    hero_product = {
        'name': 'Premium Linen Jacket',
        'category': {'name': 'Fashion & Apparel'},
        'price': 49,
        'original_price': 69,
        'discount_percent': 30,
        'tag': 'new',
        'image': 'https://images.unsplash.com/photo-1537465978529-d23b17165b3b?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZGVuaW0lMjBqYWNrZXR8ZW58MHx8MHx8fDA%3D'
    }
    
    categories = Category.objects.all()[:5]
    products = Product.objects.all().order_by("created_at").select_related('inventory').prefetch_related('images')[:12]
    
    context = {'categories': categories, 'products': products, "hero_product": hero_product}
    return render(request, 'pages/home.html', context=context)


def ajax_load_countries(request):
    countries = list(Country.objects.all().values('id', 'name_en', 'name_bn'))
    return JsonResponse(countries, safe=False)

def ajax_load_cities(request):
    country_id = request.GET.get('country_id')
    if not country_id:
        return JsonResponse([], safe=False)
    cities = list(City.objects.filter(country_id=country_id).values('id', 'name_en', 'name_bn'))
    return JsonResponse(cities, safe=False)

def ajax_load_areas(request):
    city_id = request.GET.get('city_id')
    if not city_id:
        return JsonResponse([], safe=False)
    areas = list(Area.objects.filter(city_id=city_id).values('id', 'name_en', 'name_bn'))
    return JsonResponse(areas, safe=False)

def ajax_load_zones(request):
    area_id = request.GET.get('area_id')
    if not area_id:
        return JsonResponse([], safe=False)
    zones = list(Zone.objects.filter(area_id=area_id).values('id', 'name_en', 'name_bn'))
    return JsonResponse(zones, safe=False)