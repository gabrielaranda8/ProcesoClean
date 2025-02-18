from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert

import os
import time
import pandas as pd

import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

user_clean = os.environ.get('USER')
pass_clean = os.environ.get('PASS')

def execute_process(credentials):
    # Configuración para descargar automáticamente
    download_dir = os.path.abspath("/tmp/downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Configuración para que Selenium no abra el navegador
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Modo headless
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_dir,  # Directorio donde se guardará el archivo
        "download.prompt_for_download": False,  # Evita el prompt de descarga
        "directory_upgrade": True
    })
    # print("---------------------------------->", chrome_options.to_capabilities())
    # Conexión al Selenium Hub
    driver = webdriver.Remote(
        command_executor='https://standalone-chrome-flcy.onrender.com/wd/hub',
        options=chrome_options
    )

    # Abre la página inicial
    url = "https://www.cleas.com.ar/"
    driver.get(url)

    try:
    # Rellena el formulario de inicio de sesión
        driver.find_element(By.NAME, "txtUser").send_keys(credentials["username"])  # Usuario real
        driver.find_element(By.NAME, "txtPass").send_keys(credentials["password"])  # Contraseña real
        driver.find_element(By.NAME, "lnkEnviar").click()  # Hace clic en el botón "Entrar"

        # Esperar a que cargue la respuesta
        driver.implicitly_wait(10)

        # Captura el HTML de la página resultante
        response_post_html = driver.page_source

    except Exception as e:
        print(f"error de conexion: {e}")
        driver.quit()

    if response_post_html:
        print("Podemos avanzar, ya que las credenciales estan correctas")

        try:
            # Abrir la página
            url = "https://www.cleas.com.ar/wfrmMain2.aspx"
            driver.get(url)
            print("Página cargada correctamente.")

            # Limpiar filtros primero
            try:
                # Esperar a que el enlace de limpiar filtros sea clickeable y hacer clic en él
                limpiar_filtros_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "lnkLimpiarFiltros"))
                )
                limpiar_filtros_link.click()
                
                # Esperar a que cargue la respuesta
                # driver.implicitly_wait(10)
                print("Enlace 'Limpiar Filtros' clickeado.")

                # Esperar a que el enlace 'Avanzado' sea clickeable y hacer clic en él
                filtro_link = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "lnkFiltros"))
                )
                filtro_link.click()
                print("Enlace 'Avanzado' clickeado.")

                # Ahora esperar a que el filtro de zona esté clickeable
                zona_select = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, "lstZona"))
                )
                
                # Crear una instancia de Select para manejar el dropdown
                select_zona = Select(zona_select)
                
                # Seleccionar la opción "No Asignada"
                select_zona.select_by_visible_text("No Asignada")
                print("Filtro aplicado: Zona - No Asignada.")
                
            except Exception as e:
                print(f"Error: {e}")

            # ---------------------------
            # Cambiar la responsabilidad a "Todos"
            responsabilidad_select = driver.find_element(By.NAME, "lstresponsabilidad")
            
            # Crear una instancia de Select para manejar el dropdown
            select_responsabilidad = Select(responsabilidad_select)
            
            # Seleccionar la opción "Todos" por texto visible
            select_responsabilidad.select_by_visible_text("Todos")
            print("Filtro aplicado: Responsabilidad - Todos.")
            # ---------------------------

            # ---------------------------
            # Cambiar el estado
            estado_select = driver.find_element(By.NAME, "lstEstado")
            
            # Crear una instancia de Select para manejar el dropdown
            select_estado = Select(estado_select)
            
            # Seleccionar la opción por texto visible
            select_estado.select_by_visible_text("Vigente - Sin definir responsabilidad")
            print("Filtro aplicado: Vigente - Sin definir responsabilidad.")
            # ---------------------------

            # ---------------------------

            # Aplicar el filtro de zona y seleccionar "No Asignada"
            try:
                zona_select = driver.find_element(By.NAME, "lstZona")
                
                # Crear una instancia de Select para manejar el dropdown
                select_zona = Select(zona_select)
                
                # Seleccionar la opción "No Asignada" por texto visible
                select_zona.select_by_visible_text("No Asignada")
                print("Filtro aplicado: Zona - No Asignada.")
            except Exception as e:
                print(f"Error al aplicar el filtro de zona: {e}")
            # ---------------------------

            # ---------------------------
            # Marcar la casilla "Sólo eventos nuevos (otra compañía)"
            try:
                mensajes_nuevos_checkbox = driver.find_element(By.ID, "chkMensajesNuevos")
                if not mensajes_nuevos_checkbox.is_selected():
                    mensajes_nuevos_checkbox.click()
                    print("Casilla 'Sólo eventos nuevos (otra compañía)' marcada.")
                else:
                    print("La casilla 'Sólo eventos nuevos (otra compañía)' ya estaba marcada.")
            except Exception as e:
                print(f"Error al intentar marcar la casilla: {e}")
            # ---------------------------

            # Esperar hasta que el botón de exportar esté disponible
            export_button = driver.find_element(By.NAME, "btnExportar")
            export_button.click()
            print("Botón de exportar clickeado.")

            # Manejar el popup de confirmación
            alert = driver.switch_to.alert
            print("Popup detectado.")
            alert.accept()
            print("Popup aceptado.")

            # Esperar un tiempo para que la descarga ocurra
            print("Esperando 15 segundos")
            driver.implicitly_wait(15)  # Deja más tiempo si es necesario
            downloaded_files = os.listdir(download_dir)
            # Verificar si el archivo fue descargado
            xls_files = [file for file in downloaded_files if file.endswith('.xls')]

            if xls_files:
                print(f"Archivo descargado exitosamente: {xls_files[0]}")
            else:
                print("No se descargó ningún archivo.")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Cerrar el driver
            driver.quit()

            
    credentials_path = {
      "type": "service_account",
      "project_id": "comentariosanonimos",
      "private_key_id": os.environ.get('PRIVATE_KEY_ID'),
      "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCcDsJH2/ASzrqd\nVEYRs93UheqmBDTuZhbipOjTjMBjmR5DEy/gjBzWFpODhiOCBqE0sO2Ac2L1eech\n2t5/PboAIwsh8NiYRO6ctNk1irm3BkM0c4/ZWJhTbe3nCDGu5w3XSp/jXDjGWtoo\neyM9pFLmVdImgj1dRNdi27Mzm05o+mTFKkQZvn8h1wlZ3xg78mYZ1/WvHUe/fIMn\nmhSpgXhLP2lHlkaDYgJD0kNZcnkYndoJp5xjH7IVX4+rWFyixIqeSO2nSfyFtXCC\nxoeX2Omqi4HCF9WEw6EttURAlSSHc+4z1mmzM1HS8VFUxtupAnQ5Y1EKYRDelXVT\nVBBW+12XAgMBAAECggEACg/Ti/GM0ZGdq54u5F5N+7Fkty6HQSW47QUH8/fbwbAy\nKM34ZMhz5YPQIAdKi8wkobKUpZcK9tvUwLSNavPOZcrcoWQXev3ayqTIanDW14ui\nUqPuzuss6xgn4iD/nxDLrilkFLMx/+wEq96An61UIQDAi3YTQcu5/Wg/7iBh1lfQ\nuwXiO3i9jF2UBVMz/eZIKKXzhgX820VDwEN24lOVOEWKY/fVSLnfe9TVtDkfQBB0\nWoHNRAcROzIvt5cgSyjVDOdw2KK3TQADV+1YHlPV3kp8Tl/e0ZlkdUKDXh53zG5e\n9JxdkItAWEygWKdoIEIyT84gPWqsdnayQD1yKUIFbQKBgQDblGoFRBkuzVB1E9y3\nTGvLME6Y+d3JkBY3x8eF3ShkHrq0TuhzwhgS37vyd5EaZHA578kPYv+rk+Ovbnus\n08N8NtlaCauh1yjDtUBvThF8VemjoRZar5aCCM+fy99rqb9zT9dvEbaNaEnm52x/\noAvs2RPbdbkAbYe7FFmjO9HjtQKBgQC18SFY1Ya3ppRt/WpaU2ICLs7u3qgo9RRi\nADzA6hESPndHEgzlOs/YNHqNCg72H6SOznZjsTGMiHyEb3WrdaJhVHkxxFvOUxvB\nQPTPdIYyKYFEbzWxJgs4nFdaFJJ3iB56xUKcbWVT6HWi/wNfmXfIHFabBPSHe1+n\ntgPSoinjmwKBgFcwdHTI2JML9aG3lFG4Z6kT8nGt7dJGg3v8uQ4/hfVTemF0X7rv\nXC3KZ0/dCGIJdcKboyOX9NuFashTP4qdv6bIBMBKzLsDu20SwJYx0qGjX5WYtk6m\nIEZcB011X67ZhWrdTjcNOoal3YpxZFS9EV8nx0nCUgaId3fimcFGVI5tAoGBAK9E\nm6g1AjMWgLQ4RGTBIJATwXqw+XODLGB/9AavNUTK8iJ/y/ZjImgXndsSTnlg4ChF\n0hyVTLMhpDn8GXHTv1pdguajTwFCZGFVjr/uc3wNKZ7gNuvxRywAx9FaMgJ+GUaR\nkmqYo90h+XjMitZkQ9R9IBzzuBBvlCU+nQ4i85FzAoGAQXUKyKkHoHajZ0F8O/vK\njrwQ+X75AtaExPrnjqb+lfa/zgqJeJl+S97PqzDxLwQDuPMQXZ0XRq8Yhhwk/YuL\n8bTM64R9D8G8JxVLaw2p6e6g9BaZnLzTE/sIHY+Tg0Hcd/tVCL3SnEXLUNiQi20x\nvK14SP8OIP0KcKvduwAJ53Q=\n-----END PRIVATE KEY-----\n",
      "client_email": os.environ.get('CLIENT_EMAIL'),
      "client_id": os.environ.get('CLIENT_ID'),
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": os.environ.get('CERT_URL'),
      "universe_domain": "googleapis.com"
    }

    downloaded_files = os.listdir(download_dir)
    try:
        xls_files = [file for file in downloaded_files if file.endswith('.xls')]
        excel_file = os.path.join(download_dir, xls_files[0])
    except Exception as e:
        print(f"No se encontro ningun archivo: {e}")
        xls_files = None

    if excel_file:
        print(f"Archivo encontrado: {excel_file}")

        # Leer el archivo Excel con pandas
        df_excel = pd.read_excel(excel_file, engine='xlrd')
        df_excel = df_excel.fillna("")  # Limpiar el DataFrame (reemplazar NaN con cadenas vacías)
        # print("LLEGA")
        # Verificar que la columna `Id_Oper` existe en el Excel
        if 'Id_Oper' not in df_excel.columns:
            raise ValueError("La columna 'Id_Oper' no existe en el archivo Excel.")

        # Conexión a Google Sheets
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_path, scope)
        gc = gspread.authorize(creds)

        # Abrir la hoja de Google Sheets
        spreadsheet = gc.open_by_key(sheet_path).sheet1

        # Leer datos de Google Sheets
        sheet_data = spreadsheet.get_all_values()
        if not sheet_data:
            print("La hoja de Google Sheets está vacía.")
            sheet_data = [[]]

        # Obtener IDs existentes en Google Sheets y la primera columna
        headers = sheet_data[0]  # Primera fila (encabezados)
        sheet_df = pd.DataFrame(sheet_data[1:], columns=headers)  # Ignorar la primera fila

        # Preservar la primera columna
        first_column = sheet_df.iloc[:, 0].tolist()

        # Obtener IDs existentes
        existing_ids = sheet_df['Id_Oper'].tolist() if 'Id_Oper' in sheet_df.columns else []
        print(f"IDs existentes en Google Sheets: {existing_ids}")

        # Filtrar solo los nuevos IDs
        new_data = df_excel[~df_excel['Id_Oper'].isin(existing_ids)]
        print(f"Nuevos datos a agregar:\n{new_data}")

        # Subir solo los nuevos datos a Google Sheets (preservando la primera columna)
        if not new_data.empty:
            # Preparar la data para añadir (sin tocar la primera columna)
            updated_data = pd.concat([sheet_df, new_data], ignore_index=True)
            updated_data.iloc[:, 0] = first_column + [""] * (len(updated_data) - len(first_column))  # Expandir si es necesario

            # Subir a Google Sheets
            spreadsheet.update(
                [updated_data.columns.values.tolist()] + updated_data.fillna("").values.tolist(),
                value_input_option="USER_ENTERED"
            )
            print(f"Datos nuevos añadidos a Google Sheets.")
        else:
            print("No hay nuevos datos para agregar.")

        # Eliminar el archivo procesado
        os.remove(excel_file)
    else:
        print("No se encontró un archivo Excel en el directorio de descargas.")

