# from django.test import TestCase
from .models import User
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

# Create your tests here.

class UserTests(APITestCase):
    def setUp(self):
       self.user = User(name="example",email="example@gmail.com",age=30)
       self.url = reverse("user-list")

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

    def test_field_required_400(self):
        pass
    
    def test_age_is_numeric_400(self):
        pass
    def test_field_nan_remove_400(self):
        pass
    def test_email_exist_400(self):
        pass
    def test_user_csv_created_200(self):
        pass