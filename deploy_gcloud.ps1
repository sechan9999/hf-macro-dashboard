# Deploy Macro Pulse to Google Cloud Run using GCP project credits
$PROJECT_ID = "agentichackathon-506620"
$REGION = "us-central1"
$SERVICE_NAME = "macro-pulse"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " Deploying Macro Pulse to Google Cloud Run" -ForegroundColor Green
Write-Host " Project: $PROJECT_ID | Region: $REGION | Service: $SERVICE_NAME" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan

gcloud config set project $PROJECT_ID

gcloud run deploy $SERVICE_NAME `
  --source . `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --port 8080 `
  --memory 2Gi `
  --cpu 2 `
  --set-env-vars "GCP_PROJECT=$PROJECT_ID"

Write-Host "Deployment completed!" -ForegroundColor Green
