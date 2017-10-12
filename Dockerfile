FROM python:3.6

WORKDIR /app
COPY /app /app
COPY cmd.sh /

RUN pip install -r /app/requirements.txt
RUN ["chmod", "+x", "/cmd.sh"]

EXPOSE 80

CMD ["/cmd.sh"]

