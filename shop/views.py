from django.shortcuts import render
from django.views.generic import ListView

from shop.models import Product
from shop.scraping import scraping, ScrapingError


def fill_database(request):
    if request.method == 'POST' and request.user.is_staff:
        try:
            scraping()
        except ScrapingError as err:
            print(str(err))
            return render(request, 'shop/fill-database.html', {'message': str(err)})
    return render(request, 'shop/fill-database.html', {'message': None})


class ProductsListView(ListView):
    model = Product
    template_name = 'shop/products.html'
