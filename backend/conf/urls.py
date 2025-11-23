from apps.auditlog.api import router as auditlog_router
from apps.conflict_detector.api import router as conflict_detector_router
from apps.proyectos_ley.api import router as proyectos_ley_router
from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.views import defaults as default_views
from ninja import NinjaAPI
from ninja.security import SessionAuth

########################
# API Configuration
########################
API_ROUTERS = [
    ("/auditlog", auditlog_router),
    ("/conflict-detector", conflict_detector_router),
    ("/proyectos-ley", proyectos_ley_router),
]

# Configuration process guards against multiple
session_auth = sync_to_async(SessionAuth(csrf=False))
api = NinjaAPI(title="gestion API", version="1.0.0", auth=session_auth)
for route_path, router in API_ROUTERS:
    if not router.api:
        api.add_router(route_path, router)


########################
# Django URL Configuration
########################
urlpatterns = [
    ######################
    # Webapp Template URLs
    ######################
    path(settings.ADMIN_PATH, admin.site.urls),
    path("users/", include("apps.users.urls", namespace="users")),
    path(".auth/accounts/", include("allauth.urls")),
    path(".auth/headless/", include("allauth.headless.urls")),
    path("api/", api.urls),
    path("_health/", lambda request: JsonResponse({"status": "ok"})),
    ######################
    # Additional URLs
    ######################
    # path(include("apps.myapp.urls", namespace="myapp")),
]

if settings.DEBUG:
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
