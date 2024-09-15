from django.db import models

class Candidate(models.Model):
    first_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20)
