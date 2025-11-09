from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import Http404
from .models import Topic, Entry
from .forms import TopicForm, EntryForm


def index(request):
    return render(request, 'learning_logs/index.html')


@login_required
def topics(request):
    """Show only the current user's topics."""
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    return render(request, 'learning_logs/topics.html', {'topics': topics})


@login_required
def topic(request, topic_id):
    """Show a single topic and its entries; protect ownership."""
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by('-date_added')
    return render(request, 'learning_logs/topic.html', {'topic': topic, 'entries': entries})


@login_required
def new_topic(request):
    """Add a new topic (owned by the current user)."""
    if request.method != 'POST':
        form = TopicForm()
    else:
        form = TopicForm(data=request.POST)
        if form.is_valid():
            new_topic = form.save(commit=False)
            new_topic.owner = request.user
            new_topic.save()
            return redirect('learning_logs:topics')
    return render(request, 'learning_logs/new_topic.html', {'form': form})


@login_required
def new_entry(request, topic_id):
    """Add a new entry to an owned topic."""
    topic = get_object_or_404(Topic, id=topic_id)
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    return render(request, 'learning_logs/new_entry.html', {'topic': topic, 'form': form})


@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry; protect ownership via its topic."""
    entry = get_object_or_404(Entry, id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404

    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    return render(request, 'learning_logs/edit_entry.html', {'entry': entry, 'topic': topic, 'form': form})