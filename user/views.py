from rest_framework import viewsets
from rest_framework.response import Response
import pandas as pd
import numpy as np
from rest_framework.parsers import MultiPartParser
from rest_framework import status
import re

from .models import User
from .serializers import UserSerializer

from django.db import IntegrityError, transaction



class UserViewSet(viewsets.ViewSet):
    parser_classes = (MultiPartParser,)
    
    def create(self, request):
        response_data={}
        response_data["Detailed_validation"] = {}
        

        GMAIL_REGEX = re.compile(
            r"^[a-zA-Z0-9_.+-]+@gmail\.com$"
        )

        csv_file=request.data.get("file",None)  # upload file 
        if csv_file is None:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            return Response({"error": f"Failed to read CSV: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        
        df.columns =df.columns = df.columns.str.strip().str.lower()

        if not csv_file.name.lower().endswith('.csv'):
            return Response({"error": "Uploaded file is not a CSV."}, status=status.HTTP_400_BAD_REQUEST)
        
        required_columns = {'name', 'email', 'age'}
        csv_columns = set(df.columns)
        
        if csv_columns != required_columns:
                return Response({
                    "error": "Some fields are missed in csv file",
                    "expected_fields": sorted(required_columns),
                    "received_fields": sorted(csv_columns)
                }, status=status.HTTP_400_BAD_REQUEST)
                
        try:
            df['age'] = pd.to_numeric(df['age'], errors='coerce')  
        except Exception as e:
            return Response({"error": f"Invalid age format: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
                
        response_data["total_records"]=len(df)
        
        
        
        nan_rows = df[df[['name', 'email', 'age']].isna().any(axis=1)]
        response_data["Detailed_validation"]["rows_with_empty_string"] = {"rows":nan_rows.replace({np.nan: None}).to_dict(orient='records')}
        
        

        duplicate_emails = df[df.duplicated(subset='email', keep=False)]
        response_data["Detailed_validation"]["duplicate_emails"] = {"rows":duplicate_emails.replace({np.nan: None}).to_dict(orient='records')}
        
        
        
       
        
        
        invalid_age_rows = df[(df['age'] < 0) | (df['age'] > 120)]
        response_data["Detailed_validation"]["invalid_age_rows"] = {
            "rows": invalid_age_rows.replace({np.nan: None}).to_dict(orient='records')
        }

        
        df = df.drop(invalid_age_rows.index)

        # df = df.dropna(subset=['age'])
        df = df.drop(nan_rows.index)
        df['age'] = df['age'].astype(int)
        
        df['email'] = df['email'].str.lower()

        def is_valid_gmail(email):
            if pd.isna(email):
                return False
            return bool(GMAIL_REGEX.match(email))

        valid_email_mask = df['email'].apply(is_valid_gmail)

        invalid_email_rows = df[~valid_email_mask]
        response_data["Detailed_validation"]["invalid_email_rows"] = {
            "rows": invalid_email_rows.replace({np.nan: None}).to_dict(orient='records')
        }
        df = df[valid_email_mask].copy()
        
        
        
        existing_emails = set(User.objects.values_list('email', flat=True))
        already_existing_df = df[df['email'].isin(existing_emails)]
        df = df[~df['email'].isin(existing_emails)]
        response_data["Detailed_validation"]["already_existing_emails_in_db"] = {
            "rows": already_existing_df.replace({np.nan: None}).to_dict(orient='records')
        }
                
        df = df.drop_duplicates(subset='email', keep='first')
        response_data["success_data"]=len(df)
        response_data["failure_data"]=response_data["total_records"]-len(df)
        
        
        print(df)
        users_to_create = [
            User(name=row['name'], email=row['email'], age=row['age'])
            for _, row in df.iterrows()
        ]
        
        try:
            with transaction.atomic():
                User.objects.bulk_create(users_to_create)
        except Exception as err:
            return Response({
                "error": " duplicate emails already exist",
                "details": str(err)
            }, status=status.HTTP_400_BAD_REQUEST)
        



        return Response(response_data, status=status.HTTP_200_OK)
