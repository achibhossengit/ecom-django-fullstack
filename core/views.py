from django.shortcuts import render

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
    
    categories = [
    {
        'name': 'Fashion & Apparel',
        'subtitle': 'Explore',
        'image': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ62USkwMwqewjC_YGt6MUa8b4h8q4TV5PQiw&s',  # fashion clothes photo
        'button_text': 'Shop Now',
    },
    {
        'name': 'Electronics',
        'image': 'https://images.unsplash.com/photo-1510557880182-3b7f8415f0b2?auto=format&fit=crop&w=800&q=80',  # electronics workstation
    },
    {
        'name': 'Home & Living',
        'image': 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&q=80',  # home interior photo
    },
    {
        'name': 'Beauty',
        'image': 'https://images.unsplash.com/photo-1495107334309-fcf20504a5ab?auto=format&fit=crop&w=800&q=80',  # beauty makeup/photo
    },
    {
        'name': 'Sports',
        'image': 'https://images.unsplash.com/photo-1521412644187-c49fa049e84d?auto=format&fit=crop&w=800&q=80',  # sports gear
        'badge': '🔥',
    },
    ]

    products = [
    {
        'name': 'Premium Linen Jacket',
        'category': {'name': 'Fashion & Apparel'},
        'price': 49,
        'original_price': 69,
        'discount_percent': 30,
        'tag': 'new',
        'image': 'https://images.unsplash.com/photo-1537465978529-d23b17165b3b?w=500&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8Mnx8ZGVuaW0lMjBqYWNrZXR8ZW58MHx8MHx8fDA%3D'
    },
    {
        'name': 'Wireless Earbuds Pro',
        'category': {'name': 'Electronics'},
        'price': 129,
        'original_price': 149,
        'discount_percent': 15,
        'tag': 'top rated',
        'image': 'https://images.unsplash.com/photo-1722439667098-f32094e3b1d4?q=80&w=435&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'
    },
    {
        'name': 'Ceramic Vase Set',
        'category': {'name': 'Home & Living'},
        'price': 38,
        'original_price': 50,
        'discount_percent': 25,
        'tag': '',
        'image': 'https://images.unsplash.com/photo-1616627989852-403fdf7a2a7e?auto=format&fit=crop&w=500&q=80'
    },
    {
        'name': 'Glow Serum Kit',
        'category': {'name': 'Beauty'},
        'price': 65,
        'original_price': None,
        'discount_percent': None,
        'tag': 'top rated',
        'image': 'https://images.unsplash.com/photo-1600185361257-bb21dbb7b6a7?auto=format&fit=crop&w=500&q=80'
    },
    {
        'name': 'Trail Runner Shoes',
        'category': {'name': 'Sports'},
        'price': 89,
        'original_price': 109,
        'discount_percent': 18,
        'tag': '',
        'image': 'https://images.unsplash.com/photo-1600181953697-5d3f3d35f65b?auto=format&fit=crop&w=500&q=80'
    },
    {
        'name': 'Portable Charger',
        'category': {'name': 'Electronics'},
        'price': 45,
        'original_price': None,
        'discount_percent': None,
        'tag': 'top rated',
        'image': 'https://images.unsplash.com/photo-1580910051071-25d42de0a6d6?auto=format&fit=crop&w=500&q=80'
    },
    {
        'name': 'Denim Co-ord Set',
        'category': {'name': 'Fashion & Apparel'},
        'price': 72,
        'original_price': 95,
        'discount_percent': 24,
        'tag': 'top rated',
        'image': 'https://images.unsplash.com/photo-1600185361314-67a2f273b28f?auto=format&fit=crop&w=500&q=80'
    },
    {
        'name': 'Linen Cushion Cover',
        'category': {'name': 'Home & Living'},
        'price': 24,
        'original_price': 30,
        'discount_percent': 20,
        'tag': 'top rated',
        'image': 'https://images.unsplash.com/photo-1600185361256-4b7a5e3a9c3e?auto=format&fit=crop&w=500&q=80'
    },
]

    context = {'categories': categories, 'products': products, "hero_product": hero_product}
    return render(request, 'home.html', context=context)
