from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db.models import Min

from shop_app.models import Category, Product
from shop_app.cart import Cart
from shop_app.forms import CartAddProductForm
from shop_app.utils import handle_error, check_integer

from shop_app import error_messages, config


def index(request):
    categories = Category.objects.annotate(min_price=Min('products__price'))
    return render(request, 'shop_app/index.html', context={'categories': categories})


def shop(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    cat_id, price_ord, page =\
        request.GET.get('cat'), request.GET.get('price_ord'), request.GET.get('page', 1)

    if check_integer(cat_id):
        get_object_or_404(Category, id=cat_id)
        products = products.filter(category=cat_id)

    ordering_dict = {config.ASCENDING: 'price', config.DESCENDING: '-price'}
    if price_ord in ordering_dict.keys():
        products = products.order_by(ordering_dict[price_ord])

    paginator = Paginator(products, config.PAGE_SIZE)
    products = paginator.get_page(page)

    return render(request, 'shop_app/shop.html', context={'products': products, 'categories': categories})


def product_details(request, **kwargs):
    product_id = kwargs.get('product_id')
    product = get_object_or_404(Product, id=product_id)

    cart_product_form = CartAddProductForm()
    return render(request, 'shop_app/product-details.html', context={'product': product, 'cart_product_form': cart_product_form})


def cart(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 'update': True})
    return render(request, 'shop_app/cart.html', context={'cart': cart})


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if not product.available:
        return handle_error(request, error_messages.ADD_UNAVAILABLE_PRODUCT, 400)

    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 update_quantity=cd['update'])
    else:
        return handle_error(request, error_messages.WRONG_QUANTITY_COUNT, 400)
                 
    return redirect('cart')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart')
