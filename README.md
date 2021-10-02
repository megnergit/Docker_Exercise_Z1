# Docker Exercise Z1

## What the code does

   - It converts the prices in a table in various currencies to the prices in a desired currency.

   - The latest currency exchange rates are obtained from a website.

------------------------------------------------------------------
## How to run the code in a container

1. Clone GitHub repo.

2. `docker build . -t postgres`
   Create a docker image and name it `postgres`.

3. `docker run -d --name zep1 postgres`
   Create a container with a name `zep1`.

4. `docker exec -it zep1 python3 currency_conversion.py EUR [YOUR TOKEN]
   Run python script inside the container. Replace `[YOUR TOKEN]` with
   an access token you manually obtained at `http://api.exchangeratesapi.io`.
   The access token can be given with or without the parenthesis ("---"). 

or, in case you would like to keep the container interactive, 

4. `docker exec -it zep1 /bin/bash`
    and run
    `python3 currency_conversion.py EUR [YOUR TOKEN]`
    inside the container.

## Stop container
1. `docker stop zep1'

## Clean up
1. `docker rm zep1'

## Really Clean up

1. `docker image prune`
2. `docker volume prune`
3. `docker builder prune`


------------------------------------------------------------------
## Output

The first table is the current currency exchange rate obtained from
the internet, and the second table is the mock-up table with the new
prices in the last two columns.

```
[meg@elias ~/git4/docker]$ docker build . -t postgres
[+] Building 0.7s (13/13) FINISHED
 => [internal] load build definition from Dockerfile                   0.0s
 => => transferring dockerfile: 550B                                   0.0s
 => [internal] load .dockerignore                                      0.0s
 => => transferring context: 2B                                        0.0s
 => [internal] load metadata for docker.io/library/postgres:latest     0.5s
 => [1/8] FROM docker.io/library/postgres:latest@sha256:175ff61a978bc  0.0s
 => [internal] load build context                                      0.0s
 => => transferring context: 6.47kB                                    0.0s
 => CACHED [2/8] RUN apt-get update && apt-get -y install python3 pyt  0.0s
 => CACHED [3/8] RUN apt-get -y install postgresql-server-dev-10       0.0s
 => CACHED [4/8] RUN mkdir /zep                                        0.0s
 => CACHED [5/8] WORKDIR /zep                                          0.0s
 => CACHED [6/8] COPY requirements.txt /zep/                           0.0s
 => CACHED [7/8] RUN pip3 install -r requirements.txt                  0.0s
 => CACHED [8/8] COPY currency_conversion.py /zep/                     0.0s
 => exporting to image                                                 0.0s
 => => exporting layers                                                0.0s
 => => writing image sha256:de6e8337a72948992a30beb6ee32b9c87aed1892d  0.0s
 => => naming to docker.io/library/postgres                            0.0s

[meg@elias ~/git4/docker]$ docker image ls
REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
postgres     latest    de6e8337a729   2 minutes ago   872MB
[meg@elias ~/git4/docker]$ docker run -d --name zep1 postgres
37fde0f66fbcd5299146d05c4b3c3a0561b23705e83dc4f323183bad46a1989f

[meg@elias ~/git4/docker]$ docker ps
CONTAINER ID   IMAGE      COMMAND                  CREATED          STATUS         PORTS      NAMES
37fde0f66fbc   postgres   "docker-entrypoint.s…"   28 seconds ago   Up 3 seconds   5432/tcp   zep1
[meg@elias ~/git4/docker]$ docker exec -it zep1 python3 currency_conversion.py EUR [YOUR_TOKEN]
#=================================================================
  currency  success           timestamp base       date      rates
0      EUR     True 2021-10-02 07:34:03  EUR 2021-10-02   1.000000
1      RUB     True 2021-10-02 07:34:03  EUR 2021-10-02  84.267461
2      USD     True 2021-10-02 07:34:03  EUR 2021-10-02   1.159549
#=================================================================
# id type price currency new_price new_currency
  1 gueterzug     4000.00 RUB                          47.47 EUR
  2 nightliner     140.00 USD                         120.74 EUR
  3 ice            300.00 EUR                         300.00 EUR
```

Result when 'RUB' (Russian Ruble) is given as a desired currency. 

```
[meg@elias ~/git4/docker]$ docker exec -it zep1 python3 currency_conversion.py RUB [YOUR_TOKEN]
#=================================================================
  currency  success           timestamp base       date      rates
0      EUR     True 2021-10-02 07:34:03  EUR 2021-10-02   1.000000
1      RUB     True 2021-10-02 07:34:03  EUR 2021-10-02  84.267461
2      USD     True 2021-10-02 07:34:03  EUR 2021-10-02   1.159549
#=================================================================
# id type price currency new_price new_currency
  1 gueterzug     4000.00 RUB                        4000.00 RUB
  2 nightliner     140.00 USD                       10174.17 RUB
  3 ice            300.00 EUR                       25280.24 RUB


```

------------------------------------------------------------------

## Choice of Tech Stack

   1. Python `requests`.

      The alternative was a combination of `curl` and a shell
      script. `requests` is chosen, because it enables the whole code to fit
      in one python script. The downloaded data is also swiftly
      converted to pandas DataFrame from json without an overhead.

   2. Python `sqlalchemy`.

      The alternative was `peewee`. The use of `sqlalchemy` is one of
      the constraints externally set to the project (along with being
      on-premise and a containerized solution)

   3. PostgreSQL

      Possible choices are MySQL, SQLite, SQL server, MariaDB and cloud
      data warehouse such as BigQuery and Amazon
      Redshift. One of a few constraints given to the project is to
      close it on-premise. We used `psql` client of PostgreSQL in the
      prototype project which is without a container. It was simply 
      straightforward to continue with PostgreSQL.

   4. Python `pandas` and csv format

      Other possibilities are `datatable` and similar high-performance data
      format, or native SQL (= data manipulation will be done in
      a table in the RDBMS). A drawback of Python `pandas` and csv is
      its compromised speed. At the scale we are currently working, `pandas`
      will not make a significant bottleneck.
   
   5. Docker

      The alternative was `docker-compose`. `docker-compose` uses
      `docker-compose.yml` (in addition to `Dockerfile`) to configure
      multiple containers at once, and create a network between
      them. There are, however, parameters that can be set both in
      `docker-compose.yml` and 'Dockerfile` (e.g. port and
      environmental variables), which could lead unnoticed
      conflicts or update-errors (=we thought the parameters are
      updated, but they are not, because they are set in other
      configuration file as well). The simple combination of `docker` and
      `Dockerfile` is chosen to avoid it. The project is small
      enough to fit in a single container.


------------------------------------------------------------------
## How the code works

```
[meg@elias ~/git4/docker]$ \ls -1
Dockerfile
LICENSE
README.md
currency_conversion.py
requirements.txt
```

# currency_conversion.py

1. `get_current_rate()` : Collect the latest currency exchange rate from the website.
`exchangerateapi.io`. The data is acquired in json format, and will be
converted to pandas DataFrame. 

2. `create_mock_table()` : Create a price table whose prices are to be converted.
The mock-up table will be stored in postgreSQL server. 

3. `convert_currency()` : using the DataFrame of the currency exchange rates,
convert the prices in the mock-up table to the unit of the desired currency.
The updated table is stored in postgreSQL server using sqlalchemy.


# Dockerfile
```
# base image to create a container
FROM postgres:latest

# install python3
RUN apt-get update
RUN apt-get -y install python3 python3-pip
RUN apt-get -y install postgresql-server-dev-10

# create working directory
RUN mkdir -p /zep
WORKDIR /zep

# copy dependency list to install
COPY requirements.txt /zep/

# install dependency
RUN pip3 install -r requirements.txt

# change user -> removed 
# USER postgres

# environmental variables to be used for postgreSQL
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=PostgreSQL
ENV POSTGRES_DB=db_zeppelin

# copy python script
COPY currency_conversion.py /zep/
```



------------------------------------------------------------------
## Data Model

# Currency Exchange Rate Table

The latest information of the currency exchange rate.

- id: serial ID. Integer.
- currency : the currency whose value with respect to that of the base
             currency is presented.
- success : if the retrieval of the exchange rate is successfully acquired.
- timestamp : the time that the currency exchange rate is inquired and acquired.
- base : the base currency. The `rates` are shown as the value with respect 
  to the base currency.
- date : the date that the currency exchange rate is inquired and acquired.
- rates : the value of the currency with respect to the base currency. 


# Mock-up Table

A table of prices for 3 different trains with the unit of the price (=
currency).

- id : serial ID. Integer.
- type : type of train. String.
- price : price of the train. Float.
- currency : unit of the price. String of 3 characters.
- new_price : price converted into the desired currency.
- new_currency : the desired currency to show the price




------------------------------------------------------------------
## Review / To-do

1. Scheduling
   Using Spark Airflow. 

2. Split RDBMS and ETL for larger dataset. 
   By `docker-compose` or container orchestration.
   
3. Parallel processing for larger dataset.
   By using `pyspark`.



