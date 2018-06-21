kubectl run deploy3 \
  --image=asia.gcr.io/dena-ai-training-16/nodejs:1.0  \
  --replicas=1 \
  --port=3000 \
  --limits=cpu=100m \
  --command -- node app/server.js
