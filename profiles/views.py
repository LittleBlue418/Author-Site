from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import UserProfileForm, UserForm


@login_required
def update_profile(request):
    """
    Displays the users profile if the user is logged in,
    handles change request to save updated user info
    """

    profile = request.user.profile

    if request.method == 'POST':
        user_profile_form = UserProfileForm(request.POST, instance=profile)
        user_form = UserForm(request.POST, instance=request.user)

        if user_profile_form.is_valid() and user_form.is_valid():
            user_profile_form.save()
            user_form.save()
            messages.success(request, 'Profile updated successfully')

    user_profile_form = UserProfileForm(instance=profile)
    user_form = UserForm(instance=request.user)

    context = {
        'user_profile_form': user_profile_form,
        'user_form': user_form
    }

    return render( request, 'profiles/update_profile.html', context)