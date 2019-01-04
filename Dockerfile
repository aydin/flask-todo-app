FROM python:3.7-stretch

RUN useradd -ms /bin/bash todo

WORKDIR /home/todo

COPY requirements.txt requirements.txt
RUN python -m venv venv
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY app app
COPY todo.py config.py db.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP todo.py
ENV FLASK_ENV production
ENV SECRET_KEY secret-key
ENV JWT_SECRET_KEY jwt-secret-key


RUN chown -R todo:todo ./
USER todo

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]