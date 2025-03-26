import os
import time
from datetime import datetime
import pandas as pd
import asyncio

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


### GSHEETS
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

sheet_path = os.environ.get('SHEET_PATH')


def retry_action(page, action, max_attempts=3, timeout=10000, wait_between_attempts=2000):
    """Función para reintentar una acción de Playwright con espera entre intentos."""
    for attempt in range(max_attempts):
        try:
            return action()  # Ejecuta la acción y retorna si tiene éxito
        except PlaywrightTimeoutError as e:
            print(f"Intento {attempt + 1}/{max_attempts} falló: {e}")
            if attempt < max_attempts - 1:
                page.wait_for_timeout(wait_between_attempts)  # Espera antes de reintentar
            else:
                raise  # Relanza la excepción si se agotan los intentos


async def execute_process(credentials, retry=True):
    print("COMIENZO execute_process")

    
    ids = []

    async with async_playwright() as p:
        # Lanzar el navegador en modo headless
        browser = await  p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        context = await  browser.new_context()
        page = await context.new_page()

        # Abre la página inicial
        url = "https://www.cleas.com.ar/"
        try:
            await  page.goto(url, wait_until='domcontentloaded')
            print("Página inicial cargada.")
        except PlaywrightTimeoutError:
            print("Tiempo de espera agotado al cargar la página inicial.")
            await  browser.close()
            return

        # Intentar login con manejo de espera
        try:
            time.sleep(2)
            # Esperar a que los campos de login estén disponibles
            await page.wait_for_selector('input[name="txtUser"]', timeout=10000)  # 10 segundos de espera máxima
            await page.fill('input[name="txtUser"]', credentials["username"])
            await page.fill('input[name="txtPass"]', credentials["password"])
            await page.click('input[name="lnkEnviar"]')
            time.sleep(2)

            # Esperar a que la página cargue después del login
            await page.wait_for_load_state('networkidle', timeout=15000)  # 15 segundos para carga completa
            response_post_html = await page.content()

        except PlaywrightTimeoutError as e:
            print(f"Error de conexión: tiempo de espera agotado en el login - {e}")
            await browser.close()
            return
        except Exception as e:
            print(f"Error de conexión inesperado: {e}")
            await browser.close()
            return

        if response_post_html:
            print("Podemos avanzar, ya que las credenciales están correctas")

            # Navegar a la página principal
            try:
                url = "https://www.cleas.com.ar/wfrmMain2.aspx"
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                time.sleep(2)
                await page.wait_for_load_state('networkidle', timeout=15000)
                print("Página principal cargada correctamente.")
            except PlaywrightTimeoutError:
                print("Tiempo de espera agotado al cargar la página principal.")
                await browser.close()
                return

            try:
                time.sleep(5)
                # Limpiar filtros
                await retry_action(page, lambda: page.wait_for_selector('#lnkLimpiarFiltros', state='visible', timeout=10000))
                time.sleep(5)
                await retry_action(page, lambda: page.click('#lnkLimpiarFiltros'))
                print("Enlace 'Limpiar Filtros' clickeado.")
                time.sleep(5)
                await page.wait_for_load_state('domcontentloaded', timeout=5000)

                # Hacer clic en 'Avanzado'
                time.sleep(2)
                await retry_action(page, lambda: page.wait_for_selector('#lnkFiltros', state='visible', timeout=10000))
                time.sleep(2)
                await retry_action(page, lambda: page.click('#lnkFiltros'))
                print("Enlace 'Avanzado' clickeado.")
                time.sleep(10)
                await page.wait_for_load_state('domcontentloaded', timeout=5000)

                # Seleccionar "No Asignada" en el filtro de zona
                time.sleep(2)
                await retry_action(page, lambda: page.wait_for_selector('select[name="lstZona"]', state='visible', timeout=10000))
                time.sleep(2)
                await retry_action(page, lambda: page.select_option('select[name="lstZona"]', label="No Asignada"))
                print("Filtro aplicado: Zona - No Asignada.")
                time.sleep(2)
                await page.wait_for_load_state('domcontentloaded', timeout=5000)

                # Cambiar la responsabilidad a "Todos"
                time.sleep(2)
                await retry_action(page, lambda: page.wait_for_selector('select[name="lstresponsabilidad"]', state='visible', timeout=10000))
                time.sleep(2)
                await retry_action(page, lambda: page.select_option('select[name="lstresponsabilidad"]', label="Todos"))
                print("Filtro aplicado: Responsabilidad - Todos.")
                time.sleep(2)
                await page.wait_for_load_state('domcontentloaded', timeout=5000)

                # Cambiar el estado
                time.sleep(2)
                await retry_action(page, lambda: page.wait_for_selector('select[name="lstEstado"]', state='visible', timeout=10000))
                time.sleep(2)
                await retry_action(page, lambda: page.select_option('select[name="lstEstado"]', label="Vigente - Sin definir responsabilidad"))
                print("Filtro aplicado: Vigente - Sin definir responsabilidad.")
                time.sleep(2)
                await page.wait_for_load_state('domcontentloaded', timeout=5000)

                # Volver a seleccionar "No Asignada"
                time.sleep(2)
                await retry_action(page, lambda: page.wait_for_selector('select[name="lstZona"]', state='visible', timeout=10000))
                time.sleep(2)
                await retry_action(page, lambda: page.select_option('select[name="lstZona"]', label="No Asignada"))
                print("Filtro reaplicado: Zona - No Asignada.")
                time.sleep(2)
                await page.wait_for_load_state('domcontentloaded', timeout=5000)

                # Marcar la casilla
                time.sleep(2)
                await retry_action(page, lambda: page.wait_for_selector('#chkMensajesNuevos', state='visible', timeout=10000))
                if not await page.is_checked('#chkMensajesNuevos'):
                    time.sleep(2)
                    await retry_action(page, lambda: page.check('#chkMensajesNuevos'))
                    print("Casilla 'Sólo eventos nuevos (otra compañía)' marcada.")
                else:
                    print("La casilla 'Sólo eventos nuevos (otra compañía)' ya estaba marcada.")
                time.sleep(2)
                await page.wait_for_load_state('domcontentloaded', timeout=5000)

                # Extraer IDs
                time.sleep(2)
                await retry_action(page, lambda: page.wait_for_selector('div#tramite', state='visible', timeout=15000))
                tramite_divs = await page.query_selector_all('div#tramite')
                for tramite in tramite_divs:
                    try:
                        link = await tramite.query_selector('a[id*="hlnkNroCleas"]')
                        if link:
                            href = await link.get_attribute('href')  # Esperar el resultado antes de manipularlo
                            if href and 'Id=' in href:
                                id_value = href.split('Id=')[1].split('&')[0]
                                ids.append(id_value)
                    except Exception as e:
                        print(f"Error al procesar un trámite: {e}")
                        continue

                print("IDs de los trámites encontrados:", ids)

            except PlaywrightTimeoutError as e:
                print(f"Error: tiempo de espera agotado en alguna acción - {e}")
                ids = []

                await context.close()
                await browser.close()

                if retry: 
                    print("Reintentando execute_process una vez más...")
                    await execute_process(credentials, retry=False)

            except Exception as e:
                print(f"Error inesperado: {e}")
                ids = []
                await browser.close()
            finally:
                await browser.close()

    
    if len(ids) > 0:
        print("Ahora agregaremos los IDs en Google Sheets")
        try:
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
                sheet_data = [['Id_Oper', 'last_update', 'date']]  # Encabezados mínimos si está vacía

            # Obtener encabezados y datos
            headers = sheet_data[0]
            if 'Id_Oper' not in headers or 'last_update' not in headers or 'date' not in headers:
                headers = ['Id_Oper', 'last_update', 'date']  # Asegurar encabezados necesarios
            sheet_df = pd.DataFrame(sheet_data[1:], columns=headers) if len(sheet_data) > 1 else pd.DataFrame(columns=headers)

            # Obtener IDs existentes
            existing_ids = sheet_df['Id_Oper'].tolist() if 'Id_Oper' in sheet_df.columns else []
            print(f"IDs existentes en Google Sheets: {existing_ids}")

            # Filtrar solo los nuevos IDs
            new_ids = [id_value for id_value in ids if id_value not in existing_ids]
            print(f"Nuevos IDs a agregar: {new_ids}")

            # Si hay nuevos IDs, agregarlos con la fecha actual
            if new_ids:
                # Crear un DataFrame con los nuevos IDs y last_update
                current_time = (datetime.now() - pd.Timedelta(hours=3)).strftime('%Y-%m-%d %H:%M:%S')

                date = datetime.now()
                formatted_date = date.strftime("%Y-%m-%d")
                
                new_data = pd.DataFrame({
                    'Id_Oper': new_ids,
                    'last_update': [current_time] * len(new_ids),
                    'date': [formatted_date] * len(new_ids)
                })

                # Combinar con los datos existentes
                updated_data = pd.concat([sheet_df, new_data], ignore_index=True)

                # Subir a Google Sheets (incluyendo encabezados)
                spreadsheet.update(
                    [updated_data.columns.values.tolist()] + updated_data.fillna("").values.tolist(),
                    value_input_option="USER_ENTERED"
                )
                print(f"Se agregaron {len(new_ids)} nuevos IDs a Google Sheets con last_update: {current_time}")
            else:
                print("No hay nuevos IDs para agregar.")

        except Exception as e:
            print(f"Error al interactuar con Google Sheets: {e}")



# Función para validar credenciales en CLEAS
def validate_credentials(credentials):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page()

        url = "https://www.cleas.com.ar/"
        try:
            page.goto(url, wait_until='domcontentloaded', timeout=5000)
            page.wait_for_selector('input[name="txtUser"]', timeout=5000)
            page.fill('input[name="txtUser"]', credentials["username"])
            page.fill('input[name="txtPass"]', credentials["password"])
            page.click('input[name="lnkEnviar"]')

            # Esperar a que aparezca el elemento imgCleas (indicador de login exitoso)
            page.wait_for_selector('input#imgCleas', timeout=5000)
            browser.close()
            return True  # Login exitoso si imgCleas aparece
        except PlaywrightTimeoutError:
            browser.close()
            return False  # Timeout indica que imgCleas no apareció, credenciales probablemente incorrectas
        except Exception as e:
            print(f"Error inesperado al validar credenciales: {e}")
            browser.close()
            return False