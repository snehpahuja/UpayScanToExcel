
from django.urls import path, include
from rest_framework.routers import DefaultRouter
import importlib
from django.http import JsonResponse

# Safe import of api.views (won't raise at import time)
try:
    views = importlib.import_module('api.views')
except Exception as e:
    views = None

def _get(name):
    return getattr(views, name) if views and hasattr(views, name) else None

def _not_impl(request, *args, **kwargs):
    return JsonResponse({'detail': 'endpoint not available (dev fallback)'}, status=501)

router = DefaultRouter()

# Register viewsets only if they exist
if _get('UserViewSet'):
    router.register(r'users', _get('UserViewSet'), basename='user')
if _get('CenterViewSet'):
    router.register(r'centers', _get('CenterViewSet'), basename='center')
if _get('DocumentViewSet'):
    router.register(r'documents', _get('DocumentViewSet'), basename='document')
# add more safe registrations here if needed (only when view exists)
if _get('DocumentReviewViewSet'):
    router.register(r'review', _get('DocumentReviewViewSet'), basename='review')
if _get('ProcessingQueueViewSet'):
    router.register(r'processing-queue', _get('ProcessingQueueViewSet'), basename='processing-queue')
if _get('StudentViewSet'):
    router.register(r'students', _get('StudentViewSet'), basename='student')

urlpatterns = [
    path('', include(router.urls)),
    # auth & basic endpoints (use real view if present, otherwise fallback)
    path('signup/', _get('SignupView').as_view() if _get('SignupView') else _not_impl, name='signup'),
    path('login/', _get('LoginView').as_view() if _get('LoginView') else _not_impl, name='login'),
    path('profile/', _get('UserProfileView').as_view() if _get('UserProfileView') else _not_impl, name='user-profile'),

    # upload endpoints (these are important for frontend). If missing, return fallback JSON.
    path('upload/files/', _get('DocumentUploadView').as_view() if _get('DocumentUploadView') else _not_impl, name='upload-files'),
    path('upload/bulk/', _get('BulkDocumentUploadView').as_view() if _get('BulkDocumentUploadView') else _not_impl, name='upload-bulk'),
    path('upload/categorize/', _get('DocumentCategorizationView').as_view() if _get('DocumentCategorizationView') else _not_impl, name='upload-categorize'),
]
# --- dev-only addition: stats route ---
from django.urls import path
# import the view we appended above (this uses a local import so it works even if api.views is large)
try:
    from .views import dev_stats
except Exception:
    # best-effort: if import fails, avoid breaking startup; stats route will be a no-op.
    dev_stats = None

if dev_stats:
    # Ensure urlpatterns exists, then append the route.
    try:
        urlpatterns  # noqa: F401
    except NameError:
        urlpatterns = []
    urlpatterns += [
        path('stats/', dev_stats, name='api-stats'),
    ]
# --- end dev-only addition ---
from . import views as _views
urlpatterns += [
    path('stats/filter/', getattr(_views, 'dev_stats_filtered', _not_impl), name='api-stats-filter'),
]
from api.views import DocumentListAPIView
urlpatterns += [
    path("documents/", DocumentListAPIView.as_view()),
]
