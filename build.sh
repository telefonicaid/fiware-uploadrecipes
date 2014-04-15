# File to execute the covertura and unit test and generate the information
# 
#to be shown in sonar
#
# __author__ = 'henar'


virtualenv ENV
source ENV/bin/activate
pip install -r requirements.txt

python manage.py syncdb

python manage.py test --settings=settings.jenkins deactivate

