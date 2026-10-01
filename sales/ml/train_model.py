# Optional ML trainer: run after you accumulate labelled lead outcomes.
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
FEATURES=["fit_score","dynamic_score","employee_count","existing_fleet_size","estimated_ev_requirement","monthly_km_per_vehicle"]
def train(csv_path, output="sales/ml/conversion_model.joblib"):
    df=pd.read_csv(csv_path).dropna(subset=FEATURES+["converted"])
    X=df[FEATURES]; y=df["converted"].astype(int)
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
    model=RandomForestClassifier(n_estimators=250,class_weight="balanced",random_state=42).fit(Xtr,ytr)
    print(classification_report(yte,model.predict(Xte)))
    joblib.dump(model,output)
    return model
