# Telegram Bot API

## Description
This project is a chatbot application that uses Google's Generative AI (Gemini) to generate responses. It is built with Python and uses Flask for the web server. The chatbot can be interacted with via a Telegram bot.


## Installation
1. Set up the Telegram bot using the BotFather on Telegram
2. Deploy on vercel with just a click [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/benincasantonio/gemini-ai-telegram-bot)

## Environment Variables
The following environment variables are required for the application to run:

   | Variable             | Description                               | Default Value |
   |----------------------|-------------------------------------------|---------------|
   | `GEMINI_API_KEY`     | Your Gemini API key                       | None          |
   | `TELEGRAM_BOT_TOKEN` | Your Telegram Bot token                   | None          |
   | `OWM_API_KEY`        | Your [Open Weather Map](https://openweathermap.org/api) API Key             | None          |
   
## Project Progress
This section tracks the progress of the project. The following features are planned or have been implemented:

- [x] Implement Gemini model
- [x] Implement a basic plugin
- [x] Implement DateTimePlugin
- [x] Implement gemini vision api, to recognize images
- [ ] Chat history mode
- [x] Implement other plugins (e.g. weather, stock, etc.)
- [x] Setup Continuous Delivery
- [ ] Http certificate to secure the webhook endpoint
- [ ] Make it work in telegram groups