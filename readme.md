# Telegram Bot API

## Description
This project is a chatbot application that uses Google's Generative AI (Gemini) to generate responses. It is built with Python and uses Flask for the web server. The chatbot can be interacted with via a Telegram bot.


## Installation
1. Clone the repository
2. Install the required packages using `pip install -r requirements.txt`
3. Set up the Telegram bot using the BotFather on Telegram
4. Create a `.env` file in the 'functions' directory and add the required environment variables.
5. Deploy the firebase functions using `firebase deploy --only functions`. More details on firebase documentation [here](https://firebase.google.com/docs/functions/get-started?gen=2nd#python_1)
6. Bind the firebase function URL by setting a telegram webhook using the following URL: `https://<your-project-id>.firebaseapp.com/webhook`. More details on telegram documentation [here](https://core.telegram.org/bots/api#setwebhook)

## Environment Variables
The following environment variables are required for the application to run:
   
   | Variable          | Description                               | Default Value |
   |-------------------|-------------------------------------------|---------------|
   | `GEMINI_API_KEY`  | Your Gemini API key                       | None          |

## Project Progress
This section tracks the progress of the project. The following features are planned or have been implemented:

- [x] Implement Gemini model
- [x] Implement a basic plugin
- [x] Implement DateTimePlugin
- [ ] Implement gemini vision api, to recognize images
- [ ] Chat history mode
- [ ] Implement other plugins (e.g. weather, stock, etc.)
- [ ] Setup Continuous Delivery
- [ ] Setup the new Gemini 1.5 models