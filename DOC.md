`DELETA O BANCO`
docker container rm bybot-dbot-1 & docker volume rm bybot_pgdata
docker-compose up dbot


`Se modificar o SCOPES em gmail_auth.py, delete o token.json`


## Enviar arquivos para servidor
No diretorio Projects/
`scp -i bybot.pem ./mailbot/token.json ubuntu@<IP>:/home/ubuntu/mailbot/`
fazer isso com .env, credentials e token