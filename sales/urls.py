from django.urls import path
from . import views


urlpatterns = [

path("", views.dashboard, name="dashboard"),

path("leads/", views.leads, name="leads"),
path("leads/high-intent/", views.high_intent_leads, name="high_intent_leads"),

path("recommendations/", views.recommendations, name="recommendations"),
path("product-matching/", views.product_matching, name="product_matching"),
path("dynamic-scoring/", views.dynamic_scoring, name="dynamic_scoring"),

path("agentic-ai/", views.agentic_ai, name="agentic_ai"),

path("leads/<int:pk>/", views.lead_detail, name="lead_detail"),
path("leads/<int:pk>/event/<str:event_type>/", views.event, name="event"),
path("leads/<int:pk>/run-agents/", views.run_agents, name="run_agents"),
path("leads/<int:pk>/outreach/", views.outreach, name="outreach"),
]