# Django Imports
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED
from rest_framework_jwt.authentication import api_settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render

# General Imports
import time
import datetime
import json
import os
import jwt

API_KEY = os.environ.get('API_KEY')
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER


def jwt_payload_handler(user):
    """ Custom payload handler
    Token encrypts the dictionary returned by this function, and can be decoded by rest_framework_jwt.utils.jwt_decode_handler
    """
    epoch_time = int(time.time())
    india_time = datetime.datetime.fromtimestamp(epoch_time)
    expiry_time = india_time + api_settings.JWT_EXPIRATION_DELTA
    return {
        'sub': user.id,
        'iss': api_settings.JWT_ISSUER,
        'exp': expiry_time,
        'iat': int(time.time()),
        'nbf': int(time.time()),
    }


class ApiTokenCheckMiddleware(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        if request.path == '/':
            return render(request, 'fallback.html', {})

        res = {'message': 'Api Key Invalid.'}
        request.start_time = time.time()
        try:
            if request.META['HTTP_KEY']:
                api_key = request.META['HTTP_KEY']
                if not api_key == API_KEY:
                    return HttpResponse(json.dumps(res), status=HTTP_400_BAD_REQUEST)
        except:
            return HttpResponse(json.dumps(res), status=HTTP_400_BAD_REQUEST)

        if not request.path.startswith('/auth/'):
            try:
                auth = request.META['HTTP_AUTHORIZATION'].split()[1]
                try:
                    payload = jwt_decode_handler(auth)
                    request.requested_by = payload.get('sub')
                except jwt.ExpiredSignature:
                    request.requested_by = None
                    return HttpResponse(json.dumps({'message': 'Signature has expired.'}),
                                        status=HTTP_401_UNAUTHORIZED)
                except jwt.DecodeError:
                    request.requested_by = None
                    return HttpResponse(json.dumps({'message': 'Error decoding signature.'}),
                                        status=HTTP_400_BAD_REQUEST)
                except jwt.InvalidTokenError:
                    request.requested_by = None
                    return HttpResponse(json.dumps({'message': 'Incorrect authentication token.'}),
                                        status=HTTP_401_UNAUTHORIZED)
            except Exception as e:
                print(e)
                return HttpResponse(json.dumps({'error': 'No Authorization token provided'}),
                                    status=HTTP_401_UNAUTHORIZED)

        return None
