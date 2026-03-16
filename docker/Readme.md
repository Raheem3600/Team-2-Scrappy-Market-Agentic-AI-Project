## Required software:
Docker Desktop
## Start the Database
With docker desktop running in the background (Sign-in not required), Open a terminal in the docker folder of the project and
run: 
docker compose up
## Stop the Database
run: 
docker compose down
## Reset the Database
run:
docker compose down -v
docker compose up
