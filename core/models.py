from django.db import models
from django.contrib.auth.models import User



# --- Inventory Models ---
class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Stock(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    date = models.DateField(auto_now_add=True, null=True)
    def __str__(self):
        return f"{self.material.name} - {self.quantity} tons"

# --- Quarry Models ---
class Quarry(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=200)
    def __str__(self):
        return self.name

# --- Trucks Models ---
class TruckIn(models.Model):
    truck_number = models.CharField(max_length=50)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    gross_weight = models.FloatField()
    tare_weight = models.FloatField()
    net_weight = models.FloatField()
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

class TruckOut(models.Model):
    truck_number = models.CharField(max_length=50)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    gross_weight = models.FloatField()
    tare_weight = models.FloatField()
    net_weight = models.FloatField()
    destination = models.CharField(max_length=150)
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)







class Company(models.Model):
    name = models.CharField(max_length=200)
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name




class Project(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    client_name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return self.name





class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
    ]
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    assigned_to = models.CharField(max_length=20)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return self.title
   