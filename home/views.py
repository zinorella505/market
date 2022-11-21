import requests
import json
import uuid

from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.db.models import Q
from userprofile.models import *
from userprofile.forms import *
from store.models import *
from store.forms import *
from . models import *
from . forms import *
# from django.http import HttpResponse

# Create your views here.
def index(request):
    category = Category.objects.all()
    context = {
        'adeyemi': category,
    }

    return render(request, 'index.html', context)
    
def contact(request):
  form = ContactForm()
  if request.method == 'POST':
    form = ContactForm(request.POST)
    if form.is_valid:
      form.save()
      messages.success(request, 'Thank you for contacting us!....')
      return redirect('index')
    else:
      messages.error(request, form.errors)
      return redirect('index')
  return redirect('index')


def categories(request):
  categories = Category.objects.all()
  # categories = Category.objects.get()
  # categories = Category.objects.filter()
  context = {
    'categories':categories,
  }
  return render(request, 'categories.html', context)

def product(request):
  product = Product.objects.all()
  context = {
    'product':product,
  }
  return render(request, 'product.html', context)

def category(request, id, slug):
  category = Product.objects.filter(category_id=id)

  context = {
    'category':category,
  }
  return render(request, 'category.html', context)

@login_required(login_url='signin') 
def details(request, id):
  details = Product.objects.get(pk=id)
  
  context = {
    'details':details,
  }
  return render(request, 'details.html', context)


def signin(request):
  if request.method == 'POST':
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username= username, password=password)
    if user is not None:
      login(request, user)
      messages.success(request, 'Welcome to Team cyber dev store!....')
      return redirect('index')
    else:
      messages.error(request, 'invalid username/password. Input correct details...')
      return redirect('signin')
  return render(request, 'signin.html')

@login_required(login_url='signin')
def signout(request):
  logout(request)
  return redirect('signin')

def signup(request):
  form = SignupForm()
  if request.method == 'POST':
    address = request.POST['address']
    state = request.POST['state']
    gender = request.POST['gender']
    nationality = request.POST['nationality']
    phone = request.POST['phone']
    pix = request.POST['pix']
    form = SignupForm(request.POST)
    if form.is_valid():
      user = form.save()
      newprofile = Profile(user=user)
      newprofile.username = user.username
      newprofile.first_name = user.first_name
      newprofile.last_name = user.last_name
      newprofile.email = user.email 
      newprofile.phone = phone
      newprofile.state = state
      newprofile.gender = gender
      newprofile.address = address
      newprofile.nationality = nationality
      newprofile.pix = pix
      newprofile.save()
      login(request, user)
      messages.success(request, f'Congratulations, {user.username}, Your Registration is successful!..........')
      return redirect('index')
    else:
      messages.error(request, form.errors)
      return redirect('signup')
  return render(request, 'signup.html')


@login_required(login_url='signin')
def profile(request):
  profile = Profile.objects.get(user__username = request.user.username)

  context = {
    'profile':profile,
  }

  return render(request, 'profile.html', context)

@login_required(login_url='signin')
def profile_update(request):
  profile = Profile.objects.get(user__username = request.user.username)
  update = ProfileUpdate(instance=request.user.profile)
  if request.method  == 'POST':
    update = ProfileUpdate(request.POST, request.FILES, instance=request.user.profile)
    if update.is_valid():
      user = update.save()
      new = user.first_name
      messages.success(request, f'Congratulations {{new}}, Your profile has been updated successfully!.....')
      return redirect('profile')
    else:
      messages.error(request, update.errors)
      return redirect('profile_update')
  context = {
    'profile':profile,
    'update':update,
  }
  return render(request, 'profile_update.html', context)

@login_required(login_url='signin')
def password(request):
  profile = Profile.objects.get(user__username = request.user.username)
  form = PasswordChangeForm(request.user)
  if request.method == 'POST':
    form = PasswordChangeForm(request.user, request.POST)
    if form.is_valid():
      user = form.save()
      update_session_auth_hash(request, user)
      messages.success(request, 'Password Change Successful!...')
      return redirect('profile')
    else:
      messages.error(request, form.errors)
      return redirect('password')
  context = {
    'form':form,
  }
  return render(request, 'password.html', context)

@login_required(login_url='signin')
def cart(request):
  if request.method == 'POST':
    quant = int(request.POST['quantity'])
    item_id = request.POST['product_id']
    product = Product.objects.get(pk=item_id)
    order_num = Profile.objects.get(user__username = request.user.username)
    cart_no = order_num.id

    cart = Cart.objects.filter(user__username = request.user.username, paid=False)
    if cart:
      basket = Cart.objects.filter(product_id = product.id,user__username = request.user.username, paid=False).first()
      if basket:
        basket.quantity += quant
        basket.amount = product.price * quant
        basket.save()
        messages.success(request, 'Product added successfully!....')
        return redirect('product')
      else:
        newitem = Cart()
        newitem.user = request.user
        newitem.price = product.price
        newitem.product = product
        newitem.order_no = cart_no
        newitem.quantity = quant
        newitem.title_g = product.title_r
        newitem.amount = product.price * quant
        newitem.paid = False
        newitem.save()
        messages.success(request, 'product added successfully!')
        return redirect('product')
    else:
      newitem = Cart()
      newitem.user = request.user
      newitem.product = product
      newitem.title_g = product.title_r
      newitem.amount = product.price * quant
      newitem.price = product.price
      newitem.order_no = cart_no
      newitem.quantity = quant
      newitem.paid = False
      newitem.save()
      messages.success(request, 'product addedd successfully!')
      return redirect('product')
  return redirect('product')

@login_required(login_url='signin')
def shopcart(request):
  profile = Profile.objects.get(user__username = request.user.username)
  trolley = Cart.objects.filter(user__username = request.user.username, paid=False)


  subtotal = 0
  vat = 0
  total = 0

  for cart in trolley:
    subtotal += cart.price * cart.quantity

  vat = 0.075 * subtotal

  total = subtotal + vat

  context = {
    'trolley':trolley,
    'profile': profile,
    'subtotal':subtotal,
    'total':total,
    'vat':vat,
  }
  return render(request, 'displaycart.html', context)

@login_required(login_url='signin')
def deleteitem(request):
  if request.method == 'POST':
    item_id = request.POST['item_id']
    item_delete = Cart.objects.get(pk=item_id)
    item_delete.delete()
    messages.success(request, 'Cart deleted successfull!......')
    return redirect('shopcart')

@login_required(login_url='signin')
def change(request):
  if request.method == 'POST':
    item_id = request.POST['item_id']
    quant = int(request.POST['quant'])
    modify = Cart.objects.get(pk=item_id)
    modify.quantity += quant
    modify.amount = modify.price * modify.quantity
    modify.save()
    messages.success(request, 'Cart modified successfully!..')
    return redirect('shopcart')


@login_required(login_url='signin')
def checkout(request):
  profile = Profile.objects.get(user__username = request.user.username)
  trolley = Cart.objects.filter(user__username = request.user.username, paid=False)


  subtotal = 0
  vat = 0
  total = 0

  for cart in trolley:
    subtotal += cart.price * cart.quantity

  vat = 0.075 * subtotal

  total = subtotal + vat

  context = {
    'trolley':trolley,
    'profile': profile,
    'total':total,
  }
  return render(request, 'checkout.html', context)


@login_required(login_url='signin')
def pay(request):
  if request.method == 'POST':
    api_key = 'sk_test_f157c3a60c75bde39b69f18fa765d8c5fce9d3c0'
    curl = 'https://api.paystack.co/transaction/initialize'
    cburl = 'http://52.206.212.86/callback/'
    # cburl = 'http://127.0.0.1:8000/callback/'
    ref = str(uuid.uuid4())
    profile = Profile.objects.get(user__username = request.user.username)
    shop_code = profile.id
    total = float(request.POST['total']) * 100
    user = User.objects.get(username=request.user.username)
    first_name = user.first_name
    last_name = user.last_name
    phone = request.POST['phone']
    headers = {'Authorization': f'Bearer {api_key}'}
    data = {'reference': ref, 'callback_url': cburl, 'email': user.email, 'amount': int(total), 'order_number': shop_code, 'currency': 'NGN'}

    try :
      r = requests.post(curl, headers= headers, json= data)
    except Exception:
      messages.error(request, 'Network busy, Try again later')
    else:
      transback = json.loads(r.text)
      rdurl = transback['data']['authorization_url']

      account = Payment()
      account.user = user
      account.first_name = user.first_name
      account.last_name = user.last_name
      account.phone = phone
      account.amount = total/100
      account.paid = True
      account.pay_code = ref
      account.shop_code = shop_code
      account.save()
      return redirect(rdurl)
  return redirect('checkout')

@login_required(login_url='signin')
def callback(request):
  profile = Profile.objects.get(user__username = request.user.username)
  trolley = Cart.objects.filter(user__username = request.user.username, paid = False)
  payment = Payment.objects.filter(user__username = request.user.username, paid = True)

  for items in trolley:
    items.paid = True
    items.save()

    stock = Product.object.get(pk = items.product_id)
    stock.max_quantity -= items.quantity
    stock.save()

  context = {
    'profile':profile,
    'trolley':trolley,
  }
  return render(request, 'callback.html', context)

@login_required(login_url='signin')
def search(request):
  if request.method == 'POST':
    items = request.POST['search']
    searched = Q(Q(title_r__icontains= items) | Q(price__icontains=items) | Q(slug__icontains=items))
    searched_items = Product.objects.filter(searched)

    context = {
      'items':items,
      'searched_items':searched_items,
    }

    return render(request, 'search.html', context)
  else:
    return render(request, 'search.html')


@login_required(login_url='signin')
def history(request):
  profile = Profile.objects.get(user__username = request.user.username)
  trolley = Cart.objects.filter(user__username = request.user.username, paid=True)


  subtotal = 0
  vat = 0
  total = 0

  for cart in trolley:
    subtotal += cart.price * cart.quantity

  vat = 0.075 * subtotal

  total = subtotal + vat

  context = {
    'trolley':trolley,
    'total':total,
    'profile': profile,
  }
  return render(request, 'history.html', context)






















  # category = Category.objects.all()
    
    # category = Category.objects.all() = query
    # query_set = Model.objects(manager).method of query
    # (i.e all, filter, exclude, get)

    # queries
    # query_set
    # objects managers
    # query methods

    
# CRUD
# C = Create (POST)
# R = Read (GET)
# U = Update (PUT, PATCH)
# D = Delete (DELETE)
