from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db import DatabaseError, IntegrityError
from django.views.decorators.csrf import csrf_exempt
import json


def login_page(request):
    return render(request, 'login.html')


def check_login(request):
    username = request.POST['user']
    password = request.POST['password']

    user = authenticate(username=username, password=password)
    if user is None:
        ret = "/identity/?error=Authentication Failed!"
        if 'next' in request.POST:
            ret = ret + "&next=" + request.POST.get('next')
        return redirect(ret)
    else:
        login(request, user)

    if 'next' in request.POST:
        return redirect(request.POST.get('next'))
    else:
        return redirect("/")


@csrf_exempt
def subscribe(request):
    context_data = {}

    if request.method == 'POST':
        body = json.loads(request.body)
        if True:
            try:
                user = User.objects.create_user(body['email'], body['email'], 'password')
                user = authenticate(request, username=body['email'], password='password')
                if user is not None:
                    # login(request, user)
                    # Redirect to a success page.
                    # context_data = {"success": "Account created! It's great if we know how to address you!<br>"
                    #                          + " You can update profile later and continue to use app from menu."}
                    return JsonResponse({"success": True}, safe=False)
                else:
                    context_data = {"error": "Error Creating Account"}
            except IntegrityError:
                context_data = {"error": "This email already exists. Try login or resetting password if you forgot."}
            except DatabaseError:
                context_data = {"error": "Something Wrong! Database didn't like it."}
        else:
            context_data = {"error": "Invalid values provided"}

    return JsonResponse(context_data, safe=False)


def logout_view(request):
    logout(request)
    return redirect("/")


@csrf_exempt
def user_entry(request):

    response = {'error': True, 'message': 'unknown_error'}

    if request.method == 'POST':
        bd = json.loads(request.body)
        if 'email' in bd and 'password' in bd:
            username = bd['email']
            password = bd['password']
            user = authenticate(username=username, password=password)
            if user is None:
                if User.objects.filter(email=username).exists():
                    response['error'] = True
                    response['message'] = 'incorrect_password'
                else:
                    user = User.objects.create_user(username, username, password)
                    user = authenticate(request, username=username, password=password)
                    if user is None:
                        response['error'] = True
                        response['message'] = 'error_create_user'
                    else:
                        login(request, user)
                        response['error'] = False
                        response['message'] = 'new_user_created'
            else:
                login(request, user)
                response['error'] = False
                response['message'] = 'success'
        else:
            response['error'] = True
            response['message'] = 'invalid_request'
    else:
        response['error'] = True
        response['message'] = 'invalid_request'

    return JsonResponse(response, safe=False)
