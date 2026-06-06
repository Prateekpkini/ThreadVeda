import os
import urllib.request
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils.text import slugify
from store.models import Category, Product, ProductImage, Review
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Populates the database with premium mock clothes, categories, images, and reviews'

    def handle(self, *args, **options):
        self.stdout.write('Populating database...')
        
        # Create superuser / default users if they don't exist
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            email='admin@threadveda.com',
            is_staff=True,
            is_superuser=True
        )
        admin_user.set_password('admin123')
        admin_user.save()

        user1, _ = User.objects.get_or_create(username='aarav', email='aarav@gmail.com')
        user1.first_name = 'Aarav'
        user1.save()

        user2, _ = User.objects.get_or_create(username='ananya', email='ananya@gmail.com')
        user2.first_name = 'Ananya'
        user2.save()

        user3, _ = User.objects.get_or_create(username='vihaan', email='vihaan@gmail.com')
        user3.first_name = 'Vihaan'
        user3.save()

        # Define categories
        categories_data = [
            {'name': 'Menswear', 'slug': 'menswear', 'icon': 'fa-solid fa-person'},
            {'name': 'Womenswear', 'slug': 'womenswear', 'icon': 'fa-solid fa-person-dress'},
            {'name': 'Accessories', 'slug': 'accessories', 'icon': 'fa-solid fa-glasses'},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={'name': cat_data['name'], 'icon': cat_data['icon'], 'is_active': True}
            )
            categories[cat.slug] = cat

        # Define products
        products_data = [
            # Menswear
            {
                'name': 'Premium Italian Silk Blazer',
                'category_slug': 'menswear',
                'price': 8999.00,
                'discount_price': 7499.00,
                'short_description': 'Exquisitely tailored blazer crafted from premium Italian silk blend. Perfect for smart-casual and formal occasions.',
                'description': 'Elevate your wardrobe with the Premium Italian Silk Blazer. Meticulously tailored for a modern slim fit, it features a textured silk-wool blend, notch lapels, dual rear vents, and premium horn buttons. Inside, a fully lined satin interior ensures maximum comfort and effortless layering. Designed to bridge the gap between traditional tailoring and modern sophistication.',
                'sizes': 'M, L, XL, XXL',
                'colors': 'Navy Blue, Charcoal Gray, Beige',
                'material': '70% Silk, 30% Wool',
                'stock': 12,
                'is_featured': True,
                'is_new_arrival': True,
                'is_bestseller': True,
                'image_url': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop&q=80',
                'reviews': [
                    {'user': user1, 'rating': 5, 'title': 'Outstanding quality!', 'comment': 'The blazer fits perfectly and the fabric feels incredibly premium. Def worth the price!'},
                    {'user': user2, 'rating': 4, 'title': 'Very elegant', 'comment': 'Bought this for my husband. He looks great in it. The texture of silk is beautiful.'}
                ]
            },
            {
                'name': 'Classic Linen Button-Down Shirt',
                'category_slug': 'menswear',
                'price': 2499.00,
                'discount_price': None,
                'short_description': 'Breathable, relaxed-fit shirt woven from 100% pure Belgian flax linen. Keep cool and classic.',
                'description': 'Woven from premium Belgian flax, our Classic Linen Button-Down Shirt offers unmatched breathability and a lightweight feel. Pre-washed for exceptional softness, it features a relaxed button-down collar, single chest pocket, and adjustable button cuffs. It develops character with every wash, embodying effortless summer elegance.',
                'sizes': 'S, M, L, XL',
                'colors': 'White, Olive Green, Sky Blue',
                'material': '100% Linen',
                'stock': 25,
                'is_featured': False,
                'is_new_arrival': True,
                'is_bestseller': False,
                'image_url': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80',
                'reviews': [
                    {'user': user3, 'rating': 5, 'title': 'Perfect summer shirt', 'comment': 'Super breathable. Love the Sky Blue color. Great relaxed fit.'}
                ]
            },
            # Womenswear
            {
                'name': 'Silk Wrap Midi Dress',
                'category_slug': 'womenswear',
                'price': 5999.00,
                'discount_price': 4999.00,
                'short_description': 'Flowing midi-length wrap dress in pure mulberry silk. A timeless, flattering silhouette.',
                'description': 'Crafted from 100% pure mulberry silk, the Silk Wrap Midi Dress features a adjustable wrap waist closure that flatters every silhouette. A delicate V-neckline, subtle balloon sleeves, and a flowing tiered skirt offer an elegant drape and movement. Fully lined with soft breathable viscose for comfortable all-day wear.',
                'sizes': 'XS, S, M, L',
                'colors': 'Emerald Green, Ruby Red, Midnight Black',
                'material': '100% Mulberry Silk',
                'stock': 8,
                'is_featured': True,
                'is_new_arrival': False,
                'is_bestseller': True,
                'image_url': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&auto=format&fit=crop&q=80',
                'reviews': [
                    {'user': user2, 'rating': 5, 'title': 'In love with this dress!', 'comment': 'The dress drapes beautifully. Emerald green color is gorgeous and the silk feels amazing.'}
                ]
            },
            {
                'name': 'Double-Breasted Wool Trench Coat',
                'category_slug': 'womenswear',
                'price': 12999.00,
                'discount_price': 9999.00,
                'short_description': 'Timeless double-breasted trench coat tailored from premium merino wool blend.',
                'description': 'Designed for winter warmth and timeless style, our Double-Breasted Wool Trench Coat features a structured double-breasted closure, waist belt, buttoned shoulder epaulets, and hand-warmer pockets. The heavy-weight merino wool blend keeps wind and cold out, while a premium jacquard satin lining allows for smooth layering over thick sweaters.',
                'sizes': 'S, M, L, XL',
                'colors': 'Camel, Charcoal, Navy',
                'material': '80% Merino Wool, 20% Nylon',
                'stock': 4,
                'is_featured': True,
                'is_new_arrival': True,
                'is_bestseller': False,
                'image_url': 'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=600&auto=format&fit=crop&q=80',
                'reviews': []
            },
            # Accessories
            {
                'name': 'Minimalist Chronograph Leather Watch',
                'category_slug': 'accessories',
                'price': 7999.00,
                'discount_price': None,
                'short_description': 'Sleek, minimalist timepiece with genuine Italian leather strap and Japanese quartz movement.',
                'description': 'A masterclass in minimalist design. This chronograph features a 40mm stainless steel case, clean sub-dials, sapphire crystal glass, and a supple, genuine Italian full-grain leather strap. Powered by a reliable Japanese quartz movement, it is water-resistant up to 50 meters, perfect for daily wear and formal occasions.',
                'sizes': 'FREE',
                'colors': 'Tan-Silver, Black-Gold',
                'material': 'Stainless Steel & Italian Leather',
                'stock': 15,
                'is_featured': False,
                'is_new_arrival': False,
                'is_bestseller': True,
                'image_url': 'https://images.unsplash.com/photo-1522312346375-d1a52e2b99b3?w=600&auto=format&fit=crop&q=80',
                'reviews': [
                    {'user': user1, 'rating': 5, 'title': 'Simply elegant', 'comment': 'Looks much more expensive than it is. Very comfortable strap.'}
                ]
            },
            {
                'name': 'Handcrafted Full-Grain Leather Satchel',
                'category_slug': 'accessories',
                'price': 6499.00,
                'discount_price': 5499.00,
                'short_description': 'Spacious and durable messenger bag handcrafted from premium full-grain vegetable-tanned leather.',
                'description': 'Carry your daily essentials in style with our Handcrafted Leather Satchel. Woven by expert artisans, it is constructed from premium vegetable-tanned full-grain leather that develops a beautiful patina over time. Features a padded laptop sleeve (up to 14"), multiple organizer pockets, adjustable shoulder strap, and brass hardware.',
                'sizes': 'FREE',
                'colors': 'Tan, Dark Brown',
                'material': 'Full-Grain Leather',
                'stock': 10,
                'is_featured': True,
                'is_new_arrival': True,
                'is_bestseller': True,
                'image_url': 'https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600&auto=format&fit=crop&q=80',
                'reviews': []
            }
        ]

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

        for p_data in products_data:
            cat = categories[p_data['category_slug']]
            product, created = Product.objects.get_or_create(
                name=p_data['name'],
                defaults={
                    'category': cat,
                    'price': p_data['price'],
                    'discount_price': p_data['discount_price'],
                    'short_description': p_data['short_description'],
                    'description': p_data['description'],
                    'sizes': p_data['sizes'],
                    'colors': p_data['colors'],
                    'material': p_data['material'],
                    'stock': p_data['stock'],
                    'is_featured': p_data['is_featured'],
                    'is_new_arrival': p_data['is_new_arrival'],
                    'is_bestseller': p_data['is_bestseller'],
                    'is_active': True
                }
            )

            # Download and save image if none exists
            if created or not product.images.exists():
                try:
                    self.stdout.write(f"Downloading image for {product.name}...")
                    req = urllib.request.Request(p_data['image_url'], headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as response:
                        img_file = ContentFile(response.read())
                        filename = f"{slugify(product.name)}.jpg"
                        
                        pi = ProductImage(product=product, is_primary=True)
                        pi.image.save(filename, img_file, save=True)
                        
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Failed to download image for {product.name}: {e}"))

            # Create reviews
            for rev_data in p_data['reviews']:
                Review.objects.get_or_create(
                    user=rev_data['user'],
                    product=product,
                    defaults={
                        'rating': rev_data['rating'],
                        'title': rev_data['title'],
                        'comment': rev_data['comment']
                    }
                )

        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
