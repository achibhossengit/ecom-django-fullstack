from django.views import View
from django.db import models
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.shortcuts import render
from product.models import Category, Product
from .models import Country, City, Area, Zone

def homepage(request):
    categories = Category.objects.prefetch_related('images').order_by("?")[:5]
    products = Product.objects.order_by("?").select_related('category', 'inventory').prefetch_related('images')[:8]
    for p in products:
        p.image = p.images.all()[0] if p.images.all() else None

    for c in categories:
        c.image = c.images.all()[0] if c.images.all() else None
        
    context = {
        'categories': categories,
        'products': products,
        'hero_product': products[0],
    }
    return render(request, 'pages/home.html', context=context)



class ShopView(View):
    def get(self, request):
        products = Product.objects.select_related(
            'category', 'inventory'
        ).prefetch_related('images', 'reviews').order_by('-created_at')

        # filters
        search = request.GET.get('search', '')
        category_id = request.GET.get('category', '')
        min_price = request.GET.get('min_price', '')
        max_price = request.GET.get('max_price', '')
        sort = request.GET.get('sort', '')

        if search:
            products = products.filter(name__icontains=search)
        if category_id:
            products = products.filter(category_id=category_id)
        if min_price:
            products = products.filter(inventory__price__gte=min_price)
        if max_price:
            products = products.filter(inventory__price__lte=max_price)
        if sort == 'price_asc':
            products = products.order_by('inventory__price')
        elif sort == 'price_desc':
            products = products.order_by('-inventory__price')
        elif sort == 'newest':
            products = products.order_by('-created_at')

        paginator = Paginator(products, 12)
        page = request.GET.get('page', 1)
        products = paginator.get_page(page)

        categories = Category.objects.all()

        return render(request, 'pages/shop.html', {
            'products': products,
            'categories': categories,
            'search': search,
            'category_id': category_id,
            'min_price': min_price,
            'max_price': max_price,
            'sort': sort,
        })
        
class ShopDetailView(View):
    def get(self, request, pk):
        product = get_object_or_404(
            Product.objects.select_related('category', 'inventory')
            .prefetch_related('images', 'reviews'),
            pk=pk
        )
        reviews = product.reviews.all().order_by('-created_at')
        review_count = reviews.count()
        avg_rating = reviews.aggregate(avg=models.Avg('rating'))['avg'] or 0

        return render(request, 'pages/shop_detail.html', {
            'product': product,
            'reviews': reviews,
            'review_count': review_count,
            'avg_rating': round(avg_rating, 1),
        })

class CategoryListView(View):
    def get(self, request):
        categories = Category.objects.prefetch_related('images').all()
        return render(request, 'pages/categories.html', {'categories': categories})


class AboutView(View):
    def get(self, request):
        return render(request, 'pages/about.html')



# ===========================
# ADDRESS RELATED CORE VIEWS
# ==========================
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