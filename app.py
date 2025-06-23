from flask import Flask, render_template, request, redirect, url_for, session, send_file, jsonify, flash
from flask_mail import Mail, Message
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'clave_supersecreta'

# Tiempo límite en minutos
TIEMPO_LIMITE_MINUTOS = 5

# Configuración del correo
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'avem.inscripciones@apa.org.pe'
app.config['MAIL_PASSWORD'] = 'kofr rgyf qbev rfvv'
app.config['MAIL_DEFAULT_SENDER'] = 'avem.inscripciones@apa.org.pe'
mail = Mail(app)

# Lista de stands (nombre, estilo CSS, tipo)
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulario')
def formulario():
    return render_template("formulario.html")

@app.route('/guardar_datos_cliente', methods=['POST'])
def guardar_datos_cliente():
    nombre = request.form.get('nombre', '').strip()
    empresa = request.form.get('empresa', '').strip()
    email = request.form.get('email', '').strip().lower()
    celular = request.form.get('celular', '').strip()
    pais = request.form.get('pais', '').strip()

    if not all([nombre, empresa, email, celular, pais]):
        flash("Todos los campos son obligatorios.")
        return redirect(url_for('formulario'))

    if os.path.exists("reserva_stands.csv"):
        df = pd.read_csv("reserva_stands.csv")
        fila = df[df['Email'].str.strip().str.lower() == email]

        if not fila.empty:
            empresa_existente = fila.iloc[0]['Empresa']
            stands = fila[['stand1', 'stand2']].values.flatten()
            stands = [str(s).replace('.0', '') for s in stands if pd.notna(s)]
            return render_template("ya_escogiste.html", stands=stands, empresa=empresa_existente)

    session['cliente'] = {
        'nombre': nombre,
        'empresa': empresa,
        'email': email,
        'celular': celular,
        'pais': pais,
        'inicio': int(datetime.now().timestamp() * 1000)
    }

    return redirect(url_for('plano'))



@app.route('/plano', methods=['GET', 'POST'])
def plano():
    cliente = session.get('cliente')
    if not cliente:
        return redirect(url_for('formulario'))

    email = cliente.get('email')
    start_time = cliente.get('inicio')

    # Crear archivo con columnas correctas si no existe
    if not os.path.exists("reserva_stands.csv"):
        columnas = ["Nombre", "Empresa", "Email", "Celular", "Pais", "stand1", "stand2", "Hora"]
        pd.DataFrame(columns=columnas).to_csv("reserva_stands.csv", index=False, encoding='utf-8')

    # Leer siempre como string para evitar errores como "38.0"
    df = pd.read_csv("reserva_stands.csv", dtype=str)

    # Verificar si ya tiene reservas
    fila = df[df['Email'].str.strip().str.lower() == email]
    if not fila.empty:
        seleccionados = fila[['stand1', 'stand2']].dropna(axis=1).values.flatten().tolist()
        return render_template("ya_escogiste.html", stands=seleccionados)

    # Stands reservados por usuarios
    reservados = df[['stand1', 'stand2']].values.flatten().tolist()
    reservados = [str(s).strip().replace('.0', '') for s in reservados if pd.notna(s)]

    # Agregar por defecto los stands de tipo patrocinador y auspiciador
    for nombre, _, tipo in stands:
        if tipo in ["patrocinador", "auspiciador"]:
            reservados.append(nombre)

    # Eliminar duplicados
    reservados = list(set(reservados))


    if request.method == 'POST':
        seleccion = request.form.get('stands', '').strip()
        nuevos = [s.strip() for s in seleccion.split(',') if s.strip()]
        if not nuevos or len(nuevos) > 2:
            return "Error: Selección inválida."

        if any(n in reservados for n in nuevos):
            return "Uno o más stands ya han sido reservados. Intenta nuevamente."

        # Guardar la nueva fila como texto explícitamente
        nueva_fila = {
            "Nombre": cliente['nombre'],
            "Empresa": cliente['empresa'],
            "Email": cliente['email'],
            "Celular": cliente['celular'],
            "Pais": cliente['pais'],
            "Hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "stand1": str(nuevos[0]) if len(nuevos) >= 1 else '',
            "stand2": str(nuevos[1]) if len(nuevos) == 2 else ''
        }

        df.loc[len(df)] = nueva_fila
        df.to_csv("reserva_stands.csv", index=False, encoding='utf-8')


        try:
            asunto = "🎫 Confirmación de reserva AVEM 2025"
            remitente = "RESERVAS APA <no-responder@apa.org.pe>"

            cuerpo_html = f"""
            <html>
            <body>
                <p>Hola <strong>{cliente['nombre']}</strong>,</p>

                <p>Gracias por registrarte en <strong>AVEM 2025</strong>. Esta es la confirmación de tu participación:</p>

                <ul>
                    <li><strong>📌 Empresa:</strong> {cliente['empresa']}</li>
                    <li><strong>📧 Email:</strong> {cliente['email']}</li>
                    <li><strong>📱 Celular:</strong> {cliente['celular']}</li>
                    <li><strong>🌎 País:</strong> {cliente['pais']}</li>
                </ul>

                <p><strong>🟦 Stands reservados:</strong> {', '.join(nuevos)}</p>

                <p>Nuestro equipo se pondrá en contacto contigo con los próximos pasos.</p>

                <p>Saludos,<br>Equipo AVEM</p>

                <br>
                <img src="cid:footer_img" style="max-width: 600px; width: 100%; margin-top: 30px;" alt="Footer AVEM" />
            </body>
            </html>
            """

            msg = Message(subject=asunto,
                        sender=remitente,
                        recipients=[cliente['email']])
            msg.html = cuerpo_html

            # Leer la imagen y adjuntarla como parte del HTML
            ruta_img = os.path.join(app.root_path, 'static', 'footer-apa.png')
            if os.path.exists(ruta_img):
                with open(ruta_img, 'rb') as f:
                    img_data = f.read()

                msg.attach(
                    filename='footer-apa.png',
                    content_type='image/png',
                    data=img_data,
                    disposition='inline',
                    headers={'Content-ID': '<footer_img>'}  # ✅ Diccionario en lugar de lista
                )

            mail.send(msg)

        except Exception as e:
            print("Error al enviar correo:", e)


        session.clear()
        return render_template('finalizado.html', stand=', '.join(nuevos))

    return render_template('plano.html',
                           email=email,
                           tiempo=TIEMPO_LIMITE_MINUTOS,
                           reservados=reservados,
                           stands=stands,
                           cliente=cliente,
                           tiempo_milisegundos=TIEMPO_LIMITE_MINUTOS * 60 * 1000,
                           start_time=start_time)



@app.route('/estado_stands')
def estado_stands():
    reservados = []

    if os.path.exists("reserva_stands.csv"):
        # Leer siempre como texto para evitar 38.0
        df = pd.read_csv("reserva_stands.csv", dtype=str)
        cols = [col.lower() for col in df.columns]

        if 'stand1' in cols and 'stand2' in cols:
            reservados = df[['stand1', 'stand2']].values.flatten()
        elif 'stand' in cols:
            reservados = df['stand'].values

        # Limpiar y asegurar que todos sean texto
        reservados = [str(s).strip() for s in reservados if pd.notna(s)]

    return jsonify(reservados)


@app.route('/verificar_disponibilidad/<stand>')
def verificar_disponibilidad(stand):
    stand = stand.strip()
    if os.path.exists("reserva_stands.csv"):
        df = pd.read_csv("reserva_stands.csv", dtype=str)
        if 'stand1' in df.columns and 'stand2' in df.columns:
            reservados = df[['stand1', 'stand2']].values.flatten()
            reservados = [str(s).strip() for s in reservados if pd.notna(s)]
            if stand in reservados:
                return jsonify({'disponible': False})
    return jsonify({'disponible': True})



@app.route('/descargar_csv')
def descargar_csv():
    if os.path.exists("reserva_stands.csv"):
        return send_file("reserva_stands.csv", as_attachment=True)
    return "Archivo no encontrado", 404


@app.route('/admin')
def admin():
    filtro_tipo = request.args.get('tipo')
    
    if os.path.exists("reserva_stands.csv"):
        df = pd.read_csv("reserva_stands.csv")
    else:
        df = pd.DataFrame(columns=["Email", "stand1", "stand2"])

    # Extraer lista de stands reservados
    reservados = []
    for col in ['stand1', 'stand2']:
        if col in df.columns:
            reservados.extend(
                df[col]
                .dropna()
                .astype(str)
                .str.strip()
                .str.replace(r'\.0$', '', regex=True)
                .tolist()
            )

    # Agregar por defecto los stands de tipo patrocinador y auspiciador
    for nombre, _, tipo in stands:
        if tipo in ["patrocinador", "auspiciador"]:
            reservados.append(nombre)

    # Eliminar duplicados
    reservados = list(set(reservados))


    # Preparar dataframe para estadísticas
    columnas_presentes = [col for col in ['stand1', 'stand2'] if col in df.columns]
    if columnas_presentes:
        df_melt = df.melt(id_vars=['Email'], value_vars=columnas_presentes,
                          var_name='col', value_name='stand')
        df_melt.dropna(subset=['stand'], inplace=True)
        df_melt['stand'] = df_melt['stand'].astype(str).str.strip()
    else:
        df_melt = pd.DataFrame(columns=['Email', 'stand'])

    # Clasificar tipo de stand
    def clasificar(stand):
        if stand in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']:
            return 'Patrocinador'
        elif stand.startswith('A') and stand[1:].isdigit():
            return 'Auspiciador'
        elif stand.startswith('Exp'):
            return 'Premium'
        return 'Exhibidor'

    df_melt['tipo'] = df_melt['stand'].apply(clasificar)

    # Aplicar filtro si corresponde
    if filtro_tipo:
        df_melt = df_melt[df_melt['tipo'] == filtro_tipo]

    # Conteo por tipo
    conteo = df_melt['tipo'].value_counts().to_dict()
    for tipo in ['Exhibidor', 'Premium', 'Auspiciador', 'Patrocinador']:
        conteo.setdefault(tipo, 0)

    return render_template("admin.html",
                           reservados=reservados,
                           stands=stands,
                           conteo=conteo,
                           total_reservas=len(df_melt),
                           filtro_tipo=filtro_tipo,
                           stats=conteo,
                           reservas=df_melt.to_dict(orient='records'))


if __name__ == '__main__':
    app.run(debug=True)