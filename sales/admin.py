from django.contrib import admin
from .models import Product,Lead,EngagementEvent,LeadScoreHistory,Outreach
admin.site.register([Product,Lead,EngagementEvent,LeadScoreHistory,Outreach])
