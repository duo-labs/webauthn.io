# Using Dart-sass CLI from https://sass-lang.com/install
./sass-1.50.1 _app/homepage/static/scss/index.scss _app/homepage/static/css/index.css
docker compose run django ./manage.py collectstatic --no-input
