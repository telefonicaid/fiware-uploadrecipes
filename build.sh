virtualenv ENV
source ENV/bin/activate
pip install -r requirements.txt

python manage.py syncdb

python manage.py test recipes --settings=settings.jenkins 

