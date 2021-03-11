.PHONY: virtualenv localssl deploy

virtualenv:
	python3 -m venv ./env && ./env/bin/pip install -r requirements.txt

localssl: localssl
	openssl genrsa -aes256 -passout pass:gsahdg -out server.pass.key 4096 && openssl rsa -passin pass:gsahdg -in server.pass.key -out server.key && rm server.pass.key && openssl req -new -key server.key -out server.csr && openssl x509 -req -sha256 -days 365 -in server.csr -signkey server.key -out server.crt

deploy: deploy
	git pull origin master && sudo systemctl restart bhaa
