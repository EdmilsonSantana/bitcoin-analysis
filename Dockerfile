FROM python:3.6

WORKDIR /app
COPY /app /app
COPY cmd.sh /

RUN pip install -r /app/requirements.txt
RUN ["chmod", "+x", "/cmd.sh"]

ENV TZ=America/Recife
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

EXPOSE 80

CMD ["/cmd.sh"]

