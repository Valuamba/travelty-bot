docker container rm -f $(docker container ps -a -q)
docker volume rm $(docker volume ls -q)
docker network rm $(docker network ls -q)
git
docker run -d -p 27017:27017  --name example-mongo  -e MONGODB_INITDB_ROOT_USERNAME=valuamba  -e MONGODB_INITDB_ROOT_PASSWORD=16zomole  mongo:latest