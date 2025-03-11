# start by pulling the python image
FROM python:3.11-alpine


COPY ./requirements.txt /app/requirements.txt


WORKDIR /app


RUN pip install -r requirements.txt


COPY . /app

EXPOSE 8080


ENTRYPOINT [ "python" ]

CMD ["tms.py" ]