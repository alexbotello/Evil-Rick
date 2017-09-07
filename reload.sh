docker rmi $"(docker images -f dangling=true -q)"
docker-compose build
docker-compose up