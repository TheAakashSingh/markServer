from django.contrib.auth.hashers import make_password
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from user_management import permissions
from user_management.models import UserProfile, Group, UserGroup
from user_management.serializers import UserCreateReqSerializers
from datetime import datetime
from rest_framework.permissions import AllowAny
# Create your views here.
class Users(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_uuid=None):
        """
        Get request for Users API to get user details

        Args:
            request (Request): rest_framework.request.Request
            user_uuid (str): unique ID of the user

        Returns:
            Response: User details and status
        """
        if user_uuid is None:
            user_profile = UserProfile.objects.all()
            user_list = []
            for user in user_profile:
                group = UserGroup.objects.filter(user=user)
                groups = []
                for g in group:
                    groups.append({'name': g.group.name, 'uu_id': g.group.uu_id})
                user_list.append(
                    {
                        "uu_id": user.uu_id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "date_of_birth": user.date_of_birth,
                        "phone_no": user.phone_no,
                        "gender": user.gender,
                        "employee_id": user.employee_id,
                        "role": str(user.role),
                        "image": user.image,
                        "is_active": user.is_active,
                        "password_updt_time": user.password_updt_time,
                        "groups": groups
                    }
                )
            return Response(user_list, status=status.HTTP_200_OK)
        else:
            try:
                user_profile = UserProfile.objects.get(uu_id=user_uuid)
                group = UserGroup.objects.filter(user=user_profile)
                groups = []
                for g in group:
                    groups.append({'name': g.group.name, 'uu_id': g.group.uu_id})
                user_data = {
                        "uu_id": user_profile.uu_id,
                        "email": user_profile.email,
                        "first_name": user_profile.first_name,
                        "last_name": user_profile.last_name,
                        "date_of_birth": user_profile.date_of_birth,
                        "phone_no": user_profile.phone_no,
                        "gender": user_profile.gender,
                        "employee_id": user_profile.employee_id,
                        "role": str(user_profile.role),
                        "image": user_profile.image,
                        "is_active": user_profile.is_active,
                        "password_updt_time": user_profile.password_updt_time,
                        'groups': groups
                }
                return Response(user_data, status=status.HTTP_200_OK)
            except UserProfile.DoesNotExist:

                return Response(
                    {"message": "User Doesn't Exists"}, status=status.HTTP_404_NOT_FOUND
                )

    def delete(self, request):
        try:
            user_uuid = request.data.get("user_uuid", None)
            user_profile = UserProfile.objects.get(uu_id=user_uuid)
            content = {"message": user_profile.uu_id}
            user_profile.delete()
            return Response(content, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response(
                {"message": "User Doesn't Exist"}, status=status.HTTP_404_NOT_FOUND
            )
        
    def post(self, request):
        serializer = UserCreateReqSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get("email").lower()
        password = request.data.get("password")
        role = request.data.get("role")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        dob = datetime.strptime(request.data.get("date_of_birth"), '%Y-%m-%d')
        gender = request.data.get("gender")
        mobile_no = request.data.get("phone_no")
        employee_id = request.data.get("employee_id")
        groups = request.data.get('groups', [])
        user_exist = UserProfile.objects.filter(email=email, employee_id=employee_id).exists()
        if user_exist:
            content = {"message": "User already Exist"}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            try:
                map_user = UserProfile.objects.create_user(email=email, first_name=first_name, last_name=last_name,
                                                           employee_id=employee_id, dob=dob, gender=gender,
                                                           mobile_no=mobile_no,role=role, password=password)
                for group in groups:
                    UserGroup.objects.create(user_id=map_user.id, group_id=group.get('uu_id'), created_time=datetime.now())
                content = {
                    "message": "User Successfully Created",
                    "user_id": map_user.uu_id
                }
                return Response(content, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'message': 'Error occurred while saving user ' + str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request):
        user_uuid = request.data.get("uu_id", None)
        email = request.data.get("email", None)
        if email:
            email = email.lower()
        password = request.data.get("password", None)
        if password:
            password = make_password(password)
        role = request.data.get("role", None)
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name")
        dob = request.data.get("date_of_birth")
        gender = request.data.get("gender")
        mobile_no = request.data.get("phone_no")
        employee_id = request.data.get("employee_id")
        image = request.data.get("image", None)
        groups = request.data.get("groups",[])
        try:
            current_user = UserProfile.objects.get(uu_id=user_uuid)
        except Exception as err:
            return Response(
                {'message': "User doesn't exist!!"}, status=status.HTTP_404_NOT_FOUND
            )

        email_exists = (UserProfile.objects.filter(email=email, employee_id=employee_id).exclude(uu_id=user_uuid).exists())
        if email_exists:
            content = {"message": "Another user with same employee id or email already exists"}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)


        UserProfile.objects.filter(uu_id=user_uuid).update(
            email=current_user.email if email is None else email,
            password=current_user.password if password is None else password,
            role = current_user.role if role is None else role,
            first_name = current_user.first_name if first_name is None else first_name,
            last_name = current_user.last_name if last_name is None else last_name,
            date_of_birth = current_user.date_of_birth if dob is None else dob,
            gender = current_user.gender if gender is None else gender,
            phone_no = current_user.phone_no if mobile_no is None else mobile_no,
            image=current_user.image if image is None else image
        )
        existing_user_groups = UserGroup.objects.filter(user=current_user)
        for grp in existing_user_groups:
            grp.delete()
        for group in groups:
            UserGroup.objects.create(user_id=current_user.uu_id,
                                     group_id=group.get('uu_id'),
                                     created_time=datetime.now())
        content = {
            "message": "User Successfully Updated",
            "user_id": current_user.uu_id
        }
        return Response(content, status=status.HTTP_200_OK)

class Groups(APIView):
    permission_classes = [AllowAny]
    def get(self, request, name=None):
        if name:
            try:
                group = Group.objects.get(name=name)
                group_data = {
                    'name': group.name,
                    'description': group.description,
                    'is_active': group.is_active,
                    'created_by': group.created_by,
                    'created_time': group.created_time,
                    'uu_id': group.uu_id
                }
                return Response({'data': group_data}, status.HTTP_200_OK)
            except Exception:
                return Response({'msg': 'Group does not exist'}, status.HTTP_404_NOT_FOUND)
        else:
            all_groups = []
            groups = Group.objects.all()
            for group in groups:
                all_groups.append({
                    'name': group.name,
                    'description': group.description,
                    'is_active': group.is_active,
                    'created_by': group.created_by.employee_id if group.created_by else None,
                    'created_time': group.created_time,
                    'uu_id': group.uu_id
                })
            return Response({'data': all_groups}, status.HTTP_200_OK)


    def put(self, request):
        uuid = request.data.get('uu_id')
        name = request.data.get("name")
        description = request.data.get('description')
        employee_id = request.data.get('employee_id')
        if uuid:
            try:
                group = Group.objects.filter(name=name).exclude(uu_id=uuid)
                if group:
                    return Response({'msg': "Group with same name already exists"}, status.HTTP_406_NOT_ACCEPTABLE)
                curr_group = Group.objects.get(uu_id=uuid)
                if curr_group:
                    curr_group.name = name if name else curr_group.name
                    curr_group.description = description if description else curr_group.description
                    user = UserProfile.objects.get(employee_id=employee_id)
                    if not user:
                        return Response({'msg': 'Incorrect employee ID or employee does not exists'}, status.HTTP_404_NOT_FOUND)
                    curr_group.updated_by = user
                    curr_group.updated_time = datetime.now()
                    curr_group.save()
                    return Response({'msg': "Group details updated successfully"}, status.HTTP_202_ACCEPTED)
                else:
                    return Response({'msg': 'Group with given ID does not exist'}, status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return  Response({'msg': 'Exception occurred ' + str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'msg': 'ID not sent for group'}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, uu_id):
        if not uu_id:
            return  Response({'msg': 'ID not sent in request'}, status.HTTP_400_BAD_REQUEST)

        try:
            group = Group.objects.get(uu_id=uu_id)
            if not group:
                return Response({'msg': 'Group with this ID does not exist: '+ str(uu_id)}, status.HTTP_400_BAD_REQUEST)
            group.is_active = False
            group.save()
            return Response({'msg': 'Group deleted successfully'}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': 'Error occurred while deleting group' + str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        name = request.data.get("name")
        description = request.data.get('description')
        employee_id = request.data.get('employee_id')
        group = Group.objects.filter(name=name)
        try:
            if group:
                return Response({'msg': 'Group with this name already exists'}, status.HTTP_406_NOT_ACCEPTABLE)
            user = UserProfile.objects.get(employee_id=employee_id)
            new_group = Group.objects.create(
                name=name,
                description=description,
                created_by=user,
                created_time=datetime.now()

            )
            return Response({'msg': 'Group created successfully with id: ' + str(new_group.uu_id)}, status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'msg': 'Error occurred while saving group: ' + str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
