from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from .models import Project, Role, Application
from .forms import ProjectForm, ApplicationForm


def browse_projects(request):
    projects = Project.objects.prefetch_related('roles').order_by('-created_at')
    query = request.GET.get('q', '')
    if query:
        projects = projects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    if request.GET.get('paid') == '1':
        projects = projects.filter(is_paid=True)
    if request.GET.get('unpaid') == '1':
        projects = projects.filter(is_unpaid=True)
    if request.GET.get('tech') == '1':
        projects = projects.filter(is_tech=True)
    if request.GET.get('non_tech') == '1':
        projects = projects.filter(is_non_tech=True)
    if request.GET.get('part_time') == '1':
        projects = projects.filter(is_part_time=True)
    if request.GET.get('full_time') == '1':
        projects = projects.filter(is_full_time=True)
    return render(request, 'projects/browse.html', {
        'projects': projects,
        'query': query,
    })


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    roles = project.roles.all()
    applied_role_ids = []
    if request.user.is_authenticated:
        applied_role_ids = list(Application.objects.filter(
            applicant=request.user, project=project
        ).values_list('role_id', flat=True))
    return render(request, 'projects/detail.html', {
        'project': project,
        'roles': roles,
        'applied_role_ids': applied_role_ids,
    })


@login_required
def create_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.creator = request.user
            project.save()
            role_names = request.POST.getlist('role_names')
            for role_name in role_names:
                if role_name.strip():
                    Role.objects.create(project=project, role_name=role_name.strip())
            messages.success(request, 'Project created!')
            return redirect('project_detail', pk=project.pk)
        else:
            print("FORM ERRORS:", form.errors)
    else:
        form = ProjectForm()
    return render(request, 'projects/create.html', {'form': form})


@login_required
def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk, creator=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            project.roles.all().delete()
            role_names = request.POST.getlist('role_names')
            for role_name in role_names:
                if role_name.strip():
                    Role.objects.create(project=project, role_name=role_name.strip())
            messages.success(request, 'Project updated.')
            return redirect('project_detail', pk=project.pk)
        else:
            print("FORM ERRORS:", form.errors)
    else:
        form = ProjectForm(instance=project)
    existing_roles = project.roles.all()
    return render(request, 'projects/edit.html', {
        'form': form,
        'project': project,
        'existing_roles': existing_roles,
    })


@login_required
def delete_project(request, pk):
    project = get_object_or_404(Project, pk=pk, creator=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted.')
        return redirect('dashboard')
    return render(request, 'projects/confirm_delete.html', {'project': project})


@login_required
def apply_to_role(request, role_pk):
    role = get_object_or_404(Role, pk=role_pk)
    project = role.project
    if project.creator == request.user:
        messages.error(request, "You can't apply to your own project.")
        return redirect('project_detail', pk=project.pk)
    if Application.objects.filter(applicant=request.user, role=role).exists():
        messages.warning(request, 'You have already applied to this role.')
        return redirect('project_detail', pk=project.pk)
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.role = role
            application.project = project
            application.save()
            send_mail(
                subject=f'New application for {role.role_name} in "{project.title}"',
                message=(
                    f'{request.user.get_full_name() or request.user.username} applied '
                    f'for {role.role_name} in your project "{project.title}".\n\n'
                    f'Log in to review the application.'
                ),
                from_email=None,
                recipient_list=[project.creator.email],
                fail_silently=True,
            )
            messages.success(request, 'Application submitted!')
            return redirect('my_applications')
        else:
            print("FORM ERRORS:", form.errors)
    else:
        form = ApplicationForm()
    return render(request, 'projects/apply.html', {
        'form': form,
        'role': role,
        'project': project,
    })


@login_required
def my_applications(request):
    applications = request.user.applications.select_related(
        'role', 'project'
    ).order_by('-applied_at')
    return render(request, 'projects/my_applications.html', {
        'applications': applications,
    })


@login_required
def manage_applications(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, creator=request.user)
    roles = project.roles.prefetch_related(
        'applications__applicant__profile'
    ).all()
    return render(request, 'projects/manage_applications.html', {
        'project': project,
        'roles': roles,
    })


@login_required
def update_application_status(request, app_pk, status):
    application = get_object_or_404(
        Application, pk=app_pk, project__creator=request.user
    )
    if status == 'shortlisted':
        application.status = 'shortlisted'
        application.save()
        send_mail(
            subject=f'You have been shortlisted for {application.role.role_name}!',
            message=(
                f'Hi {application.applicant.get_full_name() or application.applicant.username},\n\n'
                f'Great news! You have been shortlisted for the role of '
                f'{application.role.role_name} in "{application.project.title}".\n\n'
                f'The project creator will contact you to arrange an interview.\n\n'
                f'Creator contact details:\n'
                f'Name: {application.project.creator.get_full_name() or application.project.creator.username}\n'
                f'Email: {application.project.creator.email}\n'
                f'Phone: {getattr(application.project.creator.profile, "phone_number", "Not provided")}\n\n'
                f'Good luck!'
            ),
            from_email=None,
            recipient_list=[application.applicant.email],
            fail_silently=True,
        )
        messages.success(request, 'Applicant shortlisted — they have been notified.')

    elif status == 'accepted':
        application.status = 'accepted'
        application.save()
        application.role.is_filled = True
        application.role.save()
        send_mail(
            subject=f'Congratulations! You got accepted for {application.role.role_name}!',
            message=(
                f'Hi {application.applicant.get_full_name() or application.applicant.username},\n\n'
                f'Congratulations! Your application for {application.role.role_name} '
                f'in "{application.project.title}" has been ACCEPTED.\n\n'
                f'Creator contact details:\n'
                f'Name: {application.project.creator.get_full_name() or application.project.creator.username}\n'
                f'Email: {application.project.creator.email}\n'
                f'Phone: {getattr(application.project.creator.profile, "phone_number", "Not provided")}\n\n'
                f'Welcome to the team!'
            ),
            from_email=None,
            recipient_list=[application.applicant.email],
            fail_silently=True,
        )
        send_mail(
            subject=f'You accepted {application.applicant.get_full_name() or application.applicant.username}',
            message=(
                f'Hi {application.project.creator.get_full_name() or application.project.creator.username},\n\n'
                f'You accepted {application.applicant.get_full_name() or application.applicant.username} '
                f'for {application.role.role_name} in "{application.project.title}".\n\n'
                f'Their contact details:\n'
                f'Name: {application.applicant.get_full_name() or application.applicant.username}\n'
                f'Email: {application.applicant.email}\n'
                f'Phone: {getattr(application.applicant.profile, "phone_number", "Not provided")}\n\n'
                f'Reach out and get started!'
            ),
            from_email=None,
            recipient_list=[application.project.creator.email],
            fail_silently=True,
        )
        messages.success(request, 'Application accepted!')

    elif status == 'rejected':
        application.status = 'rejected'
        application.save()
        send_mail(
            subject=f'Update on your application for {application.role.role_name}',
            message=(
                f'Hi {application.applicant.get_full_name() or application.applicant.username},\n\n'
                f'Thank you for applying for {application.role.role_name} '
                f'in "{application.project.title}".\n\n'
                f'Unfortunately your application was not selected this time.\n\n'
                f'Keep browsing CollabSpace for more opportunities!'
            ),
            from_email=None,
            recipient_list=[application.applicant.email],
            fail_silently=True,
        )
        messages.success(request, 'Application rejected.')

    return redirect('manage_applications', project_pk=application.project.pk)


@login_required
def schedule_interview(request, app_pk):
    application = get_object_or_404(
        Application, pk=app_pk, project__creator=request.user
    )
    if request.method == 'POST':
        interview_date = request.POST.get('interview_date')
        interview_time = request.POST.get('interview_time')
        interview_link = request.POST.get('interview_link')
        interview_notes = request.POST.get('interview_notes', '')
        application.interview_date = interview_date
        application.interview_time = interview_time
        application.interview_link = interview_link
        application.interview_notes = interview_notes
        application.status = 'interview_scheduled'
        application.save()
        send_mail(
            subject=f'Interview scheduled for {application.role.role_name} — {application.project.title}',
            message=(
                f'Hi {application.applicant.get_full_name() or application.applicant.username},\n\n'
                f'Your interview has been scheduled for the role of '
                f'{application.role.role_name} in "{application.project.title}".\n\n'
                f'Interview details:\n'
                f'Date: {interview_date}\n'
                f'Time: {interview_time}\n'
                f'Meeting link: {interview_link}\n'
                f'Notes: {interview_notes}\n\n'
                f'Best of luck!'
            ),
            from_email=None,
            recipient_list=[application.applicant.email],
            fail_silently=True,
        )
        messages.success(request, 'Interview scheduled — applicant has been notified!')
        return redirect('manage_applications', project_pk=application.project.pk)
    return render(request, 'projects/schedule_interview.html', {
        'application': application,
    })