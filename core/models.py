from django.db import models



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
