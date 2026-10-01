from django.contrib import messages
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import Lead, Product, Outreach
from .services import add_event, recalculate, roi
from .agents import research_lead, match_product, outreach_text


# ============================================================
# DASHBOARD
# ============================================================

def dashboard(request):

    leads = Lead.objects.all()

    ctx = {
        "total": leads.count(),

        "hot": leads.filter(
            stage="Hot"
        ).count(),

        "converted": leads.filter(
            converted=True
        ).count(),

        "avg": round(
            leads.aggregate(
                v=Avg("dynamic_score")
            )["v"] or 0,
            1
        ),

        "leads": leads.order_by(
            "-dynamic_score"
        )[:8],

        "stages": leads.values(
            "stage"
        ).annotate(
            total=Count("id")
        ),
    }

    return render(
        request,
        "dashboard.html",
        ctx
    )


# ============================================================
# ALL LEADS
# ============================================================

def leads(request):

    q = request.GET.get(
        "q",
        ""
    ).strip()

    stage = request.GET.get(
        "stage",
        ""
    ).strip()

    qs = Lead.objects.select_related(
        "recommended_product"
    ).order_by(
        "-dynamic_score"
    )

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if q:

        qs = qs.filter(
            Q(company_name__icontains=q) |
            Q(industry__icontains=q) |
            Q(city__icontains=q)
        )

    # --------------------------------------------------------
    # STAGE FILTER
    # --------------------------------------------------------

    if stage:

        qs = qs.filter(
            stage__iexact=stage
        )

    return render(
        request,
        "leads.html",
        {
            "leads": qs,
            "q": q,
            "stage": stage,
        }
    )


# ============================================================
# HIGH INTENT LEADS
# ============================================================

def high_intent_leads(request):
    """
    Shows leads that have reached strong buying intent.

    A lead is considered High Intent when:
    1. Its stage is Hot
       OR
    2. Dynamic Lead Score is >= 80
    """

    leads_qs = Lead.objects.select_related(
        "recommended_product"
    ).filter(
        Q(stage__iexact="Hot") |
        Q(dynamic_score__gte=80)
    ).order_by(
        "-dynamic_score"
    )

    average_score = round(
        leads_qs.aggregate(
            value=Avg("dynamic_score")
        )["value"] or 0,
        1
    )

    context = {
        "leads": leads_qs,
        "total_high_intent": leads_qs.count(),
        "average_score": average_score,
    }

    return render(
        request,
        "high_intent_leads.html",
        context
    )


# ============================================================
# AI RECOMMENDATIONS
# ============================================================

def recommendations(request):
    """
    Consolidated Next-Best-Action intelligence screen.

    Leads are ranked according to the current Dynamic Lead Score.
    """

    leads_qs = Lead.objects.select_related(
        "recommended_product"
    ).order_by(
        "-dynamic_score"
    )

    total_leads = leads_qs.count()

    hot_leads = leads_qs.filter(
        stage__iexact="Hot"
    ).count()

    avg_score = round(
        leads_qs.aggregate(
            value=Avg("dynamic_score")
        )["value"] or 0,
        1
    )

    high_priority = leads_qs.filter(
        dynamic_score__gte=80
    ).count()

    context = {
        "leads": leads_qs,
        "total_leads": total_leads,
        "hot_leads": hot_leads,
        "avg_score": avg_score,
        "high_priority": high_priority,
    }

    return render(
        request,
        "recommendations.html",
        context
    )


# ============================================================
# PRODUCT MATCHING
# ============================================================

def product_matching(request):
    """
    Displays the EV selected for each B2B prospect by the
    Product Matching Agent.
    """

    leads_qs = Lead.objects.select_related(
        "recommended_product"
    ).order_by(
        "-dynamic_score"
    )

    matched_count = leads_qs.filter(
        recommended_product__isnull=False
    ).count()

    unmatched_count = leads_qs.filter(
        recommended_product__isnull=True
    ).count()

    total_leads = leads_qs.count()

    match_percentage = 0

    if total_leads > 0:

        match_percentage = round(
            (matched_count / total_leads) * 100,
            1
        )

    context = {
        "leads": leads_qs,
        "matched_count": matched_count,
        "unmatched_count": unmatched_count,
        "total_leads": total_leads,
        "match_percentage": match_percentage,
    }

    return render(
        request,
        "product_matching.html",
        context
    )


# ============================================================
# DYNAMIC SCORING
# ============================================================

def dynamic_scoring(request):
    """
    Behaviour-driven Dynamic Lead Scoring monitor.

    Leads are automatically ranked according to their latest
    customer behaviour and intelligence score.
    """

    leads_qs = Lead.objects.select_related(
        "recommended_product"
    ).order_by(
        "-dynamic_score"
    )

    average_score = round(
        leads_qs.aggregate(
            value=Avg("dynamic_score")
        )["value"] or 0,
        1
    )

    high_intent_count = leads_qs.filter(
        dynamic_score__gte=80
    ).count()

    warm_count = leads_qs.filter(
        dynamic_score__gte=60,
        dynamic_score__lt=80
    ).count()

    qualified_count = leads_qs.filter(
        dynamic_score__gte=40,
        dynamic_score__lt=60
    ).count()

    nurture_count = leads_qs.filter(
        dynamic_score__lt=40
    ).count()

    context = {
        "leads": leads_qs,
        "average_score": average_score,
        "high_intent_count": high_intent_count,
        "warm_count": warm_count,
        "qualified_count": qualified_count,
        "nurture_count": nurture_count,
        "total_leads": leads_qs.count(),
    }

    return render(
        request,
        "dynamic_scoring.html",
        context
    )


# ============================================================
# AGENTIC AI CONTROL CENTER
# ============================================================

def agentic_ai(request):
    """
    Central orchestration screen for EVLeadAI.

    Shows the eight specialized AI agents and allows the user
    to execute the AI pipeline against an individual lead.
    """

    leads_qs = Lead.objects.select_related(
        "recommended_product"
    ).order_by(
        "-dynamic_score"
    )

    # --------------------------------------------------------
    # 8 AGENT DEFINITIONS
    # --------------------------------------------------------

    agents = [

        {
            "number": "01",
            "name": "Lead Discovery Agent",
            "short_name": "Discovery",
            "icon": "fa-magnifying-glass",
            "status": "Operational",
            "description":
                "Identifies potential B2B organizations that may "
                "require electric vehicles for fleet operations.",
        },

        {
            "number": "02",
            "name": "Company Research Agent",
            "short_name": "Research",
            "icon": "fa-building",
            "status": "Operational",
            "description":
                "Analyzes company context, fleet profile and "
                "potential EV requirements.",
        },

        {
            "number": "03",
            "name": "Product Matching Agent",
            "short_name": "Product Match",
            "icon": "fa-cubes",
            "status": "Operational",
            "description":
                "Matches fleet requirements, usage and budget "
                "with the most suitable EV product.",
        },

        {
            "number": "04",
            "name": "Personalization Agent",
            "short_name": "Personalization",
            "icon": "fa-envelope",
            "status": "Operational",
            "description":
                "Generates prospect-specific outreach using "
                "company, requirement, product and ROI context.",
        },

        {
            "number": "05",
            "name": "Engagement Agent",
            "short_name": "Engagement",
            "icon": "fa-satellite-dish",
            "status": "Operational",
            "description":
                "Processes customer interaction signals such as "
                "email opens, clicks, replies and requests.",
        },

        {
            "number": "06",
            "name": "Dynamic Scoring Agent",
            "short_name": "Dynamic Score",
            "icon": "fa-chart-line",
            "status": "Operational",
            "description":
                "Continuously recalculates lead priority when "
                "customer behaviour changes.",
        },

        {
            "number": "07",
            "name": "Follow-up Agent",
            "short_name": "Follow-up",
            "icon": "fa-rotate",
            "status": "Operational",
            "description":
                "Determines when the sales team should re-engage "
                "a prospect based on current lead state.",
        },

        {
            "number": "08",
            "name": "Next-Best-Action Agent",
            "short_name": "Next Best Action",
            "icon": "fa-bolt",
            "status": "Operational",
            "description":
                "Converts the latest intelligence into the most "
                "appropriate recommended sales action.",
        },

    ]

    # --------------------------------------------------------
    # CONTROL CENTER STATISTICS
    # --------------------------------------------------------

    total_leads = leads_qs.count()

    hot_leads = leads_qs.filter(
        Q(stage__iexact="Hot") |
        Q(dynamic_score__gte=80)
    ).count()

    matched_leads = leads_qs.filter(
        recommended_product__isnull=False
    ).count()

    avg_score = round(
        leads_qs.aggregate(
            value=Avg("dynamic_score")
        )["value"] or 0,
        1
    )

    converted_leads = leads_qs.filter(
        converted=True
    ).count()

    context = {

        "agents": agents,

        "total_agents": len(agents),

        "leads": leads_qs,

        "total_leads": total_leads,

        "hot_leads": hot_leads,

        "matched_leads": matched_leads,

        "avg_score": avg_score,

        "converted_leads": converted_leads,

    }

    return render(
        request,
        "agentic_ai.html",
        context
    )


# ============================================================
# LEAD 360° DETAIL
# ============================================================

def lead_detail(request, pk):

    lead = get_object_or_404(
        Lead.objects.select_related(
            "recommended_product"
        ),
        pk=pk
    )

    context = {

        "lead": lead,

        "roi": roi(lead),

        "event_types":
            lead.events.model.TYPES,

        "history":
            lead.score_history.order_by(
                "created_at"
            ),
    }

    return render(
        request,
        "lead_detail.html",
        context
    )


# ============================================================
# ENGAGEMENT EVENT
# ============================================================

def event(request, pk, event_type):

    lead = get_object_or_404(
        Lead,
        pk=pk
    )

    # --------------------------------------------------------
    # RECORD CUSTOMER BEHAVIOUR
    # --------------------------------------------------------

    add_event(
        lead,
        event_type
    )

    # Reload the updated score from database.
    lead.refresh_from_db()

    messages.success(
        request,
        (
            f"Customer behaviour recorded. "
            f"Dynamic Lead Score is now "
            f"{lead.dynamic_score}/100."
        )
    )

    return redirect(
        "lead_detail",
        pk=pk
    )


# ============================================================
# RUN AGENTIC AI PIPELINE
# ============================================================

def run_agents(request, pk):
    """
    Executes the available AI pipeline against one lead.

    Current implementation:
        1. Company Research
        2. Product Matching
        3. Dynamic Scoring
        4. Next-Best-Action refresh

    Personalization remains available through the outreach view.
    Engagement changes are handled through the event endpoint.
    """

    lead = get_object_or_404(
        Lead,
        pk=pk
    )

    # --------------------------------------------------------
    # 1. COMPANY RESEARCH AGENT
    # --------------------------------------------------------

    lead.research_summary = research_lead(
        lead
    )


    # --------------------------------------------------------
    # 2. PRODUCT MATCHING AGENT
    # --------------------------------------------------------

    products = list(
        Product.objects.all()
    )

    lead.recommended_product = match_product(
        lead,
        products
    )

    lead.save()


    # --------------------------------------------------------
    # 3. DYNAMIC SCORING AGENT
    # 4. NEXT-BEST-ACTION AGENT
    # --------------------------------------------------------

    recalculate(
        lead,
        "Agentic AI refreshed research, product fit and lead intelligence"
    )


    # --------------------------------------------------------
    # REFRESH UPDATED DATABASE VALUES
    # --------------------------------------------------------

    lead.refresh_from_db()


    # --------------------------------------------------------
    # SUCCESS MESSAGE
    # --------------------------------------------------------

    messages.success(
        request,
        (
            "Agentic AI pipeline completed for "
            f"{lead.company_name}. "
            "Research, Product Matching, Dynamic Scoring "
            "and Next-Best-Action have been refreshed."
        )
    )


    return redirect(
        "lead_detail",
        pk=pk
    )


# ============================================================
# PERSONALIZED OUTREACH
# ============================================================

def outreach(request, pk):
    """
    Generates prospect-specific outreach using lead intelligence,
    product recommendation and ROI information.
    """

    lead = get_object_or_404(
        Lead.objects.select_related(
            "recommended_product"
        ),
        pk=pk
    )


    # --------------------------------------------------------
    # ROI INTELLIGENCE
    # --------------------------------------------------------

    roi_data = roi(
        lead
    )


    # --------------------------------------------------------
    # PERSONALIZATION AGENT
    # --------------------------------------------------------

    subject, msg = outreach_text(
        lead,
        roi_data
    )


    # --------------------------------------------------------
    # STORE GENERATED OUTREACH
    # --------------------------------------------------------

    Outreach.objects.create(
        lead=lead,
        subject=subject,
        message=msg
    )


    context = {

        "lead": lead,

        "subject": subject,

        "message_text": msg,

        "roi": roi_data,

    }


    return render(
        request,
        "outreach.html",
        context
    )