from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.model_selection import train_test_split
import pandas as pd
import pickle
import cdsw
import os
import requests
import json

HOST = "http://" + os.environ['CDSW_DOMAIN']
USERNAME = "jfletcher"
API_KEY = "ubl2cr004czgh94dcz2t4dpjft03gpsh"
PROJECT_NAME = "cc-fraud-demo-model-testing"
JOB_ID = "10"
NEW_DAY = int(os.environ['DAY'])

url = "/".join([HOST, "api/v1/projects", USERNAME, PROJECT_NAME, "jobs", JOB_ID, "start"])
job_params = {"DAY": str(NEW_DAY)}



cc_data = pd.read_pickle("resources/credit_card_dataframe_final.pkl",compression="gzip")


X = cc_data[cc_data.Day == NEW_DAY].iloc[:,3:len(cc_data.columns)-1]
y = cc_data[cc_data.Day == NEW_DAY].iloc[:,len(cc_data.columns)-1]

X_train, X_test, y_train, y_test = train_test_split(
  X, y, test_size=0.3, random_state=42
)

randF = pickle.load(open("cc_model_day_3.pkl","rb"))

predictions_rand=randF.predict(X_test)
auroc = roc_auc_score(y_test, predictions_rand)
ap = average_precision_score(y_test, predictions_rand)

print("auroc =",auroc)
print("ap =",ap)

if auroc < 0.9:
  print("model needs retraining")
  res = requests.post(
    url,
    headers = {"Content-Type": "application/json"},
    auth = (API_KEY,""),
    data = json.dumps({"environment": job_params})
  )
  print("URL", url)
  print("HTTP status code", res.status_code)
  print("Engine ID", res.json().get('engine_id'))
else:
  print("model is fine")