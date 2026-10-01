def research_lead(lead):
    return f"{lead.company_name} operates in {lead.industry} with an estimated fleet of {lead.existing_fleet_size} vehicles. Likely EV opportunity: {lead.estimated_ev_requirement} vehicles, travelling about {lead.monthly_km_per_vehicle} km/vehicle/month. Purchase horizon: {lead.purchase_timeline}."

def match_product(lead, products):
    if not products: return None
    if lead.estimated_ev_requirement>=80:
        return sorted(products,key=lambda p:(p.payload_kg,p.range_km),reverse=True)[0]
    if lead.monthly_km_per_vehicle>=2200:
        return sorted(products,key=lambda p:p.range_km,reverse=True)[0]
    affordable=[p for p in products if float(p.price)<=float(lead.budget_per_vehicle)*1.15]
    return (affordable or products)[0]

def outreach_text(lead, roi):
    product=lead.recommended_product.name if lead.recommended_product else "our EV fleet solution"
    subject=f"EV fleet savings opportunity for {lead.company_name}"
    msg=(f"Hi {lead.contact_name or 'Team'},\n\nBased on your {lead.industry.lower()} operations and an estimated requirement of {lead.estimated_ev_requirement} vehicles, "
         f"we recommend {product}. At your estimated usage, an EV transition could save approximately ₹{roi['annual_savings']:,} annually across the proposed fleet. "
         f"We would be happy to share a fleet pricing and pilot proposal tailored to {lead.company_name}.\n\nRegards,\nEV Fleet Sales Team")
    return subject,msg
