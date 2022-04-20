from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.db.models import Min

from shop_app.models import Category, Product
from shop_app.cart import Cart
from shop_app.forms import CartAddProductForm
from shop_app.utils import handle_error, check_integer

from shop_app import error_messages


def index(request):
    categories = Category.objects.annotate(min_price=Min('products__price'))
    return render(request, 'shop_app/index.html', context={'categories': categories})


def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    cat_id, price_ord = request.GET.get('cat'), request.GET.get('price_ord', 'ASC')

    if cat_id is not None:
        if not check_integer(cat_id):
            return handle_error(request, error_messages.NOT_INT_CAT_ID.format(cat_id), 400)
        else:
            get_object_or_404(Category, id=cat_id)

    if cat_id:
        products = products.filter(category=cat_id)

    if price_ord == 'ASC':
        products = products.order_by('price')
    elif price_ord == 'DESC':
        products = products.order_by('-price')
    else:
        return handle_error(request, error_messages.WRONG_ORDER_PARAM.format(price_ord), 400)


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
        return redirect('home')

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
