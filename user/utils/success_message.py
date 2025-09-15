from rest_framework.response import Response
from rest_framework import status


def ok_200(data=None, message="Success"):
    return Response({
        "status": message,
        "data": data
    }, status=status.HTTP_200_OK)