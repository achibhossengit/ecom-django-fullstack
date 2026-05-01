from django.shortcuts import render
from product.models import Category, Product

# Create your views here.
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
