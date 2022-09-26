docker container rm -f $(docker container ps -a -q)
docker volume rm $(docker volume ls -q)
docker network rm $(docker network ls -q)
git
docker run -d -p 27017:27017  --name example-mongo  -e MONGODB_INITDB_ROOT_USERNAME=valuamba  -e MONGODB_INITDB_ROOT_PASSWORD=16zomole  mongo:latest


docker run -itd -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=16zomole -e POSTGRES_DB=vpn-dion -p 45046:5432 postgres:13.3


docker run -itd -e POSTGRES_USER=s70416zomole -e POSTGRES_PASSWORD=16zomole -e POSTGRES_DB=travelty -p 5435:5432 --name travelty-pg postgres:13.3