from django.contrib import messages
from django.db.models import Avg,Count
from django.shortcuts import get_object_or_404,redirect,render
from .models import Lead,Product,Outreach
from .services import add_event,recalculate,roi
from .agents import research_lead,match_product,outreach_text

def dashboard(request):
    leads=Lead.objects.all()
    ctx={"total":leads.count(),"hot":leads.filter(stage="Hot").count(),"converted":leads.filter(converted=True).count(),"avg":round(leads.aggregate(v=Avg("dynamic_score"))["v"] or 0,1),"leads":leads.order_by("-dynamic_score")[:8],"stages":leads.values("stage").annotate(total=Count("id"))}
    return render(request,"dashboard.html",ctx)

def leads(request):
    q=request.GET.get("q","")
    qs=Lead.objects.select_related("recommended_product").order_by("-dynamic_score")
    if q: qs=qs.filter(company_name__icontains=q)
    return render(request,"leads.html",{"leads":qs,"q":q})

def lead_detail(request,pk):
    lead=get_object_or_404(Lead.objects.select_related("recommended_product"),pk=pk)
    return render(request,"lead_detail.html",{"lead":lead,"roi":roi(lead),"event_types":lead.events.model.TYPES,"history":lead.score_history.order_by("created_at")})

def event(request,pk,event_type):
    lead=get_object_or_404(Lead,pk=pk); add_event(lead,event_type); messages.success(request,f"Event recorded. Score is now {lead.dynamic_score}/100."); return redirect("lead_detail",pk=pk)

def run_agents(request,pk):
    lead=get_object_or_404(Lead,pk=pk)
    lead.research_summary=research_lead(lead)
    lead.recommended_product=match_product(lead,list(Product.objects.all()))
    lead.save(); recalculate(lead,"AI agents refreshed research and product fit")
    messages.success(request,"Research, product matching, scoring and next-best-action agents completed."); return redirect("lead_detail",pk=pk)

def outreach(request,pk):
    lead=get_object_or_404(Lead,pk=pk); r=roi(lead); subject,msg=outreach_text(lead,r); Outreach.objects.create(lead=lead,subject=subject,message=msg)
    return render(request,"outreach.html",{"lead":lead,"subject":subject,"message_text":msg})
