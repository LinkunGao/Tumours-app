@echo off
cls
type logo.txt
echo Starting Tumours Segmentation GUI App...
echo.
cd C:\Users\lgao142\Desktop\Tumours-app
docker-compose -f docker-compose.yml up