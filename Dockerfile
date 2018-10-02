FROM python:3.6

ENV PROJECT_DIR /srv/user-service
RUN pip install pipenv

ADD . $PROJECT_DIR/.

RUN cd $PROJECT_DIR && \
    pipenv install

# TODO use gunicorn
CMD cd $PROJECT_DIR/user-service && pipenv run python app.py
