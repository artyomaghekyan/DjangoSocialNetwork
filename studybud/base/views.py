from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Room, Topic, Messages
from .forms import RoomForm, UserForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotAllowed
from django.contrib.auth.forms import UserCreationForm


# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == 'POST':
       username = request.POST.get("username").lower()
       password = request.POST.get("password")
       try:
        user = User.objects.get(username=username)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Username or password doesn't exist")
       except:
        messages.error(request, "User doesn't exist")

        
    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, 'An error occurred during registration')
    page = 'register'
    context = {'psge': page, 'form': form}
    return render(request, 'base/login_register.html', context)

def logoutPage(request):
    logout(request)

    return redirect("home")

def home(request):
    q =request.GET.get("q") if request.GET.get("q") != None else ""
    rooms = Room.objects.filter(Q(topic__name__icontains=q) |
                                Q(name__icontains=q) |
                                Q(host__username__icontains=q)
                                )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Messages.objects.filter(Q(room__topic__name__icontains=q))
    context = {"rooms": rooms, 'topics': topics,
               'room_count': room_count, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.messages_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)




def room(request, id):
    room = Room.objects.get(id=id)
    room_messages = room.messages_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        message = Messages.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", id=room.id)
    context = {"room": room, 
               'room_messages': room_messages,
               'participants': participants,
               }
    
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        
        Room.objects.create(
            host=request.user,
            topic = topic,
            name=request.POST.get("name"),
            description = request.POST.get("description")
        )
        return redirect("home")
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponseNotAllowed(["GET"])  

    if request.method == "POST":
        topic_name = request.POST.get("topic")
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get("name")
        room.topic = topic
        room.description = request.POST.get("description")
        room.save()
        return redirect("home")
    context = {"form": form, 'topics': topics, 'room': room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponseNotAllowed(["GET"])  

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj': room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Messages.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponseNotAllowed(["GET"])  

    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile', pk=user.id)
    context = {'form': form}
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q =request.GET.get("q") if request.GET.get("q") != None else ""
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Messages.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)