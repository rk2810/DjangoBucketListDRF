import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.utils import jwt_encode_handler
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
        notes_data = Note.objects.filter(user_id=user_id, archived=False, flag=True).values('id', 'title', 'details',
                                                                                            'created_at', 'updated_at')
        if not notes_data:
            return Response({'message': 'No notes found.'}, HTTP_200_OK)
        return Response({'result': notes_data}, HTTP_200_OK)


class CreateNote(APIView):
    @staticmethod
    def post(request):
        user_id = request.requested_by
        details = request.POST.get('details', None)
        title = request.POST.get('title', None)
        now = datetime.datetime.now()
        Note.objects.create(user_id=user_id, title=title, details=details, created_at=now, updated_at=now, flag=True)
        return Response({'result': 'Note created!'}, HTTP_201_CREATED)


class EditNote(APIView):
    @staticmethod
    def post(request):
        user_id = request.requested_by
        note_id = request.POST.get('note_id', None)
        mode = request.POST.get('mode', None)
        details = request.POST.get('details', None)
        title = request.POST.get('title', None)
        now = datetime.datetime.now()
        if not note_id:
            return Response({'message': 'No note_id'}, HTTP_400_BAD_REQUEST)
        if mode == 'edit':
            note_obj = Note.objects.filter(id=note_id, user_id=user_id).first()
            if note_obj:
                note_obj.update(details=details, title=title, updated_at=now)
                return Response({'result': 'Note edited'}, HTTP_200_OK)
            else:
                return Response({'message': 'Note not found'}, HTTP_400_BAD_REQUEST)
        elif mode == 'delete':
            note_obj = Note.objects.filter(id=note_id, user_id=user_id).first()
            if note_obj:
                note_obj.delete()
                return Response({'result': 'Note edited'}, HTTP_200_OK)
            else:
                return Response({'message': 'Note not found'}, HTTP_400_BAD_REQUEST)
        else:
            return Response({'Please provide a mode, edit or delete'}, HTTP_400_BAD_REQUEST)


class ArchiveNote(APIView):
    @staticmethod
    def get(request):
        user_id = request.requested_by
        note_id = request.GET.get('note_id')
        note_obj = Note.objects.filter(id=note_id, user_id=user_id).first()
        note_obj.update(archived=True)
        return Response({'result': 'Note archived!'}, HTTP_200_OK)
