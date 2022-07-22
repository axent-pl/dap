FROM postman/newman:5.3
COPY ./DAP.postman_collection.json /etc/newman/
COPY ./DAP.postman_environment.json /etc/newman/
COPY ./input.csv /etc/newman/

CMD [ "run", "DAP.postman_collection.json", "-e", "DAP.postman_environment.json" ]