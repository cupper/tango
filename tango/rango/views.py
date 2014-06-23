from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.http import is_safe_url
from datetime import datetime
from rango.models import *
from rango.forms import *
from rango.bing_search import run_query

def name_to_url(name):
    return name.replace(' ', '_')


def url_to_name(url):
    if not url:
        return None
    return url.replace('_', ' ')

# Decorator for count visits
def visit_counter(f):

    def wrapper(*args, **kw):
        request = args[0]
        if request.session.get('last_visit'):
            last_visit = request.session.get('last_visit')
            visits = request.session.get('visits', 0)

            last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
            if (datetime.now() - last_visit_time).seconds > 5:
                request.session['visits'] = visits+1
                request.session['last_visit'] = str(datetime.now())
        else:
            request.session['visits'] = 0
            request.session['last_visit'] = str(datetime.now())

        return f(*args, **kw)

    return wrapper

def get_category_list():
    categories = Category.objects.order_by('-likes')[:5]
    for c in categories:
        c.url = name_to_url(c.name)
    return categories

def search(query_str):
    result_list = []
    query = query_str.strip()
    if query:
        result_list = run_query(query)
    return result_list


@visit_counter
def index(request):
    categories = get_category_list()
    pages = Page.objects.order_by('-views')[:5]

    return render(request, 'rango/index.html',
        {'categories': categories, 'pages': pages})

@visit_counter
def about(request):
    visits = request.session.get('visits', 0)
    return render(request, 'rango/about.html', {'visits': visits})

@visit_counter
def category(request, category_name_url):
    categories = get_category_list()
    category_name = url_to_name(category_name_url)
    pages = None
    category = None
    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
    except Category.DoesNotExist:
        pass

    result_list = []
    if request.method == 'POST':
        result_list = search(request.POST['query'])

    return render(request, 'rango/category.html', {'category_name_url': category_name_url,
     'category_name': category_name,
     'category': category,
     'pages': pages,
     'categories': categories,
     'result_list': result_list })


@login_required
@visit_counter
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
@visit_counter
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


@visit_counter
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


@visit_counter
def user_login(request):
    redirect_to = request.REQUEST.get('next', 'index')
    if not is_safe_url(url=redirect_to, host=request.get_host()):
        redirect_to = ('index')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(redirect_to)
            else:
                return render(request, 'rango/login.html', {'disabled_account': 1})
        else:
            return render(request, 'rango/login.html', {'bad_details': 1})
    
    # if GET
    return render(request, 'rango/login.html', {'next': redirect_to})


@login_required
def user_logout(request):
    logout(request)
    return redirect('index')


@login_required
def profile(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'rango/profile.html', {'profile': profile})

@login_required
def track_url(request):
    redirect_to = 'index'
    if (request.method == 'GET') and ('page_id' in request.GET):
        page = Page.objects.get(id=request.GET['page_id'])
        if page:
            redirect_to = page.url
            page.views += 1
            page.save()
            
    return redirect(redirect_to)
