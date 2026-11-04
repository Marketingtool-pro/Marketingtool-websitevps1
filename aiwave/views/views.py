from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html', {
        'title': 'AI Marketing OS for Google & Meta Ads',
        'subtitle': 'AI Tool'
    }) 
