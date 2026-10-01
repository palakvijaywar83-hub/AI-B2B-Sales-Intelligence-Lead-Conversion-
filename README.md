# EVLeadAI – Agentic B2B EV Sales Intelligence

MVP for EV fleet B2B sales. The system demonstrates lead discovery, company research, product matching, personalized outreach, engagement tracking, dynamic lead scoring, follow-up and next-best-action.

## Run
```bash
python -m venv venv
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations sales
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Demo story
Open a lead and click engagement events such as Email Open, Pricing Click, WhatsApp Reply, Quotation Request and Demo Request. Every event creates a LeadScoreHistory row, recalculates the score, conversion probability and Next Best Action.

## Architecture
Discovery -> Research -> Product Match -> Personalization -> Engagement -> Dynamic Scoring -> Follow-up -> Next Best Action.

The demo uses deterministic explainable scoring and an ML-ready conversion service. `sales/ml/train_model.py` can train a RandomForest model after sufficient converted/not-converted data exists. If no model is present, Django safely uses the explainable score-derived probability.
