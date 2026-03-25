from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if response.status_code == status.HTTP_404_NOT_FOUND:
            response.data = {
                "message": response.data.get('detail', "Not found."),
                "status": False,
                "data": {}
            }
        
        elif response.status_code == status.HTTP_400_BAD_REQUEST:
            response.data = {
                "message": "Validation failed.",
                "status": False,
                "data": response.data
            }
        
        # If it's a 403 (Forbidden), reformat it
        elif response.status_code == status.HTTP_403_FORBIDDEN:
             response.data = {
                "message": response.data.get('detail', "Permission denied."),
                "status": False,
                "data": {}
            }
                    
    return response
