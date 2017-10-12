from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from rest_framework.generics import (CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateAPIView)
from .serializer import ProductCreateUpdateSerializer
import re
from celery import task
import datetime
from datetime import datetime, timedelta
from .tasks import activate,desactivate
from celery import Celery
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.db.models import Q
#from flower.urls import settings

from .forms import ShopForm, ProductForm, UserForm, TraderForm, PictureForm, CollectionForm, PromotionForm, AlbumForm, PicForm, CategoryForm,WishlistForm
import re  # for spiltting words with regex
from django.db.models import Avg, Max, Min
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Shop, Product, User, Trader, Category, Picture, Collection, Promotion, Album, Pic, wish_category,wish_list
import datetime

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        if user is not None:
            if user.is_active:
                login(request, user)
                shops = Shop.objects.all()
                products = Product.objects.all()
                categories = Category.objects.all()
                return render(request, 'boutique1/discover.html',
                              {'shops': shops, 'products': products, 'categories': categories, 'shop0':shop0})
    context = {
        "form": form,
    }
    return render(request, 'boutique1/register.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                shops = Shop.objects.all()
                products = Product.objects.all()
                return redirect('/discover/')
            else:
                return render(request, 'boutique1/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'boutique1/login.html', {'error_message': 'Invalid login'})
    return render(request, 'boutique1/login.html')
#-----------------------------------------------------------------------------------------------------------------------
def discover(request, category=''):
    user = request.user
    promotions=Promotion.objects.filter(is_active=True)
    product_list = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    counter = []
    header = ''
    shop0 = len(list(Shop.objects.filter(owner__user__id=user.id)))
    for c in categories:
        counter.append((c, product_list.filter(category=c).count()))

        # SEARCH
    if 'search' in request.GET:  # If a search is happening
        query = request.GET.get('search')
        query_list = re.sub("[^\w]", " ", query).split()
        q = Q()
        for word in query_list:
            q |= Q(name__icontains=word) | Q(description__icontains=word)
        product_list = product_list.filter(q)
        header = '- search = ' + query + ' - '

    # if price range defined
    if (('min' in request.GET) and ('max' in request.GET)):
        max_p = int(request.GET.get('max'))
        min_p = int(request.GET.get('min'))

        q = Q(price__lte=max_p) & Q(price__gte=min_p)
        product_list = product_list.filter(q)
        print(q)
        header += '- price in = [' + str(min_p) + ', ' + str(max_p) + '] -'

    # if price range defined
    if ('product_type' in request.GET):
        product_type = request.GET.get('product_type')

        q = Q(product_type=product_type)
        product_list = product_list.filter(q)
        if product_type == 'VTG':
            product_type_label = 'Vintage'
        elif product_type == 'HM':
            product_type_label = 'Hand made'
        print(Product.VINTAGE)
        header += '- product type = ' + str(product_type_label) + ' -'

    # counting result elements by category
    counter = []
    for c in categories:
        counter.append((c, product_list.filter(category=c).count()))

    # if we are filtering by category
    if not category == '':
        product_list = product_list.filter(category__label=category)
        header += '- category filter = ' + str(category) + ' -'

    if ('ordering' in request.GET):
        ordering = request.GET.get('ordering')
        if ordering == 'recent':
            product_list = product_list.order_by('create_date')
        elif ordering == 'price_asc':
            product_list = product_list.order_by('price')
        elif ordering == 'price_desc':
            product_list = product_list.order_by('-price')
        header += '- ordered by ' + str(ordering) + ' -'
    else:
        product_list.order_by('create_date')
        header += '- ordered by recent -'

    max_price = product_list.aggregate(Max('price'))
    min_price = product_list.aggregate(Min('price'))

    print(max_price, min_price)

    # PAGINATION
    page = request.GET.get('page', 1)
    paginator = Paginator(product_list, 6)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {
        'header': header,
        'counter': counter,
        'products': products,
        'categories': categories,
        'max_price': max_price,
        'min_price': min_price,
        'shop0': shop0,
        'promotions':promotions,
    }
    return render(request, 'boutique1/discover.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def myShops(request):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        shops = Shop.objects.filter(owner__user=request.user)
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        query = request.GET.get("q")
        if query:
            shops = shops.filter(
                Q(name__icontains=query)
            ).distinct()
            return render(request, 'boutique1/myShops.html', {
                'shops': shops
            })
        else:
            return render(request, 'boutique1/myShops.html', {'shops': shops, 'shop0':shop0})
#-----------------------------------------------------------------------------------------------------------------------
def myProducts(request, filter_by):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        try:
            product_ids = []
            for shop in Shop.objects.filter(owner__user=request.user):
                for product in shop.product_set.all():
                    product_ids.append(product.pk)
            users_products = Product.objects.filter(pk__in=product_ids)
            shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        except Shop.DoesNotExist:
            users_products = []
        return render(request, 'boutique1/myProducts.html', {
            'product_list': users_products,
            'filter_by': filter_by,
            'shop0':shop0
        })
#-----------------------------------------------------------------------------------------------------------------------
def shopDetails(request, shop_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        shop = get_object_or_404(Shop, pk=shop_id)
        collection = Collection.objects.filter(owner__user__id=request.user.id)
        album = Album.objects.filter(owner__user__id=request.user.id)
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        return render(request, 'boutique1/shop_details.html', {'album': album, 'shop': shop, 'shop0':shop0, 'collection': collection})
#-----------------------------------------------------------------------------------------------------------------------
def prodDetails(request, shop_id, product_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        shop = get_object_or_404(Shop, pk=shop_id)
        prod = get_object_or_404(Product, pk=product_id)
        user = shop.owner.user
        return render(request, 'boutique1/prod_details.html', {'shop': shop, 'prod': prod, 'user': user,  'shop0': shop0})
#-----------------------------------------------------------------------------------------------------------------------
def shopSProducts(request, shop_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        shop = get_object_or_404(Shop, pk=shop_id)
        prods = Product.objects.filter(shop = shop)
        print(prods)
        return render(request, 'boutique1/shopSproducts.html', {'shop': shop, 'prods': prods})
#-----------------------------------------------------------------------------------------------------------------------
def product(request, id_product):
    products = Product.objects.filter(id=id_product)
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    print(products)
    context = {
        "products": products,
        'shop0':shop0
    }

    return render(request, 'boutique1/prod_details.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def create_shop(request):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    elif not hasattr(request.user, 'trader'):
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        form = TraderForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            trader = form.save(commit=False)
            trader.user = request.user
            trader.save()
            return render(request, 'boutique1/create_shop.html/')
        context = {
            "form_name": "You have to signup as a Trader to continue",
            "form": form,
            'shop0':shop0
        }
        return render(request, 'boutique1/form_template2.html', context)
    else:
        form = ShopForm(request.POST or None, request.FILES or None)
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user.trader
            shop.create_date = datetime.datetime.now()
            shop.logo = request.FILES['logo']
            file_type = shop.logo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'shop': shop,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                    'shop0':shop0
                }
                return render(request, 'boutique1/create_shop.html', context)
            shop.save()
            return render(request, 'boutique1/shop_details.html', {'shop': shop, 'shop0':shop0})
        context = {
            "form": form,
            'shop0':shop0,
        }
        return render(request, 'boutique1/create_shop.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def create_product(request, shop_id):
    form = ProductForm(request.POST or None, request.FILES or None)
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    shop = get_object_or_404(Shop, pk=shop_id)
    form_img_one = PictureForm(request.POST or None, request.FILES or None, prefix='img1')
    form_img_two = PictureForm(request.POST or None, request.FILES or None, prefix='img2')
    form_img_three = PictureForm(request.POST or None, request.FILES or None, prefix='img3')
    if form.is_valid():
        shops_products = shop.product_set.all()
        for s in shops_products:
            if s.name == form.cleaned_data.get("name"):
                context = {
                    'shop': shop,
                    'form': form,
                    'error_message': 'You already added that product',
                    'shop0':shop0
                }
                return render(request, 'boutique1/create_product.html', context)
        product = form.save(commit=False)
        product.shop = shop
        product.save()

        img1 = form_img_one.save(commit=False)
        img2 = form_img_two.save(commit=False)
        img3 = form_img_three.save(commit=False)

        img1.product = product
        img2.product = product
        img3.product = product

        img1.save()
        img2.save()
        img3.save()
        return render(request, 'boutique1/shop_details.html', {'shop': shop, 'shop0':shop0})
    context = {
        'shop': shop,
        'shop0': shop0,
        'form': form,
        "form_img_one": form_img_one,
        "form_img_two": form_img_two,
        "form_img_three": form_img_three,
    }
    return render(request, 'boutique1/create_product.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def activate_product(request, shop_id, prod_id):
    prod = get_object_or_404(Product, pk=prod_id)
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    try:
        if prod.is_active:
            prod.is_active = False
        else:
            prod.is_active = True
        prod.save()
    except (KeyError, Product.DoesNotExist):
        user = request.user
        shop = get_object_or_404(Shop, pk=shop_id)
        return render(request, 'boutique1/shop_details.html', {'shop': shop, 'user': user, 'shop0' : shop0})
    else:
        user = request.user
        shop = get_object_or_404(Shop, pk=shop_id)
        return render(request, 'boutique1/shop_details.html', {'shop': shop, 'user': user, 'shop0':shop0})
#-----------------------------------------------------------------------------------------------------------------------
def duplicate_product(request, shop_id, prod_id):
    try:
        prod = Product.objects.get(id=prod_id)
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    except Product.DoesNotExist:
        prod = None
    boutique = get_object_or_404(Shop, pk=shop_id)

    intNbr = len(list(Picture.objects.filter(product=prod)))

    if intNbr == 0:
        form = ProductForm(request.POST or None, request.FILES or None, instance=prod)
        form_img_one = PictureForm(request.POST or None, request.FILES or None, instance=None, prefix='img1')
        form_img_two = PictureForm(request.POST or None, request.FILES or None, instance=None, prefix='img2')
        form_img_three = PictureForm(request.POST or None, request.FILES or None, instance=None, prefix='img3')

        if prod:

            form = ProductForm(request.POST or None, request.FILES or None, instance=prod)
            form_img_one = PictureForm(request.POST or None, request.FILES or None, instance=None,
                                       prefix='img1')
            form_img_two = PictureForm(request.POST or None, request.FILES or None, instance=None,
                                       prefix='img2')
            form_img_three = PictureForm(request.POST or None, request.FILES or None, instance=None,
                                         prefix='img3')
            if form.is_valid():
                prod = form.save(commit=False)
                prod.id = None
                prod.save()
                img1 = form_img_one.save(commit=False)
                img2 = form_img_two.save(commit=False)
                img3 = form_img_three.save(commit=False)

                img1.product = prod
                img2.product = prod
                img3.product = prod

                img1.save()
                img2.save()
                img3.save()

                return render(request, 'boutique1/shop_details.html', {'shop': boutique, 'shop0':shop0})
            context = {
                'shop': boutique,
                'shop0': shop0,
                'form': form,
                "form_img_one": form_img_one,
                "form_img_two": form_img_two,
                "form_img_three": form_img_three,
            }
            return render(request, 'boutique1/duplicate_prod.html', context)
        return render(request, 'boutique1/shop_details.html', {'shop': boutique, 'shop0':shop0})

    else:
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        picture_one_inst = list(Picture.objects.filter(product=prod))[0]
        picture_two_inst = list(Picture.objects.filter(product=prod))[1]
        picture_three_inst = list(Picture.objects.filter(product=prod))[2]

        if prod:

            form = ProductForm(request.POST or None, request.FILES or None, instance=prod)
            form_img_one = PictureForm(request.POST or None, request.FILES or None, instance=picture_one_inst,
                                       prefix='img1')
            form_img_two = PictureForm(request.POST or None, request.FILES or None, instance=picture_two_inst,
                                       prefix='img2')
            form_img_three = PictureForm(request.POST or None, request.FILES or None, instance=picture_three_inst,
                                         prefix='img3')
            if form.is_valid():
                prod = form.save(commit=False)
                prod.id = None
                prod.save()
                img1 = form_img_one.save(commit=False)
                img2 = form_img_two.save(commit=False)
                img3 = form_img_three.save(commit=False)

                img1.id = None
                img2.id = None
                img3.id = None

                img1.product = prod
                img2.product = prod
                img3.product = prod

                img1.save()
                img2.save()
                img3.save()

                return render(request, 'boutique1/shop_details.html', {'shop': boutique, 'shop0':shop0})
            context = {
                'shop': boutique,
                'shop0': shop0,
                'form': form,
                "form_img_one": form_img_one,
                "form_img_two": form_img_two,
                "form_img_three": form_img_three,
            }
            return render(request, 'boutique1/duplicate_prod.html', context)
        return render(request, 'boutique1/shop_details.html', {'shop': boutique, 'shop0':shop0})
#-----------------------------------------------------------------------------------------------------------------------
def edit_product(request, shop_id, prod_id):
    shop = get_object_or_404(Shop, pk=shop_id)
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    prod_inst = get_object_or_404(Product, id=prod_id)

    intNbr = len(list(Picture.objects.filter(product=prod_inst)))

    if intNbr == 0:
        form = ProductForm(request.POST or None, request.FILES or None, instance=prod_inst)
        form_img_one = PictureForm(request.POST or None, request.FILES or None, instance=None, prefix='img1')
        form_img_two = PictureForm(request.POST or None, request.FILES or None, instance=None, prefix='img2')
        form_img_three = PictureForm(request.POST or None, request.FILES or None, instance=None, prefix='img3')

        if form.is_valid():
            prod_inst = form.save(commit=False)
            prod_inst.save()
            img1 = form_img_one.save(commit=False)
            img2 = form_img_two.save(commit=False)
            img3 = form_img_three.save(commit=False)

            img1.product = prod_inst
            img2.product = prod_inst
            img3.product = prod_inst

            img1.save()
            img2.save()
            img3.save()
            return render(request, 'boutique1/shop_details.html', {'shop': shop, 'shop0':shop0})
        context = {
            'shop': shop,
            'shop0': shop0,
            'form': form,
        }
        return render(request, 'boutique1/edit_prod.html', context)

    else:
        picture_one_inst = list(Picture.objects.filter(product=prod_inst))[0]
        picture_two_inst = list(Picture.objects.filter(product=prod_inst))[1]
        picture_three_inst = list(Picture.objects.filter(product=prod_inst))[2]

        form = ProductForm(request.POST or None, request.FILES or None, instance=prod_inst)
        form_img_one = PictureForm(request.POST or None, request.FILES or None, instance=picture_one_inst, prefix='img1')
        form_img_two = PictureForm(request.POST or None, request.FILES or None, instance=picture_two_inst, prefix='img2')
        form_img_three = PictureForm(request.POST or None, request.FILES or None, instance=picture_three_inst,
                                     prefix='img3')

        if form.is_valid():
            prod_inst = form.save(commit=False)
            prod_inst.save()
            img1 = form_img_one.save(commit=False)
            img2 = form_img_two.save(commit=False)
            img3 = form_img_three.save(commit=False)

            img1.product = prod_inst
            img2.product = prod_inst
            img3.product = prod_inst

            img1.save()
            img2.save()
            img3.save()
            return render(request, 'boutique1/shop_details.html', {'shop': shop, 'shop0': shop0})
        context = {
            'shop': shop,
            'shop0': shop0,
            'form': form,
            "form_img_one": form_img_one,
            "form_img_two": form_img_two,
            "form_img_three": form_img_three,
        }
        return render(request, 'boutique1/edit_prod.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def edit_shop(request, shop_id):
    boutiquei = get_object_or_404(Shop, pk=shop_id)
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    form = ShopForm(request.POST or None, request.FILES or None, instance=boutiquei)
    if form.is_valid():
        boutique = form.save(commit=False)
        boutique.save()
        shops = Shop.objects.filter(owner__user=request.user)
        return render(request, 'boutique1/myShops.html', {'shops': shops,'shop0':shop0})
    context = {
        'form': form,
        'shop': boutiquei,
        'shop0': shop0
    }
    return render(request, 'boutique1/edit_shop.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def delete_shop(request, shop_id):
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    shop = Shop.objects.get(pk=shop_id)
    shop.delete()
    shops = Shop.objects.filter(owner__user=request.user)
    return render(request, 'boutique1/myShops.html', {'shops': shops, 'shop0': shop0})
#-----------------------------------------------------------------------------------------------------------------------
def delete_product(request, shop_id, product_id):
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    shop = get_object_or_404(Shop, pk=shop_id)
    product = Product.objects.get(pk=product_id)
    str(product.price)
    product.delete()
    return render(request, 'boutique1/shop_details.html', {'shop': shop, 'product': product, 'shop0':shop0})
#-----------------------------------------------------------------------------------------------------------------------
def logout_user(request):
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
        "shop0": shop0,
    }
    return render(request, 'boutique1/login.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def activate_product(request,shop_id, prod_id):
    prod = get_object_or_404(Product, pk=prod_id)
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    try:
        if prod.is_active:
            prod.is_active = False
        else:
            prod.is_active = True
        prod.save()
    except (KeyError, Product.DoesNotExist):
        user = request.user
        shop = get_object_or_404(Shop, pk=shop_id)
        return render(request, 'boutique1/shop_details.html', {'shop0': shop0, 'shop': shop, 'user': user})
    else:
        user = request.user
        shop = get_object_or_404(Shop, pk=shop_id)
        return render(request, 'boutique1/shop_details.html', {'shop0': shop0, 'shop': shop, 'user': user})
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def detail_collection(request,collection_id):
    collection = get_object_or_404(Collection, pk=collection_id)
    return render('boutique1/collection_details.html',{'collection':collection})
#-----------------------------------------------------------------------------------------------------------------------
def myCollections(request, shop_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        #shop = Shop.objects.filter(owner__user=request.user)
        shop = get_object_or_404(Shop, pk=shop_id)
        collection = Collection.objects.filter(owner__user=request.user)
        print(collection)
        return render(request, 'boutique1/my_collections.html',{'collection':collection, 'shop': shop})
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def collections(request, shop_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        shop = Shop.objects.get(id=shop_id)
        collections = Collection.objects.filter(user=request.user)
        if 'search' in request.GET:
            query = request.GET.get('search')
            query_list = re.sub("[^\w]", " ", query).split()
            q = Q()
            for word in query_list:
                q |= Q(title__icontains=word) | Q(description__icontains=word)
                collections = collections.filter(q)

        page = request.GET.get('page', 1)
        paginator = Paginator(collections, 4)
        try:
            collections = paginator.page(page)
        except PageNotAnInteger:
            collections = paginator.page(1)
        except EmptyPage:
            collections = paginator.page(paginator.num_pages)

        return render(request, 'boutique1/my_collections.html', {'shop': shop, 'collections': collections})
#-----------------------------------------------------------------------------------------------------------------------
def create_collection(request, shop_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    elif not hasattr(request.user, 'trader'):
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        form = TraderForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            trader = form.save(commit=False)
            trader.user = request.user
            trader.save()
            return render(request, 'boutique1/create_shop.html/')
        context = {
            "form_name": "You have to signup as a Trader to continue",
            "form": form,
            'shop0':shop0
        }
        return render(request, 'boutique1/form_template2.html', context)
    else:
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        owner = Trader.objects.filter(user=request.user)
        shop = get_object_or_404(Shop, owner=owner)
        products = Product.objects.filter(shop=shop)
        if shop is None:
            return redirect('/create_boutique/')
        elif products is None:
            return redirect(shop.id + 'boutique1/create_product/')
        else:
            form = CollectionForm(request.POST or None, request.FILES or None)
            form.fields['product'].queryset = products
            if form.is_valid():
                collection = form.save(commit=False)
                collection.owner = Trader.objects.get(user=request.user)
                collection.image_collection = request.FILES['image_collection']
                file_type = collection.image_collection.url.split('.')[-1]
                file_type = file_type.lower()
                if file_type not in IMAGE_FILE_TYPES:
                    context = {
                        'collection': collection,
                        'shop': shop,
                        'form': form,
                        'error_message': 'Image file must be PNG, JPG, or JPEG',
                    }
                    return render(request, 'boutique1/create_collection.html', context)

                collection.save()
                form.save_m2m()
                collections = Collection.objects.filter(owner=owner)
                #return render(request, 'boutique1/discover.html',
                              #{'collections': collections, 'boutique': boutique})
                return redirect('/shop/'+shop_id+'/mycollections/')
            context = {
                'shop': shop,
                'form': form,
                'shop0': shop0
            }
            return render(request, 'boutique1/create_collection.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def delete_collection(request, shop_id, coll_id):
    shop = Shop.objects.get(pk=shop_id)
    collection = Collection.objects.get(id=coll_id)
    collection.delete()
    collections = Collection.objects.filter(owner__user=request.user)
    return render(request, 'boutique1/my_collections.html', {'shop': shop, 'collections': collections})
#-----------------------------------------------------------------------------------------------------------------------
def edit_collection(request, shop_id, coll_id):
    shop = Shop.objects.get(pk=shop_id)
    collectioni = get_object_or_404(Collection, pk=coll_id)
    prods = Product.objects.filter(shop=shop)

    form = CollectionForm(request.POST or None, request.FILES or None, instance=collectioni)
    form.fields['product'].queryset = prods
    if form.is_valid():
        collection = form.save(commit=False)
        product = form.cleaned_data['product']
        collection.product = product
        collection.save()
        collections = Collection.objects.filter(owner__user=request.user)
        return redirect('/shop/' + shop_id + '/mycollections/', {'shop': shop, 'collections': collections})
    context = {
        'collection' : collectioni,
        "shop": shop,
        'form': form,
    }
    return render(request, 'boutique1/edit_collection.html', context)
    #return redirect('/shop/'+shop_id+'/mycollections/')
#-----------------------------------------------------------------------------------------------------------------------
def collection_detail(request, shop_id, coll_id):
    user = request.user
    shop = get_object_or_404(Shop, pk=shop_id)
    collection = Collection.objects.get(id = coll_id)
    prods = collection.product.all()

    page = request.GET.get('page', 1)
    paginator = Paginator(prods, 4)
    try:
        prods = paginator.page(page)
    except PageNotAnInteger:
        prods = paginator.page(1)
    except EmptyPage:
        prods = paginator.page(paginator.num_pages)

    return render(request, 'boutique1/collection_details.html', {'shop': shop,'collection': collection, 'prods': prods})
#-----------------------------------------------------------------------------------------------------------------------
def activate_collection(request,shop_id, coll_id):
    collection = get_object_or_404(Collection, pk=coll_id)
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    try:
        if collection.is_active:
            collection.is_active = False
        else:
            collection.is_active = True
        collection.save()
    except (KeyError, Product.DoesNotExist):
        user = request.user
        shop = get_object_or_404(Shop, pk=shop_id)
        return render(request, 'boutique1/my_collections.html', {'shop0': shop0, 'shop': shop, 'user': user})
    else:
        user = request.user
        shop = get_object_or_404(Shop, pk=shop_id)
        #return render(request, 'boutique1/my_collections.html', {'shop0': shop0, 'shop': shop, 'user': user})
        return redirect('/shop/'+shop_id+'/mycollections/')
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def promotions(request, shop_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        shop = Shop.objects.get(id=shop_id)
        promotions = Promotion.objects.filter(shop=shop)
        if 'search' in request.GET:
            query = request.GET.get('search')
            query_list = re.sub("[^\w]", " ", query).split()
            q = Q()
            for word in query_list:
                q |= Q(title__icontains=word)
                promotions = promotions.filter(q)

        page = request.GET.get('page', 1)
        paginator = Paginator(promotions, 4)
        try:
            promotions = paginator.page(page)
        except PageNotAnInteger:
            promotions = paginator.page(1)
        except EmptyPage:
            promotions = paginator.page(paginator.num_pages)

        return render(request, 'boutique1/promotions.html', {'shop': shop, 'promotions': promotions})
#-----------------------------------------------------------------------------------------------------------------------
def create_promotion(request, shop_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:

        # product = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Product.objects.all())
        form = PromotionForm(request.POST or None, request.FILES or None)
        shop = Shop.objects.get(id=shop_id)
        # prods = Product.objects.filter(boutique=shop)
        # form.fields['product'].queryset = prods
        if form.is_valid():
            timezone = request.POST.get('tz')
            # form.product = Product.objects.filter(boutique__owner__user=request.user)
            promotion = form.save(commit=False)
            promotion.shop = shop
            promotion.save()
            start_time = promotion.start_time + timedelta(minutes=int(timezone))
            end_time = promotion.end_time + timedelta(minutes=int(timezone))
            activate.apply_async((promotion.id, promotion.product_id), eta=start_time)
            desactivate.apply_async((promotion.id, promotion.product_id), eta=end_time)
            print(start_time)
            print(end_time)
            # product = form.cleaned_data['product']
            # collection.product = product
            # collection.save()

            promotions = Promotion.objects.filter(shop=shop)
            return render(request, 'boutique1/promotions.html', {'shop': shop, 'promotions': promotions})
        context = {
            "shop": shop,
            "form": form,
        }
        return render(request, 'boutique1/create_promotion.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def delete_promotion(request, shop_id, promo_id):
    shop = Shop.objects.get(pk=shop_id)
    promotion = Promotion.objects.get(id=promo_id)
    promotion.delete()
    desactivate.apply_async((promotion.id, promotion.product_id), countdown=1)
    if promotion.product:
        promotions = Promotion.objects.filter(shop=shop)
        return render(request, 'boutique1/promotions.html', {'shop': shop, 'promotions': promotions})
    else:
        promotions = Promotion.objects.filter(shop=shop)
        return render(request, 'boutique1/promotions.html', {'shop': shop, 'promotions': promotions})
#-----------------------------------------------------------------------------------------------------------------------
def edit_promotion(request, shop_id, promo_id):
    shop = Shop.objects.get(pk=shop_id)
    promotioni = get_object_or_404(Promotion, pk=promo_id)
    prods = Product.objects.filter(shop=shop)

    form = PromotionForm(request.POST or None, request.FILES or None, instance=promotioni)
    # form.fields['product'].queryset = prods
    if form.is_valid():
        timezone = request.POST.get('tz')
        promotion = form.save(commit=False)
        # product = form.cleaned_data['product']
        # collection.product = product
        promotion.save()
        start_time = promotion.start_time + timedelta(minutes=int(timezone))
        end_time = promotion.end_time + timedelta(minutes=int(timezone))
        activate.apply_async((promotion.id, promotion.product_id), eta=start_time)
        desactivate.apply_async((promotion.id, promotion.product_id), eta=end_time)
        promotions = Promotion.objects.filter(shop__owner__user=request.user)
        return render(request, 'boutique1/promotions.html', {'shop': shop, 'promotions': promotions})
    context = {
        "shop": shop,
        'form': form,
    }
    return render(request, 'boutique1/edit_promotion.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def promotion_detail(request, shop_id, promo_id):
    user = request.user
    shop = get_object_or_404(Shop, pk=shop_id)
    promotion = Promotion.objects.get(id = promo_id)
    prods = None
    colls = None

    try:
        prods = Product.objects.filter(promotion=promotion)
        print(prods)
        colls = Collection.objects.filter(promotion=promotion)
        print(colls)
    except Product.DoesNotExist:
        colls = Collection.objects.filter(promotion=promotion)
        print(colls)

    page = request.GET.get('page', 1)
    paginator = Paginator(prods, 4)
    try:
        prods = paginator.page(page)
    except PageNotAnInteger:
        prods = paginator.page(1)
    except EmptyPage:
        prods = paginator.page(paginator.num_pages)

    return render(request, 'boutique1/promotion_detail.html', {'shop': shop,'promotion': promotion, 'prods': prods, 'colls': colls})
#-----------------------------------------------------------------------------------------------------------------------
class ProductCreateAPIView(CreateAPIView):
    queryset = Product.objects.all()

    serializer_class = ProductCreateUpdateSerializer

    def perform_create(self, serializer):
        user = self.request.user

        buser = user.buser

        shops = Shop.objects.filter(owner=buser.id)

        serializer.save(shop=shops[0])
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def create_album(request, shop_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        owner = Trader.objects.filter(user=request.user)
        #album = get_object_or_404(Album, owner=owner)
        shop = get_object_or_404(Shop, pk=shop_id)
        form = AlbumForm(request.POST or None, request.FILES or None)
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        if form.is_valid():
            album = form.save(commit=False)
            album.owner = request.user.trader
            album.album_image = request.FILES['album_image']
            file_type = album.album_image.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                    'shop0': shop0,
                    'shop': shop
                }
                return render(request, 'boutique1/create_album.html', context)
            album.save()
            #return render(request, 'boutique1/allAlbums.html/', {'album': album, 'shop0': shop0, 'shop': shop})
            return redirect('/shop/' + shop_id + '/all_albums/')
        context = {
            "form": form,
            'shop0': shop0,
            'shop': shop
        }
        return render(request, 'boutique1/create_album.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def edit_album(request, shop_id, album_id):
    shop = get_object_or_404(Shop, pk=shop_id)
    shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
    album_inst = get_object_or_404(Album, id=album_id)

    form = AlbumForm(request.POST or None, request.FILES or None, instance=album_inst)

    if form.is_valid():
        album_inst = form.save(commit=False)
        album_inst.save()
        return redirect('/shop/'+shop_id+'/all_albums/')
    context = {
        'shop': shop,
        'shop0': shop0,
        'form': form,
    }
    return render(request, 'boutique1/edit_album.html', context)
#-----------------------------------------------------------------------------------------------------------------------
def allAlbums(request, shop_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        shop = get_object_or_404(Shop, pk=shop_id)
        album = Album.objects.filter(owner__user__id=request.user.id)
        albums = Album.objects.filter(owner__user__id=request.user.id)
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        return render(request, 'boutique1/allAlbums.html', {'shop': shop, 'shop0':shop0, 'album': album, 'albums': albums})
#-----------------------------------------------------------------------------------------------------------------------
def delete_album(request, shop_id, album_id):
    shop = Shop.objects.get(pk=shop_id)
    album = Album.objects.get(id=album_id)
    album.delete()
    albums = Album.objects.filter(owner__user=request.user)
    context = {
        'shop': shop,
        'albums': albums
    }
    #return render(request, 'boutique1/my_collections.html', {'shop': shop, 'albums': albums})
    return redirect('/shop/' + shop_id + '/all_albums/')
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def albumDetails(request, shop_id, album_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        shop = get_object_or_404(Shop, pk=shop_id)
        album = get_object_or_404(Album, pk=album_id)
        pics = Pic.objects.filter(album = album)
        user = shop.owner.user
        return render(request, 'boutique1/album_details.html', {'pics': pics, 'shop': shop, 'album': album, 'user': user,  'shop0': shop0})
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def add_pic(request, shop_id, album_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        owner = Trader.objects.filter(user=request.user)
        album = get_object_or_404(Album, pk=album_id)
        shop = get_object_or_404(Shop, pk=shop_id)
        form = PicForm(request.POST or None, request.FILES or None)
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        if form.is_valid():
            pic = form.save(commit=False)
            pic.owner = request.user.trader
            pic.album = album
            pic.image = request.FILES['image']
            file_type = pic.image.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'album': album,
                    'pic': pic,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                    'shop0': shop0,
                    'shop': shop
                }
                return render(request, 'boutique1/add_pic.html', context)
            pic.save()
            #return render(request, 'boutique1/allAlbums.html/', {'album': album, 'shop0': shop0, 'shop': shop})
            return redirect('/shop/' + shop_id + '/album/details/'+album_id+'/')
        context = {
            'album': album,
            "form": form,
            'shop0': shop0,
            'shop': shop
        }
        return render(request, 'boutique1/add_pic.html', context)
# -----------------------------------------------------------------------------------------------------------------------
def delete_pic(request, shop_id, album_id, pic_id):
    shop = Shop.objects.get(pk=shop_id)
    #album = Album.objects.get(pk=album_id)
    pic = get_object_or_404(Pic, pk=pic_id)
    pic.delete()
    #pics = Pic.objects.filter(album=album)
    context = {
        'shop': shop,
        #'pics': pics,
        'pic': pic,
        #'album': album,
    }
    # return render(request, 'boutique1/my_collections.html', {'shop': shop, 'albums': albums})
    return redirect('/shop/' + shop_id + '/album/details/'+album_id)
# -----------------------------------------------------------------------------------------------------------------------
def albumDetails(request, shop_id, album_id):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        shop0 = len(list(Shop.objects.filter(owner__user__id=request.user.id)))
        shop = get_object_or_404(Shop, pk=shop_id)
        album = get_object_or_404(Album, pk=album_id)
        pics = Pic.objects.filter(album = album)
        user = shop.owner.user
        return render(request, 'boutique1/album_details.html', {'pics': pics, 'shop': shop, 'album': album, 'user': user,  'shop0': shop0})
#-----------------------------------------------------------------------------------------------------------------------




def create_wish_category(request):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        form = AlbumForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('/discoverProd/')
        context = {
            "form": form,
        }
        return render(request, 'create_wishcategory.html', context)


def my_categorys(request):
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    else:
        categorys=wish_category.objects.filter(user=request.user)
        # PAGINATION
        page = request.GET.get('page', 1)
        paginator = Paginator(categorys, 6)
        try:
            categorys = paginator.page(page)
        except PageNotAnInteger:
            categorys = paginator.page(1)
        except EmptyPage:
            categorys = paginator.page(paginator.num_pages)
        return render(request,'my_wishcategorys.html',{'categorys':categorys})

def delete_category(request, category_id):
    category = wish_category.objects.get(pk=category_id)
    category.delete()
    categorys=wish_category.objects.filter(user=request.user)
    return render(request, 'my_wishcategorys.html',{'categorys':categorys})

def edit_category(request, category_id):
    categoryi = get_object_or_404(wish_category, pk=category_id)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=categoryi)
    if form.is_valid():
        category = form.save(commit=False)
        category.save()

        return redirect('/wish/my_categorys/')
    context = {
        'form': form,
        'category': categoryi
    }
    return render(request, 'boutique1/create_boutique.html', context)


def addprod(request,category_id,prod_id):
    ws=wish_category.objects.all()
    category=get_object_or_404(wish_category,pk=category_id)
    prod=get_object_or_404(Product,pk=prod_id)
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    elif not ws:
        redirect('/wish/create_wishcategory/')
    else:
        try:
            wishlist=wish_list()
            wishlist.user = request.user
            wishlist.produit=prod
            wishlist.wish_category=category
            wishlist.save()
          #  return redirect('/discoverProd/')
        except Exception as e:
            msg=e
        return redirect('/wish/categoryProds/'+str(category_id))

def detailcategory(request, category_id):
    category = get_object_or_404(wish_category, pk=category_id)
    produit = wish_list.objects.filter(wish_category=category).values_list('produit_id')
    pro=Product.objects.filter(pk__in=produit)

    # PAGINATION
    page = request.GET.get('page', 1)
    paginator = Paginator(pro, 6)
    try:
        pro = paginator.page(page)
    except PageNotAnInteger:
        pro = paginator.page(1)
    except EmptyPage:
        pro = paginator.page(paginator.num_pages)

    return render(request,  'discover_wishlist.html', {'category': category,'products': pro})

def delete_category_produit(request,category_id,produit_id):
    produit=wish_list.objects.filter(user=request.user)
    q = Q(wish_category_id=category_id) & Q(produit_id=produit_id)
    product = produit.filter(q)
    product.delete()
    return redirect('/wish/categoryProds/' + str(category_id))



def create_wish_list(request,category_id):
    ws=wish_category.objects.all()
    category=get_object_or_404(wish_category,pk=category_id)
    if not request.user.is_authenticated():
        return render(request, 'boutique1/login.html')
    elif not ws:
        redirect('/wish/create_wishcategory/')
    else:
        form = WishlistForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            wishlist = form.save(commit=False)
            wishlist.user = request.user
            wishlist.save()
          #  return redirect('/discoverProds/')
        context = {
            "form": form,
            "category":category,
        }

        return render(request,'add_to_wishlist.html',context)