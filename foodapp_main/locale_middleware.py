import locale
from django.utils import translation

def LocaleMiddleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        locale.setlocale( locale.LC_ALL, '' )
        locale.setlocale( locale.LC_ALL, "en-gb.UTF-8" )
        translation.activate("en-GB")
        request.LANGUAGE_CODE = translation.get_language()
        language = translation.get_language_from_request(request)
        
        response = get_response(request)
        
        translation.deactivate()
        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware
   