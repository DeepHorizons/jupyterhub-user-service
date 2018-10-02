FROM python:3.6

ENV PROJECT_DIR /srv/user-service
RUN pip install pipenv

ADD . $PROJECT_DIR/.

# TODO use gunicorn
CMD cd $PROJECT_DIR && run.sh
