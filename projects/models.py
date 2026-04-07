from django.db import models
from django.contrib.auth.models import User


class Project(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in months")
    is_tech = models.BooleanField(default=False)
    is_non_tech = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    is_unpaid = models.BooleanField(default=False)
    is_part_time = models.BooleanField(default=False)
    is_full_time = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_categories(self):
        cats = []
        if self.is_tech: cats.append('Tech')
        if self.is_non_tech: cats.append('Non-tech')
        if self.is_paid: cats.append('Paid')
        if self.is_unpaid: cats.append('Unpaid')
        if self.is_part_time: cats.append('Part-time')
        if self.is_full_time: cats.append('Full-time')
        return cats


class Role(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='roles')
    role_name = models.CharField(max_length=100)
    is_filled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.role_name} — {self.project.title}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]

    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='applications')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='applications')
    application_message = models.TextField()
    resume = models.FileField(upload_to='application_resumes/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Interview fields
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.TimeField(null=True, blank=True)
    interview_link = models.URLField(null=True, blank=True)
    interview_notes = models.TextField(null=True, blank=True)

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('applicant', 'role')

    def __str__(self):
        return f"{self.applicant.username} → {self.role.role_name}"