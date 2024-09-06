#!/bin/bash

control_c() {
	kill $DB_PID
	wait $DB_PID
	read -p "Do you want to clear cache? [Y/n]: " clear_cache
	if [[ $clear_cache != "n" && $clear_cache != "N" ]]; then
		rm -f data/database.db
	fi
	echo "exit successful"
	exit
}

trap control_c SIGINT

source .venv/bin/activate
cd utils/
tshark -V | python database.py &
DB_PID=$!
cd ../
python app.py

wait $DB_PID
