Proyecto de Data Engineering del curso Coder

- En este repositorio se encuentra un container de docker con lo necesario para levantar airflow y correr un ETL que obtiene los podcast del año 2024 de la api de spotify. Para levantarlo debe descargar las carpetas en este repositorio, luego abrir una terminal y luego correr los comandos: docker compose build, ejecutarlo, docker compose up y con eso ya estaria corriendo. 
Es importante tener docker desktop abierto antes de correr los comandos. 

- Es necesario que tengan su clave de la api de spotify junto con su secret para poder gestionarlo. Tambien deberian tener su claves de acceso a amazon redshift y lo deberian gestionar en las configuraciones de airflow una vez que se levanto el container. 

- Aclaracion: se agrego la instalacion del modulo spotipy dentro del docker yaml que contiene el airflow