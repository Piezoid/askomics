export VENV=~/env
virtualenv -p python3 $VENV
$VENV/bin/pip install -r requirements.txt
$VENV/bin/python setup.py develop
$VENV/bin/pserve development.ini

