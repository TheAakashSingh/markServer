import datetime

from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import pandas as pd
import numpy as np

from data_management.models import DataTable
from user_management import permissions
from django.forms.models import model_to_dict


class EditData(APIView):
    permission_classes = (
        permissions.IsAdmin,
    )

    def put(self, request):
        row_id = request.data.get('row_id')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        address = request.data.get('address')
        mobile_no = request.data.get('mobile_no')
        email_id = request.data.get('email_id')
        city = request.data.get('city')
        pincode = request.data.get('pincode')
        order_item = request.data.get('order_item')
        order_restaurant = request.data.get('order_restaurant')
        updated_by = request.data.get('employee_id')
        date_of_birth = request.data.get('date_of_birth')
        if date_of_birth:
            date_of_birth = datetime.datetime.strptime(date_of_birth, '%Y/%m/%d')
        try:

            if row_id:
                data = DataTable.objects.get(row_id=row_id)
                if data:
                    data.first_name = first_name if first_name else data.first_name
                    data.last_name = last_name if last_name else data.last_name
                    data.address = address if address else data.address
                    data.mobile_no = mobile_no if mobile_no else data.mobile_no
                    data.email_id = email_id if email_id else data.email_id
                    data.city = city if city else data.city
                    data.pincode = pincode if pincode else data.pincode
                    data.order_item = order_item if order_item else data.order_item
                    data.order_restaurant = order_restaurant if order_restaurant else data.order_restaurant
                    data.updated_by = updated_by if updated_by else data.updated_by
                    data.date_of_birth = date_of_birth if date_of_birth else data.date_of_birth
                    data.updated_date = datetime.datetime.now()
                    data.save()
                    return Response({'msg': 'Data saved successfully'}, status.HTTP_201_CREATED)
                else:
                    return Response({'msg': 'Data not found'}, status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'msg': 'Exception occurred while saving' + str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        row_id = request.data.get('row_id')
        try:
            if row_id:
                data = DataTable.objects.get(row_id=row_id)
                if data:
                    data.delete()
                    return Response({'message': 'Data deleted successfully'}, status.HTTP_200_OK)
                else:
                    return Response({'message': 'Not found'}, status.HTTP_404_NOT_FOUND)
            else:
                return Response({'message': 'Row ID required'}, status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Error occurred while deleting ' + str(e)},
                            status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadData(APIView):
    permissions = [permissions.IsAdmin]
    ACCEPTED_FILE_TYPES = {'xlsx', 'xls', 'csv'}
    MANDATORY_COLUMNS = {'first_name', 'last_name', 'pincode', 'address', 'mobile_no', 'email_id', 'date_of_birth',
                         'city'}
    OPTIONAL_COLUMNS = {'order_item', 'order_restaurant'}

    def post(self, request):
        file = request.FILES.get('file')
        file_extension = file.name.split(".")[-1]
        if file_extension not in self.ACCEPTED_FILE_TYPES:
            return Response({'msg': 'Invalid file type. We are only processing xlsx, xls and csv documents only`'}, status.HTTP_400_BAD_REQUEST)
        try:
            if file_extension == 'csv':
                df = pd.read_csv(file)

            else:
                df = pd.read_excel(file, engine='openpyxl')
            file_columns = set(df.columns.tolist())
            if self.MANDATORY_COLUMNS - file_columns:
                return Response({'message': 'Missing mandatory columns from file. Make sure the column name matches '
                                            'exactly with following fields',
                                 'mandatory_columns': self.MANDATORY_COLUMNS, 'optional_columns': self.OPTIONAL_COLUMNS,
                                 'missing_columns': self.MANDATORY_COLUMNS - file_columns}, status.HTTP_400_BAD_REQUEST)
            df.replace(np.nan, None, inplace=True)
            for _, row in df.iterrows():
                data = DataTable.objects.create()
                data.first_name = row.get('first_name')
                data.city = row.get('city')
                data.last_name = row.get('last_name')
                data.pincode = row.get('pincode')
                data.mobile_no = row.get('mobile_no')
                data.address = row.get('address')
                data.date_of_birth = row.get('date_of_birth')
                data.email_id = row.get('email_id')
                data.order_item = row.get('order_item')
                data.order_restaurant = row.get('order_restaurant')
                data.created_date = datetime.datetime.now()
                data.created_by = request.data.get('employee_id')
                data.save()

            return Response({'msg: Data uploaded successfully to database'}, status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'msg': 'Data upload failed ' + str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)


class ViewCustomerData(APIView):
    permissions = [AllowAny]

    def get(self, request):
        row_id = request.GET.get('row_id', None)
        first_name = request.GET.get('first_name', None)
        last_name = request.GET.get('last_name', None)
        mobile_no = request.GET.get('mobile_no', None)
        email_id = request.GET.get('email_id', None)
        address = request.GET.get('address', None)
        date_of_birth = request.GET.get('date_of_birth', None)
        city = request.GET.get('city', None)
        pincode = request.GET.get('pincode', None)
        filer_dict = {
            'first_name': first_name,
            'last_name': last_name,
            'mobile_no': mobile_no,
            'email_id': email_id,
            'address': address,
            'date_of_birth': date_of_birth,
            'city': city,
            'pincode': pincode
        }
        try:
            if not row_id:
                if not first_name and not last_name and not mobile_no and not email_id and not address and not date_of_birth and not city and not pincode:
                    data_rows = DataTable.objects.all().order_by('row_id')[:50]
                else:
                    data_rows = DataTable.objects.filter(*[Q(**{k: v}) for k, v in filer_dict.items() if v]).order_by(
                        'row_id')[:50]

            else:
                if not first_name and not last_name and not mobile_no and not email_id and not address and not date_of_birth and not city and not pincode:
                    data_rows = DataTable.objects.filter(row_id__gt=row_id).order_by('row_id')[:50]
                else:
                    data_rows = DataTable.objects.filter(*[Q(**{k: v}) for k, v in filer_dict.items() if v],
                                                         row_id__gt=row_id).order_by(
                        'row_id')[:50]
            final_data_list = []
            for data in data_rows:
                final_data_list.append(model_to_dict(data))

            return Response({'data': final_data_list}, status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': 'Error occurred ' + str(e)}, status.HTTP_500_INTERNAL_SERVER_ERROR)
