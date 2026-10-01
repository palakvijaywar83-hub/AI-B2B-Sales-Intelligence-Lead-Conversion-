from django.core.management.base import BaseCommand
from sales.models import Product,Lead
from sales.services import recalculate
from sales.agents import research_lead,match_product
class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        Product.objects.all().delete(); Lead.objects.all().delete()
        products=[
            Product.objects.create(name="VoltCargo Lite",category="Cargo Scooter",price=145000,range_km=85,payload_kg=100,best_for="Last-mile and food delivery"),
            Product.objects.create(name="VoltFleet Pro",category="Fleet Scooter",price=168000,range_km=110,payload_kg=110,best_for="High-utilization urban fleets"),
            Product.objects.create(name="VoltCargo Plus",category="Cargo Scooter",price=205000,range_km=140,payload_kg=140,best_for="Courier, grocery and heavy fleet usage"),
            Product.objects.create(name="Volt L5 Cargo",category="Electric 3-Wheeler",price=325000,range_km=160,payload_kg=500,best_for="Large cargo and logistics operations") ]
        data=[("RapidRoute Logistics","Courier & Logistics","Mumbai",420,260,75,2400,190000,"0-30 Days","Decision Maker"),("FreshDrop Foods","Food Delivery","Pune",300,180,55,2600,175000,"Immediate","Influencer"),("UrbanKart Commerce","E-commerce","Bengaluru",900,350,100,2100,210000,"1-3 Months","Decision Maker"),("Metro Facility Services","Facility Management","Delhi",600,90,20,1300,155000,"3-6 Months","Influencer"),("GreenBasket Delivery","Grocery Delivery","Hyderabad",240,125,40,2300,185000,"0-30 Days","Decision Maker"),("Apex Manufacturing","Manufacturing","Nagpur",1100,45,8,900,160000,"Exploring","Unknown"),("SwiftShip Express","Last-Mile Delivery","Gurugram",520,410,120,2800,220000,"Immediate","Decision Maker"),("PrimeLease Mobility","Rental & Leasing","Chennai",150,300,85,2000,195000,"1-3 Months","Decision Maker") ]
        for n,ind,city,emp,fleet,req,km,budget,timeline,auth in data:
            l=Lead.objects.create(company_name=n,industry=ind,city=city,contact_name="Operations Head",contact_role=auth,employee_count=emp,existing_fleet_size=fleet,estimated_ev_requirement=req,monthly_km_per_vehicle=km,budget_per_vehicle=budget,purchase_timeline=timeline,authority=auth)
            l.research_summary=research_lead(l); l.recommended_product=match_product(l,products); l.save(); recalculate(l,"Initial AI qualification")
        self.stdout.write(self.style.SUCCESS("Demo products and leads created."))
