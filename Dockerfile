FROM python:3.9



RUN pip install pandas
RUN pip install spotipy
RUN pip install sendgrid
RUN pip install psycopg2