FROM python:3.6-slim 

COPY ./dags/create_tables.py ./
COPY ./dags/models.py ./

RUN pip install sqlalchemy==1.4.26
RUN pip install psycopg2-binary==2.9.1

CMD python create_tables.py