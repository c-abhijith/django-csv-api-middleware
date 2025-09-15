# from django.test import TestCase
from .models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

class UserTests(APITestCase):
    def setUp(self):
        self.existing = User.objects.create(name="example", email="example@gmail.com", age=30)
        self.url = reverse("user-list")
       
    def csv_file(self, text: str, name: str = "users.csv", content_type: str = "text/csv"):
        return SimpleUploadedFile(name, text.encode("utf-8"), content_type=content_type)

    def test_no_file_400(self):
        res = self.client.post(self.url, data={}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)
        self.assertTrue(res.data["error"], "No file provided") 
        
    def test_invalid_csv_400(self):
        user_file = SimpleUploadedFile(
            "user.csv",
            b"",
            content_type="text/csv"
        )
        res = self.client.post(self.url, data={"file": user_file}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)
        self.assertTrue(res.data["error"],"Failed to read CSV")
        
    def test_non_csv_extension_400(self):
        file = SimpleUploadedFile("users.txt", b"name,email,age\nA,a@gmail.com,20\n", content_type="text/plain")
        res = self.client.post(self.url, data={"file": file}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", res.data)
        self.assertTrue(res.data["error"], "Uploaded file is not a CSV.")
        
        
    def test_age_failure_400(self):
        csv = (
            "name,email,age\n"
            "TooYoung,young@gmail.com,-1\n"
            "TooOld,old@gmail.com,130\n"
            "Ok,ok@gmail.com,40\n"
        )
        res = self.client.post(self.url, data={"file": self.csv_file(csv)}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        invalid_age = res.data["Detailed_validation"]["invalid_age_rows"]["rows"]
        self.assertEqual(len(invalid_age), 2)
        self.assertEqual(res.data["total_records"], 3)
        self.assertEqual(res.data["success_data"], 1)  
        self.assertEqual(res.data["failure_data"], 2)
    
    def test_field_nan_remove_400(self):
        csv = (
            "name,email,age\n"
            "Sam,,20\n"         
            ",sam@gmail.com,21\n" 
            "Good,good@gmail.com,22\n"
        )
        res = self.client.post(self.url, data={"file": self.csv_file(csv)}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        missing = res.data["Detailed_validation"]["rows_with_empty_string"]["rows"]
        self.assertEqual(len(missing), 2)
        self.assertEqual(res.data["success_data"], 1)  
        self.assertTrue(User.objects.filter(email="good@gmail.com").exists())
        
    def test_invalid_email_400(self):
        csv = (
            "name,email,age\n"
            "Yahoo User,user@yahoo.com,33\n"  
            "Bad Email,bad,28\n"              
            "Good Gmail,ok@gmail.com,20\n"    
        )
        res = self.client.post(self.url, data={"file": self.csv_file(csv)}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        invalid = res.data["Detailed_validation"]["invalid_email_rows"]["rows"]
        self.assertEqual(len(invalid), 2)
        self.assertEqual(res.data["success_data"], 1)
        self.assertTrue(User.objects.filter(email="ok@gmail.com").exists())
        
    def test_email_exist_400(self):
        csv = (
            "name,email,age\n"
            "example,example@gmail.com,31\n" 
            "New One,new@gmail.com,26\n"
        )
        res = self.client.post(self.url, data={"file": self.csv_file(csv)}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        already = res.data["Detailed_validation"]["already_existing_emails_in_db"]["rows"]
        self.assertEqual(len(already), 1)
        self.assertTrue(User.objects.filter(email="new@gmail.com").exists())
        self.assertEqual(User.objects.filter(email="example@gmail.com").count(), 1)
        
    def test_user_csv_created_200(self):
        csv = (
            "name,email,age\n"
            "A,a1@gmail.com,20\n"
            "B,b1@gmail.com,21\n"
        )
        res = self.client.post(self.url, data={"file": self.csv_file(csv)}, format="multipart")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["total_records"], 2)
        self.assertEqual(res.data["success_data"], 2)
        self.assertEqual(res.data["failure_data"], 0)
       