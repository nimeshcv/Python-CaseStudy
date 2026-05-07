def user_role(request):
    user = getattr(request, "user", None)
    role = None

    if user and user.is_authenticated:
        if user.is_superuser:
            role = "admin"
        else:
            profile = getattr(user, "profile", None)
            role = getattr(profile, "role", None)

    return {"user_role": role}
