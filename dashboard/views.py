from django.shortcuts import render, redirect
from . forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    return render(request,'dashboard/home.html')

@login_required
def notes(request):
    if request.method == "POST":
        form = NotesFrom(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user,title=request.POST['title'],description=request.POST['description'])
            notes.save()
        messages.success(request,f"Notes Added from {request.user.username} Successfully!")
    else:    
        form = NotesFrom()
    notes = Notes.objects.filter(user=request.user)
    context = {'notes':notes,'form':form}
    return render(request,'dashboard/notes.html',context)

@login_required
def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")


class NotesDetailView(generic.DetailView):
    model = Notes

@login_required    
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            homeworks = Homework(
                user = request.user,
                subject = request.POST['subject'],
                title = request.POST['title'],
                description = request.POST['description'],
                due = request.POST['due'],
                is_finished = finished
            )
        homeworks.save()
        messages.success(request,f'Homework Added from {request.user.username} !!!')
    else:
        form = HomeworkForm()
    homework = Homework.objects.filter(user=request.user)
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
        
    context = {
            'homeworks':homework,
            'homeworks_done':homework_done,
            'form':form,
    }
    return render(request,'dashboard/homework.html',context)


@login_required
def update_homework(request,pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')

@login_required
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")
    
    
def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['result']:
            result_dist = {
                'input':text,
                'title':i['title'],
                'duration':i['duration'],
                'thumbnails':i['thumbnails'][0]['url'],
                'channel':i['channel']['name'],
                'link':i['link'],
                'views':i['viewCount']['short'],
                'published':i['publishedTime']
            }
            desc = ''
            if i['descriptionSnippet']:
                for j in i['descriptionSnippet']:
                    desc += j['text']
            result_dist['description'] = desc
            result_list.append(result_dist)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/youtube.html',context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request,'dashboard/youtube.html',context)  

@login_required
def todo(request):
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST["is_finished"]
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False
            todos = Todo(
                user = request.user,
                title = request.POST['title'],
                is_finished = finished
            )
            todos.save()
            messages.success(request,f"Todo Added from {request.user.username}!!!")
    else:
        form = TodoForm()
    todo = Todo.objects.filter(user=request.user)
    if len(todo) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'form':form,
        'todos':todo,
        'todos_done':todos_done
    }
    return render(request,'dashboard/todo.html',context)

@login_required
def update_todo(request,pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')

@login_required
def delete_todo(request,pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect("todo")


def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q="+text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):
            result_dist = {
                'title':answer['items'][i]['volumeInfo']['title'],
                'subtitle':answer['items'][i]['volumeInfo'].get('subtitle'),
                'description':answer['items'][i]['volumeInfo'].get('description'),
                'count':answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories':answer['items'][i]['volumeInfo'].get('categories'),
                'rating':answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail': answer['items'][i]['volumeInfo'].get('imageLinks', {}).get('thumbnail'),
                'preview':answer['items'][i]['volumeInfo'].get('previewLink')
                
            }
            result_list.append(result_dist)
            context={
                'form':form,
                'results':result_list
            }
        return render(request,'dashboard/books.html',context)
    else:
        form = DashboardForm()
    context = {'form':form}
    return render(request,'dashboard/books.html',context) 


def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"+text
        r = requests.get(url)
        answer = r.json()
        try:
            phonetics = answer[0]['phonetics'][0]['text']
            audio = answer[0]['phonetics'][0]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            context = {
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio':audio,
                'definition':definition,
                'example':example,
                'synonyms':synonyms
            }
        except:
            context = {
                'form':form,
                'input':'',
                
            }
        return render(request,"dashboard/dictionary.html",context)
    else:                
        form = DashboardForm()
        context = {'form':form}
    return render(request,'dashboard/dictionary.html',context)


def wiki(request):
    if request.method == 'POST':
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary
        }
        return render(request,'dashboard/wiki.html',context)
    else:
        form = DashboardForm()
        context = {
            'form':form
        }
    return render(request,'dashboard/wiki.html',context)

def conversion(request):
    if request.method == "POST":
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = ConversionLengthForm()
            context = {
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']  
                second = request.POST['measure2']  
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'yard' and second == 'feet':
                        answer = f'{input} yard = {int(input)*3} feet'
                    if first == 'yard' and second == 'meter':
                        answer = f'{input} yard = {int(input)/1.094} meter'
                    if first == 'yard' and second == 'centimeter':
                        answer = f'{input} yard = {int(input)*91.44} centimeter'
                    if first == 'yard' and second == 'kilometer':
                        answer = f'{input} yard = {int(input)/1094} kilometer'
                    if first == 'yard' and second == 'millimeter':
                        answer = f'{input} yard = {int(input)*914.4} millimeter'
                    if first == 'yard' and second == 'mile':
                        answer = f'{input} yard = {int(input)/1760} mile'
                      
                        
                    if first == 'feet' and second == 'yard':
                        answer = f'{input} feet = {int(input)/3} yard'
                    if first == 'feet' and second == 'meter':
                        answer = f'{input} feet = {int(input)/3.281} meter'
                    if first == 'feet' and second == 'centimeter':
                        answer = f'{input} feet = {int(input)*30.48} centimeter'
                    if first == 'feet' and second == 'kilometer':
                        answer = f'{input} feet = {int(input)/3281} kilometer'
                    if first == 'feet' and second == 'millimeter':
                        answer = f'{input} feet = {int(input)*304.8} millimeter'
                    if first == 'feet' and second == 'mile':
                        answer = f'{input} feet = {int(input)/5280} mile'
                        
                    
                    if first == 'meter' and second == 'yard':
                        answer = f'{input} meter = {int(input)*1.094} yard'
                    if first == 'meter' and second == 'feet':
                        answer = f'{input} meter = {int(input)*3.281} feet'
                    if first == 'meter' and second == 'centimeter':
                        answer = f'{input} meter = {int(input)*100} centimeter'
                    if first == 'meter' and second == 'kilometer':
                        answer = f'{input} meter = {int(input)/1000} kilometer'
                    if first == 'meter' and second == 'millimeter':
                        answer = f'{input} meter = {int(input)*1000} millimeter'
                    if first == 'meter' and second == 'mile':
                        answer = f'{input} meter = {int(input)/1609} mile'
                        
                        
                    if first == 'centimeter' and second == 'yard':
                        answer = f'{input} centimeter = {int(input)/91.44} yard'
                    if first == 'centimeter' and second == 'feet':
                        answer = f'{input} centimeter = {int(input)/30.48} feet'
                    if first == 'centimeter' and second == 'meter':
                        answer = f'{input} centimeter = {int(input)/100} meter'
                    if first == 'centimeter' and second == 'kilometer':
                        answer = f'{input} centimeter = {int(input)/100000} kilometer'
                    if first == 'centimeter' and second == 'millimeter':
                        answer = f'{input} centimeter = {int(input)*10} millimeter'
                    if first == 'centimeter' and second == 'mile':
                        answer = f'{input} centimeter = {int(input)/160900} mile'
                        
                        
                    if first == 'kilometer' and second == 'yard':
                        answer = f'{input} kilometer = {int(input)*1094} yard'
                    if first == 'kilometer' and second == 'feet':
                        answer = f'{input} kilometer = {int(input)*3281} feet'
                    if first == 'kilometer' and second == 'centimeter':
                        answer = f'{input} kilometer = {int(input)*100000} centimeter'
                    if first == 'kilometer' and second == 'meter':
                        answer = f'{input} kilometer = {int(input)*1000} meter'
                    if first == 'kilometer' and second == 'millimeter':
                        answer = f'{input} kilometer = {int(input)*1000000} millimeter'
                    if first == 'kilometer' and second == 'mile':
                        answer = f'{input} kilometer = {int(input)/1.609} mile'
                        
                        
                    if first == 'millimeter' and second == 'yard':
                        answer = f'{input} millimeter = {int(input)/914.4} yard'
                    if first == 'millimeter' and second == 'feet':
                        answer = f'{input} millimeter = {int(input)/304.8} feet'
                    if first == 'millimeter' and second == 'centimeter':
                        answer = f'{input} millimeter = {int(input)/10} centimeter'
                    if first == 'millimeter' and second == 'meter':
                        answer = f'{input} millimeter = {int(input)/1000} meter'
                    if first == 'millimeter' and second == 'kilometer':
                        answer = f'{input} millimeter = {int(input)/1000000} kilometer'
                    if first == 'millimeter' and second == 'mile':
                        answer = f'{input} millimeter = {int(input)/1609344} mile'
                        
                    if first == 'mile' and second == 'yard':
                        answer = f'{input} mile = {int(input)*1760} yard'
                    if first == 'mile' and second == 'feet':
                        answer = f'{input} mile = {int(input)*5280} feet'
                    if first == 'mile' and second == 'centimeter':
                        answer = f'{input} mile = {int(input)*160900} centimeter'
                    if first == 'mile' and second == 'meter':
                        answer = f'{input} mile = {int(input)*1609} meter'
                    if first == 'mile' and second == 'kilometer':
                        answer = f'{input} mile = {int(input)*1.609} kilometer'
                    if first == 'mile' and second == 'millimeter':
                        answer = f'{input} mile = {int(input)*1609344} millimeter'
                    
                        
                context = {
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                    
                }
        if request.POST['measurement'] == 'mass':
            measurement_form = ConversionMassForm()
            context = {
                'form':form,
                'm_form':measurement_form,
                'input':True
            }
            if 'input' in request.POST:
                first = request.POST['measure1']  
                second = request.POST['measure2']  
                input = request.POST['input']
                answer = ''
                if input and int(input) >= 0:
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if first == 'pound' and second == 'milligram':
                        answer = f'{input} pound = {int(input)*453592} milligram'
                    if first == 'pound' and second == 'gram':
                        answer = f'{input} pound = {int(input)*453.6} gram'
                    if first == 'pound' and second == 'ton':
                        answer = f'{input} pound = {int(input)/2000} ton'
                        
                        
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input)*2.20462} pound'
                    if first == 'kilogram' and second == 'milligram':
                        answer = f'{input} kilogram = {int(input)*1000000} milligram'
                    if first == 'kilogram' and second == 'gram':
                        answer = f'{input} kilogram = {int(input)*1000} gram'
                    if first == 'kilogram' and second == 'ton':
                        answer = f'{input} kilogram = {int(input)/907.2} ton'
                        
                        
                    if first == 'milligram' and second == 'pound':
                        answer = f'{input} milligram = {int(input)/453600} pound'  
                    if first == 'milligram' and second == 'kilogram':
                        answer = f'{input} milligram = {int(input)/1000000} kilogram' 
                    if first == 'milligram' and second == 'gram':
                        answer = f'{input} milligram = {int(input)/1000} gram'
                    if first == 'milligram' and second == 'ton':
                        answer = f'{input} milligram = {int(input)*1000000000} ton' 
                        
                        
                    if first == 'gram' and second == 'pound':
                        answer = f'{input} gram = {int(input)/453.6} pound'  
                    if first == 'gram' and second == 'kilogram':
                        answer = f'{input} gram = {int(input)/1000} kilogram' 
                    if first == 'gram' and second == 'milligram':
                        answer = f'{input} gram = {int(input)*1000} milligram' 
                    if first == 'gram' and second == 'ton':
                        answer = f'{input} gram = {int(input)*1000000} ton' 
                        
                    if first == 'ton' and second == 'pound':
                        answer = f'{input} ton = {int(input)*2000} pound'  
                    if first == 'ton' and second == 'kilogram':
                        answer = f'{input} ton = {int(input)*907.2} kilogram' 
                    if first == 'ton' and second == 'milligram':
                        answer = f'{input} ton = {int(input)/1000000000} milligram' 
                    if first == 'ton' and second == 'gram':
                        answer = f'{input} ton = {int(input)/1000000} gram' 
                    
                        
                context = {
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                    
                }
                    
    else:
        form = ConversionForm()
        context = {
            'form':form,
            'input':False
        }
    return render(request,'dashboard/conversion.html',context)



def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f"Account Created for {username}!!!")
            return redirect("login")
    else:
        form = UserRegistrationForm()
    context = {
        'form':form
    }
    return render(request,"dashboard/register.html",context)

@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False,user=request.user)
    todos = Todo.objects.filter(is_finished=False,user=request.user)
    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False
    if len(todos) == 0:
        todos_done = True
    else:
        todos_done = False
    context = {
        'homeworks' : homeworks,
        'todos' : todos,
        'homework_done' : homework_done,
        'todos_done' : todos_done
    }
    
    return render(request,"dashboard/profile.html",context)


def news(request):
    url = "https://newsapi.org/v2/top-headlines?country=in&apiKey=27547a35e54b4430a8148d0c5d554f47"
    
    top_news_headlines = requests.get(url).json()
    
    articles = top_news_headlines.get('articles', [])  # Corrected the key to 'articles'
    desc = []
    title = []
    img = []
    
    for article in articles:
        title.append(article.get('title', ''))
        desc.append(article.get('description', ''))
        img.append(article.get('urlToImage', ''))
        
    mylist = zip(title, desc, img)
    context = {'mylist': mylist}
    
    return render(request, 'dashboard/news.html', context)

        
    


