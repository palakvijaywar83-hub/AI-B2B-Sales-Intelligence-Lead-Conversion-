from .models import EngagementEvent,LeadScoreHistory
EVENT_WEIGHTS={"email_open":2,"pricing_click":7,"product_view":5,"brochure":5,"whatsapp_reply":8,"quote":15,"demo":20,"no_response":-7,"not_interested":-30}

def base_fit(lead):
    industry={"Last-Mile Delivery":90,"Food Delivery":92,"Courier & Logistics":90,"E-commerce":84,"Grocery Delivery":82,"Rental & Leasing":76}.get(lead.industry,60)
    fleet=min(100,30+lead.existing_fleet_size*.25)
    req=min(100,35+lead.estimated_ev_requirement*.65)
    budget=min(100,max(20,float(lead.budget_per_vehicle)/2500))
    urgency={"Immediate":100,"0-30 Days":90,"1-3 Months":70,"3-6 Months":45,"Exploring":20}.get(lead.purchase_timeline,50)
    authority={"Decision Maker":100,"Influencer":70,"User":45,"Unknown":25}.get(lead.authority,40)
    return round(.30*industry+.20*fleet+.20*req+.12*budget+.10*urgency+.08*authority,1)

def recalculate(lead, reason="Profile recalculation"):
    old=lead.dynamic_score
    fit=base_fit(lead)
    behavior=sum(EVENT_WEIGHTS.get(e.event_type,0) for e in lead.events.all())
    score=max(0,min(100,fit*.58+behavior))
    lead.fit_score=fit
    lead.dynamic_score=round(score,1)
    lead.conversion_probability=round(max(2,min(98,(score/100)**1.55*100)),1)
    if lead.converted: lead.stage="Converted"
    elif score>=80: lead.stage="Hot"
    elif score>=60: lead.stage="Warm"
    elif score>=40: lead.stage="Qualified"
    else: lead.stage="Cold"
    lead.next_best_action,lead.next_action_reason=next_best_action(lead)
    lead.save()
    if abs(old-lead.dynamic_score)>.01:
        LeadScoreHistory.objects.create(lead=lead,old_score=old,new_score=lead.dynamic_score,reason=reason)
    return lead

def next_best_action(lead):
    types=list(lead.events.values_list("event_type",flat=True))
    if "not_interested" in types: return "Move to nurture","Prospect indicated low current intent; avoid aggressive follow-up."
    if "quote" in types and lead.dynamic_score>=82: return "Call decision maker and close quotation","Quotation intent plus a high behavioural score signals purchase readiness."
    if lead.dynamic_score>=80 and "demo" not in types: return "Schedule fleet demo within 24 hours","High fit and engagement; product experience is the strongest next step."
    if lead.dynamic_score>=68 and "whatsapp_reply" in types: return "Share fleet pricing + ROI proposal","Prospect is responsive and ready for commercial value proof."
    if lead.dynamic_score>=58: return "Send personalized EV ROI calculator","Build business case using fuel savings, fleet size and payback."
    if lead.dynamic_score>=42: return "Send matched product brochure","Lead is qualified but needs product education before sales escalation."
    return "Research company and send personalized introduction","Low signal; enrich company and fleet context before spending sales time."

def add_event(lead,event_type):
    label=dict(EngagementEvent.TYPES).get(event_type,event_type)
    EngagementEvent.objects.create(lead=lead,event_type=event_type)
    return recalculate(lead,label)

def roi(lead):
    n=lead.estimated_ev_requirement
    km=lead.monthly_km_per_vehicle
    petrol=km/40*105
    electric=km/35*8
    monthly=max(0,(petrol-electric)*n)
    product=float(lead.recommended_product.price) if lead.recommended_product else 170000
    payback=(product*n/monthly) if monthly else 0
    return {"monthly_savings":round(monthly),"annual_savings":round(monthly*12),"payback_months":round(payback,1),"vehicles":n}
