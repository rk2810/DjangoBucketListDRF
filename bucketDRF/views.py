#  Django imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.utils import jwt_encode_handler
from rest_framework.status import (HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST)
from django.contrib.auth.hashers import check_password, make_password

# Middleware imports
from bucketDRF.middleware.TokenHandler import jwt_payload_handler

# Models import
from bucketDRF.models import User, Note

# Misc. imports
import datetime


class SignUp(APIView):
    @staticmethod
    def post(request):
        """SignUp requires the following post parameters in body(x-www-form-urlencoded):
        Method: POST
        username (each user is supposed to have a unique username),
        name (full name of user),
        password (bcrypt is used to save hash of the password),
        and confirm_password.

         url pattern -> /auth/signup/

        return:
        <Created 201>:
        1. {'result': 'Signed up successfully.'}
        Signed up successfully.

        <Bad request 400>:
        1. {'message': 'Please choose another username.'}
        if username is already taken.

        2. {'message': 'Passwords do not match.'}
        When password != confirm_password
        """

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
        """
        SignIn requires the following post parameters in body(x-www-form-urlencoded):
        Method: POST
        username (user's unique identity)
        password (user's password)

        url pattern -> /auth/signin/

        return:
        <OK 200>:
        1. {
        'message': 'Signed in successfully.',
        'user_details':
            {
            'id': <user_id>,
            'name': <user_name>
            },
        'token': <jwt_token>
        }

        <Bad request 400>:
        1. {'message': 'User does not exist.'}
        User credentials are invalid / user does not exist.
        """

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
                                 'token': token}, HTTP_200_OK)
        else:
            return Response({'message': 'User does not exist.'}, HTTP_400_BAD_REQUEST)


class GetNotes(APIView):
    @staticmethod
    def get(request):
        """
        GetNotes extract <user_id> from the token.
        Method: GET
        user_id from JWT thru middleware
        note_id (optional, to load a particular note)

        url pattern -> notes/view

        return:
        <OK 200>
        1. {'message': 'No notes found.'}
        When no notes are found for the particular user.

        2. {
        'result': [
            {
            'id': <note_id>,
            'title': <note_title>,
            'details': <note_data/details>,
            'created_at': <note_created_at>,
            'updated_at': <note_updated_at>
            },
            {. . .}
        ]
        }
        All notes associated to the user.
        """
        print(request.user.id)
        user_id = request.requested_by
        note_id = request.GET.get('note_id', None)
        if not note_id:
            dynamic_filter = {'user_id': user_id, 'archived': False, 'flag': True}
        else:
            dynamic_filter = {'user_id': user_id, 'archived': False, 'flag': True, 'note_id': note_id}

        notes_data = Note.objects.filter(**dynamic_filter).values('id', 'title', 'details', 'created_at', 'updated_at')
        if not notes_data:
            return Response({'message': 'No notes found.'}, HTTP_200_OK)
        return Response({'result': notes_data}, HTTP_200_OK)


class CreateNote(APIView):
    @staticmethod
    def post(request):
        """
        CreateNote requires the following post parameters in body(x-www-form-urlencoded):
        Method: POST
        however, user_id is extracted from JWT token
        details (note data/text)
        title(note title)

        url pattern -> notes/create/

        return:
        <Created 201>:
        {'result': 'Note created!'}
        Entry of note is saved.
        """

        user_id = request.requested_by
        details = request.POST.get('details', None)
        title = request.POST.get('title', None)
        now = datetime.datetime.now()
        Note.objects.create(user_id=user_id, title=title, details=details, created_at=now, updated_at=now, flag=True)
        return Response({'result': 'Note created!'}, HTTP_201_CREATED)


class EditNote(APIView):
    @staticmethod
    def post(request):
        """
        EditNote requires the following post parameters in body(x-www-form-urlencoded):
        Method: POST
        user_id is however extracted from JWT
        note_id (ID of note to be edited)
        mode (edit/delete)
            1. <edit> mode:
                editing requires the following fields:
                details (note detail/data)
                title (note title)
                -> Basically the whole note object is updated with new data
            2 <delete> mode:
                deleting requires just <note_id>
                -> DO USE CONFIRMATION ON FRONTEND BEFORE EXECUTING THIS, This operation
                cannot be reverted.

         url pattern -> notes/edit/

        return:
         <OK 200>:
         1. {'result': 'Note edited'}
         When note is edited successfully.

         2. {'result': 'Note deleted.'}
         When note is deleted successfully.

        <Bad request 400>:
        1. {'message': 'No note_id'}
        When note_id is not provided.

        2. {'message': 'Note not found'}
        When provided note_id does not exist.

        3. {'message': 'Please provide a mode, edit or delete'}
        When the operation mode is not specified
        """

        user_id = request.requested_by
        note_id = request.POST.get('note_id', None)
        mode = request.POST.get('mode', None)
        details = request.POST.get('details', None)
        title = request.POST.get('title', None)
        now = datetime.datetime.now()
        if not note_id:
            return Response({'message': 'No note_id'}, HTTP_400_BAD_REQUEST)
        note_obj = Note.objects.get(id=note_id, user_id=user_id)
        if mode == 'edit':
            if note_obj:
                note_obj.details = details
                note_obj.title = title
                note_obj.updated_at = now
                note_obj.save()

                return Response({'result': 'Note edited'}, HTTP_200_OK)
            else:
                return Response({'message': 'Note not found'}, HTTP_400_BAD_REQUEST)
        elif mode == 'delete':
            if note_obj:
                note_obj.delete()
                return Response({'result': 'Note deleted.'}, HTTP_200_OK)
            else:
                return Response({'message': 'Note not found'}, HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'Please provide a mode, edit or delete'}, HTTP_400_BAD_REQUEST)


class ArchiveNote(APIView):
    @staticmethod
    def get(request):
        """
        ArchiveNote requires note_id from URL parameter.
        Method: GET

        url pattern -> notes/archive

        return:
        <OK 200>:
        1. {'result': 'Note archived!'}
        When note is archived successfully.

        <Bad request 400>:
        1. {'message': 'Note not found.'}
        When note_id does not exist.

        """
        user_id = request.requested_by
        note_id = request.GET.get('note_id')
        note_obj = Note.objects.filter(id=note_id, user_id=user_id).first()
        if not note_obj:
            return  Response({'message': 'Note not found.'}, HTTP_400_BAD_REQUEST)
        note_obj.archived = True
        note_obj.save()
        return Response({'result': 'Note archived!'}, HTTP_200_OK)


class ViewArchivedNotes(APIView):
    @staticmethod
    def get(request):
        """
                ViewArchivedNotes extract <user_id> from the token.
                Method: GET
                user_id from JWT thru middleware

                url pattern -> notes/getarchived

                return:
                <OK 200>
                1. {'message': 'No notes found.'}
                When no notes are found for the particular user.

                2. {
                'result': [
                    {
                    'id': <note_id>,
                    'title': <note_title>,
                    'details': <note_data/details>,
                    'created_at': <note_created_at>,
                    'updated_at': <note_updated_at>
                    },
                    {. . .}
                ]
                }
                All notes associated to the user.
                """
        user_id = request.requested_by
        notes_data = Note.objects.filter(user_id=user_id, archived=True, flag=True).values('id', 'title', 'details',
                                                                                           'created_at', 'updated_at')
        if not notes_data:
            return Response({'message': 'No notes found.'}, HTTP_200_OK)
        return Response({'result': notes_data}, HTTP_200_OK)
