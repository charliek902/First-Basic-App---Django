from django.db import models

class MyModel(models.Model):
    id = models.AutoField(primary_key=True)  
    manufacturer = models.CharField(max_length=255)
    model_number = models.CharField(max_length=255)
    first_publication_date = models.DateField()
    on_market_start_date = models.DateField()
    power_on_mode_sdr = models.FloatField()
    power_on_mode_hdr = models.FloatField()
    screen_area = models.IntegerField()
    energy_class = models.CharField(max_length=255)
    energy_class_sdr = models.CharField(max_length=255)
    energy_class_hdr = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.manufacturer} - {self.model_number}"

    class Meta:
        app_label = 'EPRELServer'
        db_table = 'new_energyLibrary'
