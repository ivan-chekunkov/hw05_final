from django.shortcuts import render


def page_not_found(request, exception):
    """Отправка на кастомную страницу 404 ошибки."""
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    """Отправка на кастомную страницу 403 ошибки."""
    return render(request, 'core/403csrf.html')


def server_error(request):
    """Отправка на кастомную страницу 500 ошибки."""
    return render(request, 'core/500_server_error.html', status=500)
