
if [ ! -d "venv" ]; then
    echo --------------------
    echo Creating virtualenv
    echo --------------------
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt 

export FLASK_APP=main.py
if [ ! -d "alembic" ]; then
    echo --------------------
    echo INIT THE alembic folder
    echo --------------------
    alembic init alembic
    export FLASK_APP=main.py;
fi
echo --------------------
echo Ready 4 initial data
echo --------------------