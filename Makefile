run: 
	gunicorn -k flask_sockets.worker app:app

rungevent:
	python3 geventapp.py

clientall: clientdummy clientmem clientredis clientudb clientpickle

clientdummy:
	python3 testclient.py dummy

clientredis:
	python3 testclient.py redis

clientmem:
	python3 testclient.py memory

clientudb:
	python3 testclient.py udb

clientpickle:
	python3 testclient.py pickle