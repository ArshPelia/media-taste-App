# Create your views here.
import json
import requests
import sys

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from .models import User, Question, Note, Progress

from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import QuestionSerializer, NoteSerializer

from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
# Load environment variables from file
from dotenv import load_dotenv

# Create your views here.

""" 
as long as the user is signed in, this function renders the mainapp/inbox.html template

"""


def index(request):

    # Authenticated users view their inbox
    if request.user.is_authenticated:
        return render(request, "mainapp/index.html")

    # Everyone else is prompted to sign in
    else:
        return HttpResponseRedirect(reverse("login"))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "mainapp/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "mainapp/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "mainapp/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(email, email, password)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "mainapp/register.html", {
                "message": "Email address already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "mainapp/register.html")
