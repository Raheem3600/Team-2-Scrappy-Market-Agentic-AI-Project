# Team-2-Scrappy-Market-Agentic-AI-Project

## Requirements

- Docker Desktop installed and running
- Ollama installed locally
- `llama3` pulled in Ollama

## First-Time Setup

1. Open a terminal.
2. Start Ollama on your computer.
3. Run `ollama pull llama3`.

## Start the Application

1. Open a terminal in the project folder.
2. If needed, create the local environment file by running `Copy-Item .env.example .env`.
3. Start the containers by running `docker compose up --build`.

## What Starts

- SQL Server database container
- Backend container
- Investigator container
- UI container

## Open the App

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Stop the Application

Run `docker compose down --remove-orphans` in the project folder.

## Notes

- Ollama runs locally on the host machine and is not inside Docker.
- The first Docker startup may take a few minutes while containers build.
