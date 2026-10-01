from django.urls import path
from . import views
urlpatterns=[path("",views.dashboard,name="dashboard"),path("leads/",views.leads,name="leads"),path("leads/<int:pk>/",views.lead_detail,name="lead_detail"),path("leads/<int:pk>/event/<str:event_type>/",views.event,name="event"),path("leads/<int:pk>/agents/",views.run_agents,name="run_agents"),path("leads/<int:pk>/outreach/",views.outreach,name="outreach")]
