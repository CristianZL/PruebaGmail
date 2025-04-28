import os
import time
from playwright.sync_api import sync_playwright

# Ruta para guardar la sesión
USER_DATA_DIR = "C:/Users/Cristian/Documents/PruebaGmail/session_whatsapp"

def enviar_por_whatsapp_playwright(context, telefono, mensaje, archivo_pdf):
    page = context.new_page()

    try:
        print(f"⏳ Buscando número {telefono} en WhatsApp...")
        page.goto(f"https://web.whatsapp.com/send?phone={telefono}&text={mensaje}", timeout=60000)

        # Esperar por si aparece el botón "Continuar al chat"
        try:
            continuar_btn = page.wait_for_selector("a[href*='send']", timeout=5000)
            if continuar_btn:
                print("➡️ Haciendo clic en 'Continuar al chat'...")
                continuar_btn.click()
                time.sleep(5)
        except Exception:
            # No apareció el botón, no pasa nada
            pass

        # Esperar que cargue el área de escribir mensaje
        page.wait_for_selector("div[contenteditable='true']", timeout=60000)

        # Presionar Enter para enviar mensaje de texto
        input_box = page.query_selector("div[contenteditable='true']")
        if input_box:
            input_box.press('Enter')
            time.sleep(2)
        else:
            raise Exception("❌ No se encontró el área de mensajes.")

        # Esperar el botón de adjuntar (clip) y hacer clic en él
        page.wait_for_selector("span[data-icon='clip']", timeout=60000)  # Aumento del timeout
        clip_button = page.query_selector("span[data-icon='clip']")
        if clip_button:
            clip_button.click()
            time.sleep(2)
        else:
            raise Exception("❌ No se encontró el botón de adjuntar.")

        # Adjuntar el archivo
        file_input = page.query_selector("input[type='file']")
        if file_input:
            file_input.set_input_files(archivo_pdf)
            time.sleep(2)
        else:
            raise Exception("❌ No se encontró el campo para adjuntar archivos.")

        # Esperar el botón de enviar y hacer clic en él
        page.wait_for_selector("span[data-icon='send']", timeout=30000)
        send_button = page.query_selector("span[data-icon='send']")
        if send_button:
            send_button.click()
            time.sleep(5)
        else:
            raise Exception("❌ No se encontró el botón de enviar.")

        print(f"✅ Enviado a {telefono}")

    except Exception as e:
        print(f"❌ Error al enviar mensaje a {telefono}: {e}")
        with open('errores_envio.txt', 'a') as log:
            log.write(f"{telefono} - Error: {str(e)}\n")

    finally:
        page.close()

def main():
    print("🌐 Iniciando navegador con Playwright...")

    with sync_playwright() as p:
        # Crear el navegador usando un perfil persistente
        browser = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,
            args=["--start-maximized"]
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://web.whatsapp.com")

        # Si la sesión no está guardada, escanear el código QR
        if not os.path.exists(os.path.join(USER_DATA_DIR, 'Default')):
            input("📱 Escanea el código QR de WhatsApp y presiona Enter para continuar...")

        # Lista de contactos a los que se les enviará el reporte
        contactos = [
            {"nombre": "Cristian", "telefono": "573026592764", "archivo": "reporte_cristian.pdf"},
            {"nombre": "Andres", "telefono": "573205104637", "archivo": "reporte_andres.pdf"}
        ]

        for contacto in contactos:
            print(f"📄 Generando reporte para {contacto['nombre']}...")
            enviar_por_whatsapp_playwright(
                browser,
                contacto['telefono'],
                f"Hola {contacto['nombre']}, aquí tienes tu reporte 📄",
                contacto['archivo']
            )

        print("🎉 Proceso finalizado con éxito.")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    main()
