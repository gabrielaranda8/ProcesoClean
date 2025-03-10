from flask import Flask, render_template, request, redirect, url_for, session
import threading
import time
from datetime import datetime, timedelta
from proceso import execute_process, validate_credentials
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev") # Cambia esto por una clave secreta segura

# Variables globales
is_running = False
current_thread = None
process_count = 0  # Contador de procesos ejecutados
frequency = 0  # Frecuencia en minutos
stop_process = False  # Bandera para detener el proceso

# Función que ejecuta el proceso cada cierta cantidad de minutos
def long_running_process(frequency, credentials):
    global is_running, process_count, stop_process
    while is_running:

        current_time = datetime.now()
        new_time = current_time - timedelta(hours=3)
        formatted_time = new_time.strftime("%H:%M")

        # Si son más de 18:00, detener el proceso
        if formatted_time > "18:00":
            print("Son más de 18:00. Deteniendo el proceso automáticamente.")
            is_running = False
            stop_process = True  # Establecer la bandera
            break  # Salir del bucle

        process_count += 1  # Incrementar el contador de procesos
        print(f"Iniciando el proceso número {process_count}...")
        execute_process(credentials)  # Pasar las credenciales
        print(f"Proceso número {process_count} completado.")
        # Esperar a la siguiente ejecución, según la frecuencia (en minutos)
        time.sleep(frequency * 60)  # Convertir la frecuencia a segundos

# Decorador para proteger rutas que requieren autenticación
def login_required(f):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  # Necesario para evitar conflictos con Flask
    return wrapper

@app.before_request
def check_stop_process():
    global stop_process
    if stop_process:
        stop_process = False
        # Si se tiene que detener el proceso, hacer un redirect
        return redirect(url_for("index"))

# Ruta principal para mostrar el estado del proceso y controlar la ejecución
@app.route("/proceso", methods=["GET", "POST"])
@login_required
def index():
    global is_running, current_thread, process_count, frequency

    if request.method == "POST":
        if request.form["action"] == "start":
            frequency = int(request.form["frequency"])
            if not is_running:
                is_running = True
                process_count = 0  # Reiniciar el contador cuando se inicia
                credentials = {"username": session["user"], "password": session["pass"]}  # Credenciales del usuario
                current_thread = threading.Thread(target=long_running_process, args=(frequency, credentials))
                current_thread.start()
        elif request.form["action"] == "stop":
            is_running = False
            if current_thread is not None:
                current_thread.join()
        return redirect(url_for("index"))

    return render_template("index.html", is_running=is_running, process_count=process_count, frequency=frequency if is_running else 0)

# Ruta de inicio de sesión
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        credentials = {"username": username, "password": password}
        
        # Validar credenciales contra CLEAS
        if validate_credentials(credentials):
            session["user"] = username
            session["pass"] = password
            return redirect(url_for("index"))
        else:
            return "Credenciales inválidas", 401

    return render_template("login.html")

# Ruta para cerrar sesión
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5050)
