from django.shortcuts import render, redirect, get_object_or_404

from .forms import ProductForm
from .models import Product


def home(request):
    return render(request, 'home.html')


def product_list(request):
    products = Product.objects.order_by('-created_at')
    return render(request, 'product_list.html', {'products': products})


def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            return redirect('demo_app:product_detail', pk=product.pk)
    else:
        form = ProductForm()

    return render(request, 'product_form.html', {'form': form})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})