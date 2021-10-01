# base image
FROM postgres:latest

# install python3
RUN apt-get update && apt-get -y install python3 python3-pip 
RUN apt-get -y install postgresql-server-dev-10

# create working directory
RUN mkdir /zep
WORKDIR /zep
COPY requirements.txt /zep/

# install dependency
RUN pip3 install -r requirements.txt

# change user
USER postgres

# environmental variable 
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=PostgreSQL
ENV POSTGRES_DB=db_zeppelin

# copy python code
COPY currency_conversion.py /zep/

# CMD ["pg_ctl", "-D", "/var/lib/postgresql/data", "-l",  "logfile",  "start"]
# CMD ["service", "postgresql", "start"]  
# CMD ["python3", "currency_conversion.py", "EUR", "36713a14ec549b80bded5bc3c14aab27"]
# RUN apt-get -y musl-dev
# RUN apt-get -y install python3 python3-pip python3-dev
# RUN apt-get -y install gcc
# VOLUME ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]
# EXPOSE 5432

