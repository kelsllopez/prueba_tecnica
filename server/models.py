from django.db import models

class SafeguardReport(models.Model):
    machine_serial = models.CharField(max_length=20, default="844585")
    report_datetime = models.DateTimeField(auto_now_add=True)
    engine_off_timestamp = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    distance_to_road_m = models.FloatField()
    is_safe = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'safeguard_reports'
        ordering = ['-engine_off_timestamp']

    def __str__(self):
        status = "Seguro" if self.is_safe else "Inseguro"
        return f"Resguardo {self.machine_serial} - {self.engine_off_timestamp} ({status})"
