FROM python:3.6

COPY /app /app
COPY cmd.sh /

RUN pip install -r /app/requirements.txt

CMD ["/cmd.sh"]