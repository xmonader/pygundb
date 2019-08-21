run: 
	gunicorn -k flask_sockets.worker "test_server:build_app('$$gundb')"

doc:
	python3 -m pdoc gundb --html --output-dir docs/api --force

rungevent:
	python3 geventapp.py $$gundb

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
