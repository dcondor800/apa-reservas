from flask import Flask, render_template, request, redirect, url_for, session
from flask_mail import Mail, Message
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'clave_supersecreta'
TIEMPO_LIMITE_MINUTOS = 5

# Configuración de Flask-Mail con Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'dcondor79@gmail.com'           # ← Cambia esto
app.config['MAIL_PASSWORD'] = 'jiab sppf msnh bfqm'       # ← Cambia esto
app.config['MAIL_DEFAULT_SENDER'] = 'dcondor79@gmail.com'     # ← Cambia esto

mail = Mail(app)

# Lista de stands de ejemplo (debes completarla según tu layout)
stands = [
    ("32", "grid-column: 3; grid-row: 1;", "exhibidor"),
    ("31", "grid-column: 4; grid-row: 1;", "exhibidor"),
    ("30", "grid-column: 5; grid-row: 1;", "exhibidor"),
    ("29", "grid-column: 6; grid-row: 1;", "exhibidor"),
    ("A10", "grid-column: 8; grid-row: 1 / span 3;", "auspiciador"),
    ("I", "grid-column: 10 / span 2; grid-row: 1 / span 3;", "patrocinador"),
    ("A9", "grid-column: 13; grid-row: 1 / span 3;", "auspiciador"),
    ("28", "grid-column: 15; grid-row: 1;", "exhibidor"),
    ("27", "grid-column: 16; grid-row: 1;", "exhibidor"),
    ("26", "grid-column: 17; grid-row: 1;", "exhibidor"),
    ("25", "grid-column: 18; grid-row: 1;", "exhibidor"),
    ("33", "grid-column: 3; grid-row: 3;", "exhibidor"),
    ("34", "grid-column: 4; grid-row: 3;", "exhibidor"),
    ("Exp10", "grid-column: 6; grid-row: 3;", "premium"),
    ("Exp9", "grid-column: 15; grid-row: 3;", "premium"),
    ("23", "grid-column: 17; grid-row: 3;", "exhibidor"),
    ("24", "grid-column: 18; grid-row: 3;", "exhibidor"),
    ("36", "grid-column: 3; grid-row: 4;", "exhibidor"),
    ("35", "grid-column: 4; grid-row: 4;", "exhibidor"),
    ("22", "grid-column: 17; grid-row: 4;", "exhibidor"),
    ("21", "grid-column: 18; grid-row: 4;", "exhibidor"),
    ("A8", "grid-column: 6; grid-row: 5 / span 3;", "auspiciador"),
    ("A7", "grid-column: 15; grid-row: 5 / span 3;", "auspiciador"),
    ("H", "grid-column: 8 / span 2; grid-row: 5 / span 3;", "patrocinador"),
    ("G", "grid-column: 12 / span 2; grid-row: 5 / span 3;", "patrocinador"),
    ("37", "grid-column: 3; grid-row: 6;", "exhibidor"),
    ("38", "grid-column: 4; grid-row: 6;", "exhibidor"),
    ("19", "grid-column: 17; grid-row: 6;", "exhibidor"),
    ("20", "grid-column: 18; grid-row: 6;", "exhibidor"),
    ("40", "grid-column: 3; grid-row: 7;", "exhibidor"),
    ("39", "grid-column: 4; grid-row: 7;", "exhibidor"),
    ("18", "grid-column: 17; grid-row: 7;", "exhibidor"),
    ("17", "grid-column: 18; grid-row: 7;", "exhibidor"),
    ("41", "grid-column: 3; grid-row: 9;", "exhibidor"),
    ("Exp8", "grid-column: 4; grid-row: 9;", "premium"),
    ("Exp7", "grid-column: 17; grid-row: 9;", "premium"),
    ("16", "grid-column: 18; grid-row: 9;", "exhibidor"),
    ("A6", "grid-column: 6; grid-row: 9 / span 3;", "auspiciador"),
    ("A5", "grid-column: 15; grid-row: 9 / span 3;", "auspiciador"),
    ("F", "grid-column: 8 / span 2; grid-row: 9 / span 3;", "patrocinador"),
    ("E", "grid-column: 12 / span 2; grid-row: 9 / span 3;", "patrocinador"),
    ("42", "grid-column: 3; grid-row: 10;", "exhibidor"),
    ("Exp6", "grid-column: 4; grid-row: 10;", "premium"),
    ("Exp5", "grid-column: 17; grid-row: 10;", "premium"),
    ("15", "grid-column: 18; grid-row: 10;", "exhibidor"),
    ("43", "grid-column: 3; grid-row: 13;", "exhibidor"),
    ("Exp4", "grid-column: 4; grid-row: 13;", "premium"),
    ("Exp3", "grid-column: 17; grid-row: 13;", "premium"),
    ("14", "grid-column: 18; grid-row: 13;", "exhibidor"),
    ("A4", "grid-column: 6; grid-row: 13 / span 3;", "auspiciador"),
    ("A3", "grid-column: 15; grid-row: 13 / span 3;", "auspiciador"),
    ("D", "grid-column: 8 / span 2; grid-row: 13 / span 3;", "patrocinador"),
    ("C", "grid-column: 12 / span 2; grid-row: 13 / span 3;", "patrocinador"),
    ("44", "grid-column: 3; grid-row: 14;", "exhibidor"),
    ("Exp2", "grid-column: 4; grid-row: 14;", "premium"),
    ("Exp1", "grid-column: 17; grid-row: 14;", "premium"),
    ("13", "grid-column: 18; grid-row: 14;", "exhibidor"),
    ("B", "grid-column: 8 / span 2; grid-row: 17 / span 3;", "patrocinador"),
    ("A", "grid-column: 12 / span 2; grid-row: 17 / span 3;", "patrocinador"),
    ("A2", "grid-column: 3 / span 2; grid-row: 17 / span 2;", "auspiciador"),
    ("A1", "grid-column: 17 / span 2; grid-row: 17 / span 2;", "auspiciador"),
    ("58", "grid-column: 1; grid-row: 2;", "exhibidor"),
    ("57", "grid-column: 1; grid-row: 3;", "exhibidor"),
    ("56", "grid-column: 1; grid-row: 4;", "exhibidor"),
    ("55", "grid-column: 1; grid-row: 5;", "exhibidor"),
    ("54", "grid-column: 1; grid-row: 6;", "exhibidor"),
    ("53", "grid-column: 1; grid-row: 7;", "exhibidor"),
    ("52", "grid-column: 1; grid-row: 8;", "exhibidor"),
    ("51", "grid-column: 1; grid-row: 9;", "exhibidor"),
    ("50", "grid-column: 1; grid-row: 10;", "exhibidor"),
    ("49", "grid-column: 1; grid-row: 11;", "exhibidor"),
    ("48", "grid-column: 1; grid-row: 12;", "exhibidor"),
    ("47", "grid-column: 1; grid-row: 13;", "exhibidor"),
    ("46", "grid-column: 1; grid-row: 14;", "exhibidor"),
    ("45", "grid-column: 1; grid-row: 15;", "exhibidor"),
    ("12", "grid-column: 20; grid-row: 2;", "exhibidor"),
    ("11", "grid-column: 20; grid-row: 3;", "exhibidor"),
    ("10", "grid-column: 20; grid-row: 4;", "exhibidor"),
    ("9", "grid-column: 20; grid-row: 5;", "exhibidor"),
    ("8", "grid-column: 20; grid-row: 8;", "exhibidor"),
    ("7", "grid-column: 20; grid-row: 9;", "exhibidor"),
    ("6", "grid-column: 20; grid-row: 10;", "exhibidor"),
    ("5", "grid-column: 20; grid-row: 11;", "exhibidor"),
    ("4", "grid-column: 20; grid-row: 12;", "exhibidor"),
    ("3", "grid-column: 20; grid-row: 13;", "exhibidor"),
    ("2", "grid-column: 20; grid-row: 14;", "exhibidor"),
    ("1", "grid-column: 20; grid-row: 15;", "exhibidor"),

]

def obtener_prioridad_disponible():
    df = pd.read_csv("preregistro.csv")
    usados = []
    expirados = []

    if os.path.exists("reserva_stands.csv"):
        reservas = pd.read_csv("reserva_stands.csv")
        usados = reservas['email'].tolist()

    if os.path.exists("expirados.csv"):
        expirados = pd.read_csv("expirados.csv")['email'].tolist()

    df = df[~df['email'].isin(usados + expirados)]
    return df['orden_prioridad'].min() if not df.empty else None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()

        if os.path.exists("reserva_stands.csv"):
            df_reserva = pd.read_csv("reserva_stands.csv")
            if email in df_reserva['email'].values:
                stand_reservado = df_reserva[df_reserva['email'] == email]['stand'].values[0]
                return render_template("ya_escogiste.html", stand=stand_reservado)

        if os.path.exists("expirados.csv"):
            df_exp = pd.read_csv("expirados.csv")
            if email in df_exp['email'].values:
                return render_template("expirado_espera.html", modo="reintento")

        df = pd.read_csv("preregistro.csv")
        df['email'] = df['email'].str.strip().str.lower()
        user = df[df['email'] == email]

        if user.empty:
            return render_template("index.html", error="Correo no registrado.")

        prioridad_usuario = int(user['orden_prioridad'].values[0])
        return redirect(url_for('espera', email=email, prioridad_usuario=prioridad_usuario))

    return render_template('index.html')

@app.route('/espera')
def espera():
    email = request.args.get('email')
    prioridad_usuario = int(request.args.get('prioridad_usuario'))
    prioridad_actual = obtener_prioridad_disponible()

    if prioridad_usuario == prioridad_actual:
        if 'start_time' not in session or session.get('email') != email:
            session['start_time'] = int(datetime.now().timestamp() * 1000)  # tiempo en milisegundos
        session['email'] = email
        return redirect(url_for('plano'))

    return render_template('espera.html', email=email, prioridad_usuario=prioridad_usuario, prioridad_actual=prioridad_actual)

@app.route('/plano', methods=['GET', 'POST'])
def plano():
    email = session.get('email')
    start_time = session.get('start_time')

    if not start_time or not email:
        return redirect(url_for('index'))

    # Verifica si el usuario ya reservó un stand
    if os.path.exists("reserva_stands.csv"):
        df_reserva = pd.read_csv("reserva_stands.csv")
        if email in df_reserva['email'].values:
            stand_reservado = df_reserva[df_reserva['email'] == email]['stand'].values[0]
            return render_template("ya_escogiste.html", stand=stand_reservado)
    else:
        df_reserva = pd.DataFrame(columns=["email", "stand"])

    reservados = df_reserva['stand'].tolist()

    if request.method == 'POST':
        stand = request.form['stand'].strip()

        if stand in reservados:
            return f"El stand {stand} ya fue reservado."

        # Guardar reserva en CSV
        nueva_reserva = pd.DataFrame([[email, stand]], columns=["email", "stand"])
        nueva_reserva.to_csv("reserva_stands.csv", mode='a', header=not os.path.exists("reserva_stands.csv"), index=False)

        # Enviar correo de confirmación
        try:
            msg = Message("Confirmación de reserva de stand",
                          recipients=[email])
            msg.body = f"Has reservado exitosamente el stand {stand}. Gracias por tu participación."
            mail.send(msg)
        except Exception as e:
            print(f"Error al enviar correo: {e}")

        return render_template('finalizado.html', stand=stand)

    return render_template(
        'plano.html',
        email=email,
        tiempo=TIEMPO_LIMITE_MINUTOS,
        reservados=reservados,
        stands=stands,
        tiempo_milisegundos=TIEMPO_LIMITE_MINUTOS * 60 * 1000,
        start_time=start_time
    )


@app.route('/expirar', methods=['POST'])
def expirar():
    email = session.get('email')
    if not email:
        return '/', 200

    if os.path.exists("reserva_stands.csv"):
        df_reserva = pd.read_csv("reserva_stands.csv")
    else:
        df_reserva = pd.DataFrame(columns=["email", "stand"])

    if email not in df_reserva['email'].values:
        if os.path.exists("expirados.csv"):
            df_exp = pd.read_csv("expirados.csv")
        else:
            df_exp = pd.DataFrame(columns=['email'])

        if email not in df_exp['email'].values:
            df_exp = pd.concat([df_exp, pd.DataFrame([{'email': email}])], ignore_index=True)
            df_exp.to_csv("expirados.csv", index=False)

    session.clear()
    return '/expirado_espera?modo=expirado', 200

@app.route('/expirado_espera')
def expirado_espera():
    modo = request.args.get('modo', 'expirado')
    return render_template("expirado_espera.html", modo=modo)

@app.route('/admin')
def admin():
    if not os.path.exists("reserva_stands.csv"):
        reservas = []
    else:
        df = pd.read_csv("reserva_stands.csv")

        # Clasificador de tipo
        def clasificar(stand):
            stand = str(stand).strip()
            if stand in ['A','B','C','D','E','F','G','H','I']:
                return 'Patrocinador'
            elif stand.startswith('A') and stand[1:].isdigit():
                return 'Auspiciador'
            elif stand.startswith('Exp'):
                return 'Premium'
            else:
                return 'Exhibidor'

        df['tipo'] = df['stand'].apply(clasificar)
        reservas = df.to_dict(orient='records')

    return render_template("admin.html", reservas=reservas)

if __name__ == '__main__':
    app.run(debug=True)
