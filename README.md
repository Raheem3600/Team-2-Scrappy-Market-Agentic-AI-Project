# Team-2-Scrappy-Market-Agentic-AI-Project

## Requirements

- Docker Desktop installed and running
- Ollama installed locally
- `llama3` pulled in Ollama

## First-Time Setup

1. Open a local terminal such as PowerShell or Command Prompt.
2. Start Ollama on your computer.
3. In the terminal, run `ollama pull llama3` to download the local AI model used by the project.
4. Confirm that Ollama is still running before starting Docker.

## Start the Application

1. Open a terminal in the project folder:
   `Team-2-Scrappy-Market-Agentic-AI-Project-main`
2. Create the local environment file by running `Copy-Item .env.example .env`.
3. Start the containers by running `docker compose up --build`.
4. Wait for the database, backend, investigator, and UI containers to finish starting.

## What Starts

- SQL Server database container
- Backend container
- Investigator container
- UI container

## Open the App

Open [http://localhost:8501](http://localhost:8501) in your browser.

The application services use these ports:

- `1433` - SQL Server
- `8000` - backend API
- `9000` - investigator/orchestrator
- `8501` - Streamlit UI

## Stop the Application

Run `docker compose down --remove-orphans` in the project folder.

## Notes

- Ollama runs locally on the host machine and is not inside Docker.
- The first Docker startup may take a few minutes while containers build.
- The first database startup may also take a short time while initialization scripts run.
- If one of the ports above is already in use, Docker may fail to start until that conflict is removed.
- If you change any values in `.env`, restart the stack with `docker compose up --build`.
- Local hardware limits may affect performance. The Ollama model can use at least 5 GB of memory by itself, and the Docker containers also require additional system memory and disk space while running.
- On lower-spec machines, startup and response times may be slower because Ollama, SQL Server, and the application containers are all sharing local resources.
