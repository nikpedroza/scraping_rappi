from selenium import webdriver
from selenium.webdriver.common.by import By #Buscador en el html
from selenium.webdriver.common.action_chains import ActionChains    #Acciones de teclado y mouse
from selenium.webdriver.support.ui import WebDriverWait #Espera condiciones en la pagina
from selenium.webdriver.support import expected_conditions as EC    #Busca elementos con determinada condicion
from selenium.webdriver.common.keys import Keys #Movimientos de teclado
from selenium.common.exceptions import NoSuchElementException,TimeoutException #Se usa en try-except para identificar errores de selenium
import gspread  #Libreria para Google Sheets
from google.oauth2.service_account import Credentials #Libreria para Google Sheets
#import requests #Comentado para pruebas
import json #Para almacenar y administrar los JSON
from time import sleep  #Temporizador
from datetime import datetime,timedelta #Necesario para conseguir iterar fechas
import csv  #Guardamos los datos
import os #Lo utilizamos unicamente para no sobreescribir el csv
from dotenv import load_dotenv #Esto es para importar datos privados guardados en un .env
import asyncio  #Asincronia
import aiohttp  #Asincronia

load_dotenv()

def Login_y_extraccion_token():
    driver=webdriver.Chrome()
    url="https://partners.rappi.com/home"
    driver.get(url)
    wait=WebDriverWait(driver,10)
    movimiento=ActionChains(driver)

    email=os.getenv("EMAIL")    #Datos guardados en .env
    password=os.getenv("PASSWORD")  #Datos guardados en .env

    if not email or not password:
        print("Virificar que el EMAIL o PASSWORD no estan definidos")

    '''LOGIN'''
    sleep(4)#Pausa para esperar que cargue la pagina
    wait.until(EC.visibility_of_element_located((By.XPATH,"//*[@id='1-email']"))).send_keys(email,Keys.TAB)
    wait.until(EC.visibility_of_element_located((By.XPATH,"//*[@id='1-password']"))).send_keys(password,Keys.ENTER)

    sleep(10)   #Se agrega el tiempo suficiente ya que RAPPI agrega una "publicidad" sobre la parte HOME
    #Codigo de 2FA
    if "https://partners.rappi.com/home" in driver.current_url: #verificamos estar en el home
        print("Inicio de sesion correcto")
    elif "https://partners.rappi.com/plans" in driver.current_url:  #Verificamos estar en su "Publicidad" y eliminamos
        boton_skip=wait.until(EC.visibility_of_element_located((By.XPATH,"//*[@id='main-layout-main-content']/div/main/article[6]/section/button/div/div")))
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);");sleep(0.5) #Escroleamos sin razon para "demostrar" que tocamos el boton
        movimiento.move_to_element(boton_skip).click().perform()
        print("Inicio de sesion correcto")
        sleep(5)
    else:
        try:
            otro_metodo=wait.until(EC.visibility_of_element_located((By.XPATH,"/html/body/div/main/section/div/div/div/div/form/button")))
            movimiento.move_to_element(otro_metodo).click().perform()

            elegir_correo=wait.until(EC.visibility_of_element_located((By.XPATH,"//*[@id='with-selector-list']/li[2]/form/button")))
            movimiento.move_to_element(elegir_correo).click().perform()

            codigo_2fa=wait.until(EC.visibility_of_element_located((By.XPATH,"//*[@id='code']")))
            codigo_recibido=input("Por favor ingrese el codigo recibido: ")
            codigo_2fa.send_keys(codigo_recibido,Keys.ENTER)

            print("Datos ingresados correctamente, ahora estas en el dashboard")    
        except (NoSuchElementException,TimeoutException) as e:
            print("Inicio correcto no se detecto factor 2FA")
    '''FIN LOGIN'''

    wait.until(EC.visibility_of_element_located((By.XPATH,"//*[@id='main-layout-main-content']/div[2]/div[2]")))
    driver.refresh()    #reinicamos para cargar el json con los datos
    sleep(3)

    '''OBTENCION DE TOKEN'''
    try:
        token=driver.execute_script("return window.localStorage.getItem('access_token');")  #Guardamos el token UNICO que da la pagina
        print("Token obtenido, pasando a la peticion de datos...")
        sleep(1)
    except Exception  as e:
        print(f"Error {e}")
    return token

def obtener_id_sheets():
    # Autenticación con la cuenta de servicio
    creds = Credentials.from_service_account_file(
        'sheet-api-python.json',    #Se enlazan las credenciales de la api personal de GOOGLE
        scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
    client = gspread.authorize(creds)
    # ID del Google Sheet y nombre de la hoja con el rango deseado
    spreadsheet_id = os.getenv("SPREAD_SHEET_ID")
    sheet = client.open_by_key(spreadsheet_id).worksheet("id_rappi_general")

    # Leer el rango donde estan almacenados los ID de tiendas
    valores = sheet.get("M2:M")
    ids=[]
    
    for var in valores: #FILTRAMOS LOS "FALSE"
        if var[0] != "FALSE":
            ids.append(var[0])
    
    return ids

def obtener_json(token,fecha,id_sucursal):
    json_url="https://services.rappi.com/rests-partners-gateway/cauth/partners-indicators/indicator/sales/prime?previous=true"#Ruta de las peticiones para enviarlas

    #Header copiado desde la DevTool de RAPPI para enviar los datos de manera que el servidor los acepte y los tome como propios
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json;charset=UTF-8',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'es',
        'Origin': 'https://partners.rappi.com',
        'Referer': 'https://partners.rappi.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    }
    # Creamos una lista para almacenar los paises de las sucursales
    country=[]
    c=0
    for i in id_sucursal:#Iteramos los ID para separar el country code
        if "AR" in i:
            country.append("AR")
        elif "CL" in i:
            country.append("CL")
        elif "MX" in i:
            country.append("MX")
        elif "PE" in i:
            country.append("PE")
        elif "CO" in i:
            country.append("CO")
        elif "CR" in i:
            country.append("CR")
        else:
            print(f"Pais no identificado para la sucursal {i}, se omitira")
            country.append("AR")

    diccionario_para_csv=[] #Creamos una lista donde se guardaran diccionarios de los datos obtenidos
    for i in id_sucursal:
        payload = { #Se lo mandamos como "payload" para evitar errores
            "country_code": f"{country[c]}",
            "from": f"{fecha}",
            "to": f"{fecha}",
            "store_ids": [
                f"{i}"
            ]
        }
        c+=1
        respuesta=requests.post(json_url,headers=headers,json=payload)
        

        print(f"status code: {respuesta.status_code}") #Confirmamos que el servidor haya recibido la REQUEST correctamente 
        print(f"Dato numero:{c}")
        
        try:
            datos=respuesta.json()
            print(f"-----------------\nID:{i}\nGanancia:${datos['total_amount']}\nOrdenes: {datos['total_orders']}\n{fecha}\n-----------------")
            diccionario_para_csv.append({
                "Fecha":fecha,
                "ID":i,
                "Ordenes":datos['total_orders'],
                "Ganancia":datos['total_amount']
                })
        except json.JSONDecodeError: 
            print("-----------------\nNo se pudo decodificar el json,Continuamos con el siguiente dato.\n-----------------")

    #Escritura del csv
    archivo_existe=os.path.isfile("datos.csv")
    
    with open("datos.csv","a",encoding="UTF-8",newline="") as datos_csv:
        #Definimos los encabezados
        nom_columna=["Fecha","ID","Ordenes","Ganancia"]
        csv_dics=csv.DictWriter(datos_csv,fieldnames=nom_columna)
            
        if not archivo_existe:
            csv_dics.writeheader()  # Escribimos encabezado solo si es la primera vez

        for fila in diccionario_para_csv:
            csv_dics.writerow(fila)


#INICIAMOS LA SECUENCIA
if __name__=="__main__":
    token=Login_y_extraccion_token()   #Relizamos login
    print("OBTENIENDO LOS DATOS DEL SHEETS....")
    id_tiendas=obtener_id_sheets()  #Consultamos las tiendas
    print("INICIANDO PETICIONES....")

    #Esto para obtener una fecha personalizada
    #fecha_desde=input("Ingrese desde donde empiezan los datos en este formateo:'AAAA-MM-DD' Incluyendo el '-'\nIngrese:")
    #fecha_hasta=input("Ingrese hasta donde obtener los datos en este formateo:'AAAA-MM-DD' Incluyendo el '-'\nIngrese:")
    #fecha_desde=datetime.datetime.strptime(fecha_desde,"%Y-%m-%d").date()
    #fecha_hasta=datetime.datetime.strptime(fecha_hasta,"%Y-%m-%d").date()
      
    #aca igresar las fechas predefinas
    fecha_desde=datetime.date(2025,7,22)    
    fecha_hasta=datetime.date(2025,7,23)
    
    fecha_iterador=fecha_desde

    while fecha_iterador <= fecha_hasta:
        obtener_json(token,fecha_iterador,id_tiendas)#fecha:año/mes/dia #Guarda el json en esa variable
        fecha_iterador+=timedelta(days=1)
    
    #Opcion 3: Mostrar dia de ayer 
    #En caso de uso comentar el WHILE y descomentar el llamada a la funcion de abajo
    hoy=datetime.now().date()
    ayer=hoy-timedelta(days=1)  #En caso de querer restar mas dias subirle a days=
    #obtener_json(token,ayer,id_tiendas)
    
    print("Obtencion finalizada")