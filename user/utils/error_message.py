from rest_framework.response import Response
from rest_framework import status


def internal_server_error_500(message):
    return Response( {
            "error":"error",
            "message": str(message),
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def bad_request_400(message,err):
    return Response({
                    "error":message,
                    "details": str(message)
                }, status=status.HTTP_400_BAD_REQUEST)
