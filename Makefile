make:
	docker build --progress=plain -t cronchoco .
	docker run -d -v ${CURDIR}:/app cronchoco bash -c "crontab /app/cronchoco/crontab && cron -f"

shell:
	docker exec -it `docker ps -aqf "ancestor=cronchoco"` bash

	
down:
	-docker stop `docker ps -aqf "ancestor=cronchoco"`
	-docker rm `docker ps -aqf "ancestor=cronchoco"`

logs:
	docker logs  --follow `docker ps -aqf "ancestor=cronchoco"`