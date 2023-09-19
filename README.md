# praktikum_new_diplom
cd backend
python3 -m venv venv
source venv/bin/activate

python -m pip install django

django-admin startproject foodgram
python3 manage.py startapp users
pip freeze> requirements.txt
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python3 manage.py runserver
python3 manage.py createsuperuser
 docker-compose up --build
python manage.py show_urls