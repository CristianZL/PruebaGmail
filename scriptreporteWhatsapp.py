import pandas as pd
from fpdf import FPDF
import pywhatkit
import os
import datetime

# Cargar datos
archivo = "datos.xlsx"
df = pd.read_excel(archivo, sheet_name="Datos")
contactos = pd.read_excel(archivo, sheet_name="Contactos")

# Filtrar por observación
df_filtrado = df[df["Observación"] == "No impreso"]

# Crear carpeta de salida
carpeta_pdf = "reportes_pdf"
os.makedirs(carpeta_pdf, exist_ok=True)

# Agrupar por asesor
asesores = df_filtrado["Asesor"].unique()

for asesor in asesores:
    df_asesor = df_filtrado[df_filtrado["Asesor"] == asesor]
    telefono_row = contactos[contactos["Asesor"] == asesor]

    if telefono_row.empty:
        print(f"No se encontró número para {asesor}")
        continue

    telefono = str(telefono_row.iloc[0]["WhatsApp"])

    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Reporte de {asesor}", ln=True, align='C')

    for index, row in df_asesor.iterrows():
        texto = f"{row['Fecha']} - {row['Producto']} - ${row['Valor']}"
        pdf.cell(200, 10, texto, ln=True)

    pdf_path = os.path.join(carpeta_pdf, f"{asesor}.pdf")
    pdf.output(pdf_path)

    # Enviar por WhatsApp
    ahora = datetime.datetime.now()
    hora = ahora.hour
    minuto = ahora.minute + 2  # enviar 2 minutos después de ejecutar

    print(f"Enviando reporte de {asesor} a {telefono}...")

    pywhatkit.sendwhats_image(
        phone_no=f"+{telefono}",
        img_path=pdf_path,
        caption=f"Buenas tardes {asesor}, aquí está tu reporte de hoy 📄",
        wait_time=20,
        tab_close=True
    )

print("¡Todos los reportes han sido enviados!")
