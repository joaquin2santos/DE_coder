from datetime import timedelta,datetime
from pathlib import Path
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import os
from  Extract import extraer_data, conexion_db, cargar_datos
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

dag_path = os.getcwd()
default_args = {
    'start_date': datetime(2023, 6, 20),
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

ingestion_dag = DAG(
    dag_id='ingestar_data',
    default_args=default_args,
    description='Recopila datos de los podcast de  spotify en 2024',
    schedule_interval=timedelta(days=1),
    catchup=False
)

#tarea 1, conectar a la api y tranformar la info, retonrna un diccionario
task_1 = PythonOperator(
    task_id='extraer_data',
    python_callable=extraer_data,
    dag=ingestion_dag,
)

#tarea 2 conecta a amazon redshift y crea la base de datos
task_2 = PythonOperator(
    task_id='conectar_redshift',
    python_callable=conexion_db,
    dag=ingestion_dag,
)

# tarea 3 carga la info en la tabla de redshift
task_3 = PythonOperator(
    task_id='cargar_data',
    python_callable=cargar_datos,
    dag=ingestion_dag,
)





task_1 >> task_2 >> task_3