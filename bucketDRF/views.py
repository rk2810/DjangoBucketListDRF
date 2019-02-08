import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import get_authorization_header
from rest_framework_jwt.utils import jwt_encode_handler, jwt_decode_handler
from rest_framework.status import (HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST)
from django.contrib.auth.hashers import check_password, make_password

from bucketDRF.middleware.TokenHandler import jwt_payload_handler

# Models
from bucketDRF.models import User, Note


class SignUp(APIView):
    @staticmethod
    def post(request):
        username = request.POST.get('username')
        name = request.POST.get('name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        user_check = User.objects.filter(username=username)
        if user_check:
            return Response({'message': 'Please choose another username.'}, HTTP_400_BAD_REQUEST)
        if password != confirm_password:
            return Response({'message': 'Passwords do not match.'}, HTTP_400_BAD_REQUEST)
        password_hash = make_password(password)
        now = datetime.datetime.now()
        User.objects.create(username=username, password=password_hash, name=name, created_at=now, updated_at=now)
        return Response({'result': 'Signed up successfully.'}, HTTP_201_CREATED)


class SignIn(APIView):
    @staticmethod
    def post(request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=username, flag=1).first()
        if user_obj:
            if check_password(password, user_obj.password):
                payload = jwt_payload_handler(user_obj)
                token = jwt_encode_handler(payload)
                return Response({'message': 'Signed in successfully.',
                                 'user_details': {'id': user_obj.id,
                                                  'name': user_obj.name},
                                 'token': token})
        else:
            return Response({'User does not exist.'}, HTTP_400_BAD_REQUEST)


class GetNotes(APIView):
    @staticmethod
    def get(request):
        user_id = request.requested_by
        return Response([user_id], HTTP_200_OK)
