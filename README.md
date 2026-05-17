# Pulso Retail

Aplicación Django simple para subir un CSV de ventas, validar cada fila y guardar los registros limpios en una tabla única `FactVenta`.

## Estructura del proyecto

- `arquitecturadatos/` - configuración del proyecto Django.
- `ventas/` - app principal con el modelo `FactVenta`, vistas y lógica de carga CSV.
- `ventas/templates/ventas/` - templates para la carga y el panel de resultados.

## Requisitos

- Python 3.11+
- Django 4.2+

## Configuración

1. Crear un entorno virtual:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. El proyecto usa MySQL según el requerimiento del curso. Antes de ejecutar migraciones asegúrate de haber creado la base de datos y el usuario en tu servidor MySQL/MariaDB.
3. Pasos rápidos para configurar MySQL local (ej. con XAMPP o MySQL):

    - Crear base de datos y usuario (ejemplo desde consola MySQL):

       ```sql
       CREATE DATABASE rikdata CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
       CREATE USER 'rikuser'@'localhost' IDENTIFIED BY 'tu_password';
       GRANT ALL PRIVILEGES ON rikdata.* TO 'rikuser'@'localhost';
       FLUSH PRIVILEGES;
       ```

    - Instalar dependencias en tu entorno virtual:

       ```powershell
       .\.venv\Scripts\python.exe -m pip install -r requirements.txt
       ```

    - Actualizar `arquitecturadatos/settings.py` si tus credenciales o host/puerto son distintas (campo `DATABASES`).

    - Ejecutar migraciones y crear las tablas en MySQL:

       ```powershell
       .\.venv\Scripts\python.exe manage.py migrate
       ```
5. Crear un superusuario (opcional):
   ```bash
   python manage.py createsuperuser
   ```
6. Iniciar el servidor:
   ```bash
   python manage.py runserver
   ```

## Uso

- Visitar `http://127.0.0.1:8000/` para subir el CSV.
- Visitar `http://127.0.0.1:8000/panel/` para ver los resultados.
- El archivo de ejemplo `sample_ventas.csv` está disponible en la raíz del proyecto.

## Notas sobre MySQL

- El proyecto ahora usa MySQL como base de datos por defecto. Se utiliza `PyMySQL` como driver (está listado en `requirements.txt`).
- Si utilizas `XAMPP` activa el servicio de MariaDB/MySQL y usa phpMyAdmin para crear la base de datos siguiendo los pasos anteriores.
- Si prefieres que deje preparada una configuración alternativa o un script de creación, dímelo y lo agrego.

## Formato CSV esperado

El CSV debe contener estas columnas exactas:

`cliente,email,region,producto,categoria,marca,tienda,ciudad,tipo_tienda,fecha,cantidad,monto`

## Comportamiento

- El CSV se lee con `csv.DictReader`.
- Se eliminan filas duplicadas.
- Se validan fecha, email, cantidad y monto.
- Los registros se guardan en la tabla `FactVenta`.
- Los registros con errores conservan el texto de error en la columna `errores`.
