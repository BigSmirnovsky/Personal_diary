from django.shortcuts import render, redirect
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.contrib.auth.decorators import login_required
from django.http import Http404


def check_topic_owner(topic, request):
    """Проверка того, что тема принадлежит текущему пользователю"""
    if topic.owner != request.user:
        raise Http404

def index(request):
    """ Домашняя страница приложения Personal_diary"""
    return render(request, 'Personal_diarys/index.html')

@login_required
def topics(request):
    """Выводит список тем"""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {'topics': topics}
    return render(request, 'Personal_diarys/topics.html', context)

@login_required
def topic(request, topic_id):
    """Выводит одну тему и все её записи"""
    topic = Topic.objects.get(id=topic_id)
    # Проверка того, что тема принадлежит текущему пользователю.
    check_topic_owner(topic, request) 
    entries = topic.entry_set.order_by('-date_added')
    context = {'topic': topic, 'entries': entries}
    return render(request, 'Personal_diarys/topic.html', context)

@login_required
def new_topic(request):
    """Определяет новую тему"""
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = TopicForm()
    else:
        # Отправленные данные POST; обработать данные.
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('Personal_diarys:topics')

    # Вывести пустую или недействительную форму
    context = {'form': form}
    return render(request, 'Personal_diarys/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Добавляет новую запись по конкретной теме."""
    topic = Topic.objects.get(id=topic_id)
    if request.method != 'POST':
        # Данные не отправлялись; создается пустая форма.
        form = EntryForm()
    else:
        # Отправлены данные POST; обработать данные
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.owner = request.user
            new_entry.save()
            return redirect('Personal_diarys:topic', topic_id=topic_id)

    # Вывести пустую или недействительную форму
    context = {'topic': topic, 'form': form}
    return render(request, 'Personal_diarys/new_entry.html', context)

@login_required
def edit_entry(request, entry_id):
    """Редактирует существующую запись"""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    
    check_topic_owner(topic, request)

    if request.method != 'POST':
        # Исходный запрос; форма заполняется данными текущей записи
        form = EntryForm(instance=entry)
    else:
        # Отправка данных POST; обработать данные.
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('Personal_diarys:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'Personal_diarys/edit_entry.html', context)

@login_required
def delete_topic(request, topic_id):
    """Удаляет тему"""
    topic = Topic.objects.get(id=topic_id)
    if request.method == 'POST':
        topic.delete()
        return redirect('Personal_diarys:topics')

    return render(request, 'Personal_diarys/delete_topic.html')

@login_required
def delete_entry(request, entry_id):
    """Удаляет запись"""
    entry = Entry.objects.get(id=entry_id)
    if request.method == 'POST':
        entry.delete()
        return redirect('Personal_diarys:topics')

    return render(request, 'Personal_diarys/delete_entry.html')

#Нужно чтобы при делет ентри переходило на тему а не на все темы
