from pathlib import Path
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score,precision_score,recall_score,roc_auc_score

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/"models"/"landslide_model.joblib"
rng=np.random.default_rng(42); n=5000
rain24=rng.gamma(2.4,35,n).clip(0,220); rain72=(rain24+rng.gamma(4,45,n)).clip(0,550)
soil=rng.normal(62,18,n).clip(15,100); slope=rng.normal(32,13,n).clip(5,70); elev=rng.normal(1100,700,n).clip(50,4500)
ndvi=rng.normal(.46,.14,n).clip(.15,.85); hist=rng.normal(40,25,n).clip(0,100)
eqm=rng.normal(0,1.1,n).clip(0,7.5); eqd=rng.uniform(5,500,n); eqdepth=rng.uniform(1,200,n)
logit=-7+0.018*rain24+0.006*rain72+0.035*soil+0.055*slope+0.018*hist-2.2*ndvi+0.45*eqm-0.0018*eqd
prob=1/(1+np.exp(-logit)); y=(rng.random(n)<prob).astype(int)
X=np.column_stack([rain24,rain72,soil,slope,elev,ndvi,hist,eqm,eqd,eqdepth])
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
model=RandomForestClassifier(n_estimators=300,max_depth=12,min_samples_leaf=3,class_weight="balanced",random_state=42,n_jobs=-1).fit(Xtr,ytr)
p=model.predict_proba(Xte)[:,1]; pred=(p>=.5).astype(int)
metrics={"accuracy":accuracy_score(yte,pred),"precision":precision_score(yte,pred,zero_division=0),"recall":recall_score(yte,pred,zero_division=0),"roc_auc":roc_auc_score(yte,p)}
OUT.parent.mkdir(exist_ok=True); joblib.dump({"model":model,"metrics":metrics,"features":["rainfall24h","rainfall72h","soilMoisture","slope","elevation","ndvi","historicalDensity","earthquakeMagnitude","earthquakeDistanceKm","earthquakeDepthKm"],"training":"synthetic demonstration data; replace with validated NER data"},OUT)
print("Saved",OUT); print(metrics)
