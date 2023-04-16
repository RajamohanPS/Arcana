from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path('fdmnt/<str:symbol>', views.get_fundamentals, name="fundamental"),
    path('calreturn', views.portfolio_analyzer, name='analyzer')
    # path("<str:room_name>/", views.room, name="room"),
]