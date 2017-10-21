FROM python:3.6

WORKDIR /server
COPY /server /server
COPY cmd.sh /

RUN pip install -r /server/requirements.txt
RUN ["chmod", "+x", "/cmd.sh"]

ENV TZ=America/Recife
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

EXPOSE 80

CMD ["/cmd.sh"]

