from django.shortcuts import render


def customerSupport(request):
    return render(request, 'banking/customerSupport.html')

def custom_404_view(request, exception):
    context = {
        'title': '404'
    }
    return render(request, 'banking/404.html', status=404, context=context)