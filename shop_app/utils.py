from django.shortcuts import render


def check_integer(param_value):
    return isinstance(param_value, int) or isinstance(param_value, str) and param_value.isdigit()


def handle_error(request, message, status_code):
    error_dict = {
        'error_message': message,
        'status': status_code
    }
    return render(request, 'shop_app/error.html', status=status_code, context=error_dict)
