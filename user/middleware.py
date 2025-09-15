from django.core.cache import cache
from django.http import JsonResponse  
from rest_framework import status



class IPAddressLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip_address = self.get_client_ip(request)
        print(f"Client IP: {ip_address}")
        request.client_ip = ip_address
        key = f"ip:{ip_address}"
        count = cache.get(key, 0)
        count += 1
        cache.set(key, count)
        print(f"IP {ip_address} has made {count} requests.")
        if count > 100:
                return JsonResponse({"message": "Too many requests"}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
