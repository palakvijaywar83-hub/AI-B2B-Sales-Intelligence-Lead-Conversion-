from django.db import models

class Product(models.Model):
    name=models.CharField(max_length=100)
    category=models.CharField(max_length=80)
    price=models.DecimalField(max_digits=12,decimal_places=2)
    range_km=models.PositiveIntegerField()
    payload_kg=models.PositiveIntegerField(default=100)
    best_for=models.CharField(max_length=250)
    def __str__(self): return self.name

class Lead(models.Model):
    STAGES=[("Cold","Cold"),("Qualified","Qualified"),("Warm","Warm"),("Hot","Hot"),("Converted","Converted")]
    company_name=models.CharField(max_length=160)
    industry=models.CharField(max_length=100)
    city=models.CharField(max_length=80)
    contact_name=models.CharField(max_length=100,blank=True)
    contact_role=models.CharField(max_length=100,blank=True)
    email=models.EmailField(blank=True)
    phone=models.CharField(max_length=30,blank=True)
    employee_count=models.PositiveIntegerField(default=50)
    existing_fleet_size=models.PositiveIntegerField(default=10)
    estimated_ev_requirement=models.PositiveIntegerField(default=5)
    monthly_km_per_vehicle=models.PositiveIntegerField(default=1500)
    budget_per_vehicle=models.DecimalField(max_digits=12,decimal_places=2,default=160000)
    purchase_timeline=models.CharField(max_length=50,default="1-3 Months")
    authority=models.CharField(max_length=50,default="Influencer")
    source=models.CharField(max_length=80,default="Lead Discovery Agent")
    research_summary=models.TextField(blank=True)
    recommended_product=models.ForeignKey(Product,null=True,blank=True,on_delete=models.SET_NULL)
    fit_score=models.FloatField(default=50)
    dynamic_score=models.FloatField(default=30)
    conversion_probability=models.FloatField(default=20)
    stage=models.CharField(max_length=20,choices=STAGES,default="Cold")
    next_best_action=models.CharField(max_length=200,default="Research company")
    next_action_reason=models.TextField(blank=True)
    converted=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self): return self.company_name

class EngagementEvent(models.Model):
    TYPES=[("email_open","Email Opened"),("pricing_click","Pricing Link Clicked"),("product_view","Product Viewed"),("brochure","Brochure Downloaded"),("whatsapp_reply","WhatsApp Replied"),("quote","Quotation Requested"),("demo","Demo Requested"),("no_response","No Response / Decay"),("not_interested","Not Interested")]
    lead=models.ForeignKey(Lead,on_delete=models.CASCADE,related_name="events")
    event_type=models.CharField(max_length=40,choices=TYPES)
    notes=models.CharField(max_length=250,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

class LeadScoreHistory(models.Model):
    lead=models.ForeignKey(Lead,on_delete=models.CASCADE,related_name="score_history")
    old_score=models.FloatField()
    new_score=models.FloatField()
    reason=models.CharField(max_length=250)
    created_at=models.DateTimeField(auto_now_add=True)

class Outreach(models.Model):
    lead=models.ForeignKey(Lead,on_delete=models.CASCADE,related_name="outreach")
    channel=models.CharField(max_length=30,default="Email")
    subject=models.CharField(max_length=200,blank=True)
    message=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
