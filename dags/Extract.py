#importar librerias
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import datetime
from sqlalchemy import create_engine
import json
import psycopg2
from psycopg2.extras import execute_values
from airflow.models import  Variable
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# cargar el archivo JSON con las claves
#with open(r'C:\Users\BANGHO\Desktop\botsito\accesos_coderhouse.json','r') as f:
 #   datos = json.load(f)
#claves
secret = Variable.get('secret')
id_client = Variable.get('id_client')
usuario = Variable.get('usuario')
contraseña_bd = Variable.get('pasword')
host = Variable.get('host')
database = Variable.get('database')

sender_email = Variable.get("gmail_user")
password= Variable.get("gmail_key")
sender_email = Variable.get("gmail_user")
smtp_server = Variable.get("smtp_server")
smtp_port = 587


conn = psycopg2.connect(
            host=host,
            dbname=database,
            user=usuario,
            password=contraseña_bd,
            port='5439'
        )
def extraer_data():
    #crear llamada a la api
    client_credentials_manager= SpotifyClientCredentials(client_id=id_client, client_secret= secret)
    sp= spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    #buscar la info en la api
    busqueda = sp.search(q='podcast 2024', type='track', limit=50) 
    #variable con la fecha de extraccion
    now = datetime.date.today().strftime('%Y-%m-%d')
    #columnas para guardar la info 
    columnas = {'Id': [],'Artista': [], 'Podcast': [],'Duracion': [], 'Genero': [],'Album': [], 'Album_img': [], 'Episodios': [], 'Popularidad': [], 'Fecha_Lanzamiento': [],'Fecha_Modificacion': []}
    #acceder a la info
    for track in busqueda['tracks']['items']:
        id = track['id']
        artist_name = track['artists'][0]['name']
        artist_id = track['artists'][0]['id']
        track_name = track['name']
        duration = track['duration_ms']
        track_id = track['id']
        album_group = track['album']['name']
        album_img = track['album']['images'][0]['url'] 
        album_cont = track['album']['total_tracks']
        track_genre =track.get("genres")
        track_popularity = track['popularity']
        track_year = track['album']['release_date']
        #sacar las comillas 
        track_name = track_name.replace("'", "")
        album_group = album_group.replace("'", "")
        columnas['Id'].append(id)
        columnas['Artista'].append(artist_name)
        columnas['Podcast'].append(track_name)
        columnas['Duracion'].append(duration)
        columnas['Album'].append(album_group)
        columnas['Album_img'].append(album_img)
        columnas['Episodios'].append(album_cont)
        columnas['Genero'].append(track_genre)
        columnas['Popularidad'].append(track_popularity)
        columnas['Fecha_Lanzamiento'].append(track_year)
        columnas['Fecha_Modificacion'].append(now)

    #crear el dataframe
    df = pd.DataFrame(columnas)
    #sacar duplicadas
    df.drop_duplicates(subset=['Artista', 'Podcast','Album'], keep='first', inplace=True)
    #llenar los nulos que no tenemos info
    df['Genero'].fillna('Sin Dato', inplace=True)
    df['Genero'].replace('', 'Sin Dato', inplace=True)

    #filtrar para cargar solo valores positivos en la duracion
    df = df.query('Duracion > 0')
    #chequear los formatos de fecha 
    df['Fecha_Lanzamiento'] = pd.to_datetime(df['Fecha_Lanzamiento'], format='%Y-%m-%d')
    df['Fecha_Lanzamiento'] = df['Fecha_Lanzamiento'].dt.strftime('%Y-%m-%d')
    df=df.to_dict()

    return df

def conexion_db():
        # conexion a redshift
    try:
        conn = psycopg2.connect(
            host=host,
            dbname=database,
            user=usuario,
            password=contraseña_bd,
            port='5439'
        )
        print("Conectado a Redshift con éxito!")
        
    except Exception as e:
        print("No es posible conectar a Redshift")
        print(e)
        
    #crear la tabla si no existe
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS joaquintwosantos_coderhouse.podcast_2024
            (
            Id VARCHAR(50) primary key  
            ,Artista VARCHAR(255)   
            ,Podcast VARCHAR(255)  
            ,Duracion INTEGER
            ,Genero VARCHAR(300)   
            ,Album VARCHAR(100)
            ,Album_img  VARCHAR(100)
            ,Episodios INTEGER  
            ,Popularidad INTEGER 
            ,Fecha_Lanzamiento date   
            ,Fecha_Modificacion	date
            )
        """)
        conn.commit()

        #cerrar la conexion
        cur.close()
        conn.close()

def cargar_datos(df):
        # conexion a redshift
    try:
        conn = psycopg2.connect(
            host=host,
            dbname=database,
            user=usuario,
            password=contraseña_bd,
            port='5439'
        )
        print("Conectado a Redshift con éxito!")
        
    except Exception as e:
        print("No es posible conectar a Redshift")
        print(e)
   
    #insertar los valores en la tabla
    with conn.cursor() as cur:
        execute_values(
            cur,
            '''
            INSERT INTO  podcast_2024 (Id, Artista, Podcast, Duracion, Genero, Album, Album_img, Episodios, Popularidad, Fecha_Lanzamiento, Fecha_Modificacion)
            VALUES %s
            ''',
            [tuple(row) for row in df.values],
            page_size=len(df)
        )
        conn.commit()
        #cerrar la conexion
        cur.close()
        conn.close()

def extraer_datos2():
    #crear llamada a la api
    client_credentials_manager= SpotifyClientCredentials(client_id=id_client, client_secret= secret)
    sp= spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    #buscar la info en la api
    busqueda = sp.search(q='podcast 2024', type='track', limit=50) 
    #variable con la fecha de extraccion
    now = datetime.date.today().strftime('%Y-%m-%d')
    #columnas para guardar la info 
    columnas = {'Id': [],'Artista': [], 'Podcast': [],'Duracion': [], 'Genero': [],'Album': [], 'Album_img': [], 'Episodios': [], 'Popularidad': [], 'Fecha_Lanzamiento': [],'Fecha_Modificacion': []}
    #acceder a la info
    for track in busqueda['tracks']['items']:
        id = track['id']
        artist_name = track['artists'][0]['name']
        artist_id = track['artists'][0]['id']
        track_name = track['name']
        duration = track['duration_ms']
        track_id = track['id']
        album_group = track['album']['name']
        album_img = track['album']['images'][0]['url'] 
        album_cont = track['album']['total_tracks']
        track_genre =track.get("genres")
        track_popularity = track['popularity']
        track_year = track['album']['release_date']
        #sacar las comillas 
        track_name = track_name.replace("'", "")
        album_group = album_group.replace("'", "")
        columnas['Id'].append(id)
        columnas['Artista'].append(artist_name)
        columnas['Podcast'].append(track_name)
        columnas['Duracion'].append(duration)
        columnas['Album'].append(album_group)
        columnas['Album_img'].append(album_img)
        columnas['Episodios'].append(album_cont)
        columnas['Genero'].append(track_genre)
        columnas['Popularidad'].append(track_popularity)
        columnas['Fecha_Lanzamiento'].append(track_year)
        columnas['Fecha_Modificacion'].append(now)

    #crear el dataframe
    df = pd.DataFrame(columnas)
    #sacar duplicadas
    df.drop_duplicates(subset=['Artista', 'Podcast','Album'], keep='first', inplace=True)
    #llenar los nulos que no tenemos info
    df['Genero'].fillna('Sin Dato', inplace=True)
    df['Genero'].replace('', 'Sin Dato', inplace=True)

    #filtrar para cargar solo valores positivos en la duracion
    df = df.query('Duracion > 0')
    #chequear los formatos de fecha 
    df['Fecha_Lanzamiento'] = pd.to_datetime(df['Fecha_Lanzamiento'], format='%Y-%m-%d')
    df['Fecha_Lanzamiento'] = df['Fecha_Lanzamiento'].dt.strftime('%Y-%m-%d')
      
    #insertar los valores en la tabla
    with conn.cursor() as cur:
        execute_values(
            cur,
            '''
            INSERT INTO  podcast_2024 (Id, Artista, Podcast, Duracion, Genero, Album, Album_img, Episodios, Popularidad, Fecha_Lanzamiento, Fecha_Modificacion)
            VALUES %s
            ''',
            [tuple(row) for row in df.values],
            page_size=len(df)
        )
        conn.commit()
        #cerrar la conexion
        cur.close()
        conn.close()


def alerta_mail():
    try:
        subject = 'Carga de datos'
        body_text = 'El proceso de ETL de Podcast 2024 termino.'
        msg = MIMEMultipart()

        msg['From'] = sender_email
        msg['To'] = sender_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_text, 'plain'))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
        print('El email fue enviado correctamente.')

    except Exception as exception:
        print(exception)
        print('El mail reboto')