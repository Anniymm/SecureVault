from django.urls import path
from .views import Generate2FASetupView, Enable2FAView, Verify2FAView

urlpatterns = [
    path("generate/", Generate2FASetupView.as_view(), name="generate-2fa"),
    path("enable/", Enable2FAView.as_view(), name="enable-2fa"),
    path("verify/", Verify2FAView.as_view(), name="verify-2fa"),
]
