kubectl run deploy \
  --image=asia.gcr.io/dena-ai-training-16/lightgbm-clf:latest \
  --replicas=1 \
  --port=3000 \
  --limits=cpu=1000m \
  --command -- 40-predict.py
