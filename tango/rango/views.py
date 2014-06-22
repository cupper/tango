from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import *
from rango.forms import *

def name_to_url(name):
    return name.replace(' ', '_')


def url_to_name(url):
    if not url:
        return None
    return url.replace('_', ' ')


def index(request):
    categories = Category.objects.order_by('-likes')[:5]
    for c in categories:
        c.url = name_to_url(c.name)

    pages = Page.objects.order_by('-views')[:5]
    return render(request, 'rango/index.html', {'categories': categories,
     'pages': pages})


def about(request):
    return render(request, 'rango/about.html')


def category(request, category_name_url):
    category_name = url_to_name(category_name_url)
    pages = None
    category = None
    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
    except Category.DoesNotExist:
        pass

    return render(request, 'rango/category.html', {'category_name_url': category_name_url,
     'category_name': category_name,
     'category': category,
     'pages': pages})


@login_required
def add_category(request, category_name_url = None):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request)
        print form.errors
    else:
        form = CategoryForm(initial={'name': url_to_name(category_name_url)})
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_url):
    category_name = url_to_name(category_name_url)
    form = None
    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            try:
                cat = Category.objects.get(name=category_name)
                page.category = cat
            except Category.DoesNotExist:
                return render(request, 'rango/add_category.html')

            page.views = 0
            page.save()
            return redirect('category', category_name_url=category_name_url)
        print form.errors
    else:
        form = PageForm()
    return render(request, 'rango/add_page.html', {'category_name_url': category_name_url,
     'category_name': category_name,
     'form': form})


def register(request):
    registered = False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    return render(request, 'rango/register.html', {'user_form': user_form,
     'profile_form': profile_form,
     'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect('index')
            else:
                return HttpReponse('Your Rango account is disabled')
        else:
            print 'Invalid login details: {0}, {1}'.format(username, password)
            return HttpResponse('Invalid login details supplied')
    else:
        return render(request, 'rango/login.html', {})


@login_required
def user_logout(request):
    logout(request)
    return redirect('index')

