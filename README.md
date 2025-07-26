# Rappi Data Extractor 📊🛒

Este proyecto automatiza el proceso de login, extracción de token y recopilación de datos de ventas de sucursales desde el portal de **Rappi Partners**, integrando además la lectura de IDs desde una hoja de cálculo de **Google Sheets** y exportando los resultados a un archivo CSV.

---

## 🧰 Tecnologías usadas

- Python 3.x
- Selenium
- gspread (Google Sheets API)
- python-dotenv
- requests
- CSV (módulo estándar)

---

## ▶️ Cómo ejecutar

1. Instalá las dependencias necesarias:

```bash
pip install selenium gspread python-dotenv google-auth requests
```

2. Colocá el archivo `sheet-api-python.json` en la raíz (este contiene las credenciales de tu cuenta de servicio de Google).

3. Ejecutá el script:

```bash
python app.py
```

---

## ⚙️ Funcionalidad

- Hace login automático en la web de Rappi Partners.
- Extrae el token desde `localStorage` del navegador.
- Obtiene IDs de sucursales desde Google Sheets.
- Realiza múltiples peticiones POST a la API interna de Rappi con fechas iterativas.
- Exporta los resultados a `datos.csv`.

---

## 📌 Notas

- El script fue diseñado con `ChromeDriver`, asegurate de tenerlo instalado y en el `PATH`.
- Maneja 2FA y ventanas emergentes de forma automatizada.
- La autenticación con Google Sheets se realiza en modo solo lectura.
- Por seguridad, los datos sensibles se manejan vía `.env`.

---

## ✍️ Autor

Desarrollado por **Nikpedroza**