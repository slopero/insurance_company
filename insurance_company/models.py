from django.db import models





class Employee(models.Model):
    id_employee = models.AutoField(primary_key=True)
    surname_employee = models.TextField()
    name_employee = models.TextField()
    patronymic = models.TextField()
    post = models.TextField()
    ser_pass = models.TextField()
    num_pass = models.TextField()
    birth_date = models.DateField()
    
    class Meta:
        unique_together = ['ser_pass', 'num_pass']
        db_table = 'employee'
        managed = False

class User(models.Model):
    id = models.AutoField(primary_key=True)
    login = models.TextField()
    password_hash = models.TextField()
    id_employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, db_column='id_employee')

    class Meta:
        db_table = 'users'
        managed = False
    
    
class Client(models.Model):
    GENDER_CHOICES = [
        ('мужской', 'Мужской'),
        ('женский', 'Женский'),
    ]
    
    id_client = models.AutoField(primary_key=True)
    surname_client = models.TextField()
    name_client = models.TextField()
    patronymic = models.TextField()
    gender = models.TextField(choices=GENDER_CHOICES)
    ser_pass = models.TextField()
    num_pass = models.TextField()
    birth_date = models.DateField()
    
    class Meta:
        unique_together = ['ser_pass', 'num_pass']
        db_table = 'clients'
        managed = False


class Contract(models.Model):
    id_contract = models.AutoField(primary_key=True)
    id_employee = models.ForeignKey(Employee, on_delete=models.DO_NOTHING, db_column='id_employee')
    id_client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, db_column='id_client')
    date_start = models.DateField()
    date_end = models.DateField()
    cost_insurance = models.FloatField()
    kind_insurance = models.TextField()
    
    class Meta:
        db_table = 'insurance_contract'
        managed = False
        