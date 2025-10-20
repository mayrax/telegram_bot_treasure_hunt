from the conda environment of the telegram bot, these are the command to restart and run the bot application.

configuration if asked:
git config --global user.email "YOUR_EMAIL"
git config --global user.name "YOUR_USERNAME"

(docker must be open for this to work, and in the prompt you need to launch these script from the folder where there is the docker file, the requirement file and the python file).

1) building the docker image

docker build -t YOUR_NAME_TAG_IMAGE .


2) tagging the image

docker tag YOUR_NAME_TAG_IMAGE gcr.io/YOUR_GOOGLE_CLOUD_PROJECT
(YOUR_GOOGLE_CLOUD_PROJECT is the project id name that we created in google cloud console a.k.a google cloud platform)


3) pushing the image to the cloud 

docker push gcr.io/YOUR_GOOGLE_CLOUD_PROJECT


4) running the image/project

gcloud run deploy YOUR_NAME_TAG_IMAGE --image gcr.io/YOUR_GOOGLE_CLOUD_PROJECT --platform managed --region us-central1 --allow-unauthenticated


if there are any modification to the script you need to rerun all the scripts,
if the application is frozen just rerun the last script.


to stop the service:

gcloud run services delete telegram-bot --region us-central1


ENV VARIABLES IN GOOGLE CLOUD

in google could for the script to work environment variable must be set.
to set these environment variables in the google cloud console these are the steps that must be done:
go to cloud console menu -> "Cloud Run" -> "Services" -> click on telegram-bot -> "edit and deploy a new revision" -> staying on container -> "variables and secrets" 
here we put the variables to run and then we deploy a new revision, we have to do these if we stop the service.

TELEGRAM_BOT_TOKEN = this is the key given to us by the telegram when we create a bot via botFather.
CLOUD_RUN_SERVICE_URL = this is the path of our app in google cloud, we can find it here: "Cloud Run" -> "Services" -> click on telegram-bot
WEBHOOK_PATH = questo è l'endpoint del path che telegram chiamerà sul servizio di Cloud Run, non è obbligatorio ma è una buona pratica, questo lo si crea a piacere.


