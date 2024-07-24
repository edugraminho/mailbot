`DELETA O BANCO`
docker container rm bybot-dbot-1 & docker volume rm bybot_pgdata
docker-compose up dbot


`Se modificar o SCOPES em gmail_auth.py, delete o token.json`