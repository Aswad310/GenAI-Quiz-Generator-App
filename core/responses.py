from rest_framework.response import Response
from rest_framework import status


class BaseResponse(Response):
    def __init__(self, data=None, message="", status_code=status.HTTP_200_OK, success=True, **kwargs):
        content = {
            "status": success,
            "message": message,
            "data": data if data is not None else {}
        }
        super().__init__(data=content, status=status_code, **kwargs)
