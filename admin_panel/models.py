#admin_panel/models.py
from django.db import models

# Create your models here.

class UpcomingLaunch(models.Model):
    """
    Model to store details about upcoming car launches,
    including car specifics and launch event details.
    """
    car_name = models.CharField(max_length=200, help_text="Name of the car being launched.")
    car_minimal_details = models.TextField(
        blank=True,
        help_text="e.g., Engine CC, Power (BHP), Torque (Nm), Transmission type."
    )
    car_description = models.TextField(
        blank=True,
        help_text="Detailed description of the upcoming car."
    )
    
    launch_date = models.DateField(help_text="Date of the car launch event.")
    launch_time_start = models.TimeField(help_text="Start time of the launch event.")
    launch_time_end = models.TimeField(help_text="End time of the launch event.")
    venue = models.CharField(max_length=255, help_text="Name of the launch venue (e.g., 'Exhibition Hall 3').")
    location = models.CharField(max_length=255, help_text="City and state/country of the launch event (e.g., 'Mumbai, India').")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Upcoming Launch"
        verbose_name_plural = "Upcoming Launches"
        ordering = ['launch_date', 'launch_time_start']

    def __str__(self):
        return f"{self.car_name} Launch on {self.launch_date}"
