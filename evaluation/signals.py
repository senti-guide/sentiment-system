from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib.auth.models import Group
from allauth.account.signals import user_logged_in as allauth_user_logged_in
import logging

# Set up logging to debug
logger = logging.getLogger(__name__)

@receiver(allauth_user_logged_in)
def add_user_to_student_group(sender, request, user, **kwargs):
    # Log to ensure the signal is fired
    logger.info(f"User {user.username} logged in. Checking if the user should be added to the students group.")

    # Check if the user has a social account and is logging in via Google
    if user.socialaccount_set.filter(provider='google').exists():
        # Log that the user is logging in via Google
        logger.info(f"User {user.username} logged in via Google.")

        # Ensure the 'students' group exists
        try:
            students_group = Group.objects.get(name='students')
            if students_group not in user.groups.all():
                user.groups.add(students_group)
                user.save()  # Save the user after adding the group
                logger.info(f"User {user.username} added to the 'students' group.")
            else:
                logger.info(f"User {user.username} is already in the 'students' group.")
        except Group.DoesNotExist:
            logger.error("The 'students' group does not exist in the database.")
    else:
        logger.info(f"User {user.username} did not log in via Google. No group added.")
