## Required software:
Docker Desktop
## Start the Database
With docker desktop running in the background (Sign-in not required), Open a terminal in the docker folder of the project and
run: 
docker compose up

Username:SA
Password: IT7993!Scrappy
## Managing the Database
Once the container is running, it can be managed in Docker Desktop. The scrappymarket container will appear in the Docker Desktop dashboard where it can be:
- Started
- Stopped
- Restarted
- View logs
  
Stopping the container from Docker Desktop will stop the SQL Server without removing the container.
## Remove the Database
run: 
docker compose down
## Reset the Database
run:
docker compose down -v
docker compose up
