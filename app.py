from flask import Flask, render_template, request, redirect, url_for
import threading
import time
from proceso import execute_process

app = Flask(__name__)

# Variables globales
is_running = False
current_thread = None
process_count = 0  # Contador de procesos ejecutados
frequency = 0  # Frecuencia en minutos

# Función que ejecuta el proceso cada cierta cantidad de minutos
def long_running_process(frequency):
    global is_running, process_count
    while is_running:
        process_count += 1  # Incrementar el contador de procesos
        print(f"Iniciando el proceso número {process_count}...")
        execute_process()  # Aquí va tu proceso
        print(f"Proceso número {process_count} completado.")
        # Esperar a la siguiente ejecución, según la frecuencia (en minutos)
        time.sleep(frequency * 60)  # Convertir la frecuencia a segundos

# Ruta principal para mostrar el estado del proceso y controlar la ejecución
@app.route("/", methods=["GET", "POST"])
def index():
    global is_running, current_thread, process_count, frequency

    if request.method == "POST":
        if request.form["action"] == "start":
            frequency = int(request.form["frequency"])
            if not is_running:
                is_running = True
                process_count = 0  # Reiniciar el contador cuando se inicia
                current_thread = threading.Thread(target=long_running_process, args=(frequency,))
                current_thread.start()
        elif request.form["action"] == "stop":
            is_running = False
            if current_thread is not None:
                current_thread.join()
        return redirect(url_for("index"))

    return render_template("index.html", is_running=is_running, process_count=process_count, frequency=frequency if is_running else 0)

if __name__ == "__main__":
    print("ARRANCA FLASK ---------------------------------->")
    app.run(debug=True, host='0.0.0.0', port=5000)