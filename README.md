# 📦 UNITY PERÚ SAC – Sistema de Gestión de Almacén

Aplicación web desarrollada con **Streamlit** para el control y gestión del almacén de UNITY PERÚ SAC: inventario de productos, entradas, salidas, guías de remisión, reportes y administración de usuarios con roles.


## 📸 Capturas de pantalla

Login 
<img width="1422" height="843" alt="Captura de pantalla 2026-07-03 103835" src="https://github.com/user-attachments/assets/c4a6efbe-5947-4cf1-9fd2-e7aad2c95536" />
Dashboard
<img width="1903" height="852" alt="Captura de pantalla 2026-07-03 103918" src="https://github.com/user-attachments/assets/60e41b63-362c-4b77-9a9d-ade52ef556f7" />
Productos
<img width="1891" height="860" alt="Captura de pantalla 2026-07-03 103930" src="https://github.com/user-attachments/assets/b3fdb6b7-5ead-430d-a56c-2511516f59e8" />
Entradas / Salidas
<img width="1886" height="854" alt="Captura de pantalla 2026-07-03 103942" src="https://github.com/user-attachments/assets/3f1c54d4-530c-4b3e-93cd-d6203f8fbda7" />
 


## ✨ Características

- **Inicio de sesión** con selección de usuario y contraseña, control de acceso por roles.
- **Dashboard** con KPIs (productos totales, ingresos del mes, salidas del mes, alertas de stock bajo) y gráficos con Plotly.
- **Gestión de productos**: catálogo, categorías (Laptops, Monitores, Accesorios, Impresoras, Almacenamiento, etc.), stock y precios, búsqueda y filtros.
- **Entradas de almacén**: listado, búsqueda y filtro por estado (Completa, Pendiente, Con Observación).
- **Salidas de almacén**: listado, búsqueda y filtro por estado (Despachado, En Tránsito, Entregado, Pendiente).
- **Guías de remisión**: listado, búsqueda, estado y verificación de firma del cliente.
- **Reportes**: accesos rápidos a reportes de inventario, entradas, salidas, productos, fechas y movimientos.
- **Usuarios y roles** (solo Administrador): Administrador, Almacenero, Logística, Operario.
- Interfaz personalizada con estilos CSS propios (tema claro, sidebar oscuro, tarjetas KPI, tablas y badges de estado).
- Conexión a **SQL Server** con `pyodbc` (driver de Microsoft) y respaldo automático con `pymssql` cuando el driver ODBC no está disponible (por ejemplo, en Streamlit Cloud).
- Modo de datos de muestra: si la base de datos no está disponible o las tablas están vacías, la app muestra datos de ejemplo para poder navegar la interfaz igualmente.

## 🛠️ Tecnologías

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Plotly](https://plotly.com/python/)
- [SQL Server](https://www.microsoft.com/sql-server) (`pyodbc` / `pymssql`)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- Python 3.9+

## 📁 Estructura del proyecto

```
gestion_almacen/
├── app.py                     # Aplicación principal (Streamlit)
├── requirements.txt           # Dependencias de Python
├── packages.txt                # Dependencias del sistema (drivers ODBC/FreeTDS)
└── .streamlit/
    ├── config.toml             # Tema y configuración de Streamlit
    └── secrets.toml            # Credenciales de conexión (NO subir a GitHub)
```

## ⚙️ Requisitos previos

- Python 3.9 o superior
- Una instancia de **SQL Server** accesible (local o remota) con la base de datos `ALMACEN_UNITY`
- En Windows/local: [ODBC Driver 17 for SQL Server](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)
- En Linux / Streamlit Cloud: `unixodbc`, `unixodbc-dev`, `freetds-dev`, `freetds-bin` (ya listados en `packages.txt`)

## 🚀 Instalación local

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/gestion_almacen.git
   cd gestion_almacen
   ```

2. Crea y activa un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate      # En Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Configura tus credenciales de base de datos (ver sección siguiente).

5. Ejecuta la aplicación:
   ```bash
   streamlit run app.py
   ```

6. Abre tu navegador en `http://localhost:8501`.

## 🔐 Configuración de credenciales

La app lee las credenciales de conexión desde `st.secrets`. Crea tu propio archivo `.streamlit/secrets.toml` (este archivo **no debe subirse a GitHub**) con el siguiente formato:

```toml
[db]
server = "TU_SERVIDOR"
database = "ALMACEN_UNITY"
username = "TU_USUARIO"
password = "TU_CONTRASEÑA"
```

> ⚠️ **Importante sobre seguridad:** el archivo `.streamlit/secrets.toml` de este proyecto contiene actualmente una contraseña real en texto plano, y `app.py` también tiene credenciales por defecto "hardcodeadas" como respaldo. Antes de subir el proyecto a GitHub:
> 1. Agrega `.streamlit/secrets.toml` a tu `.gitignore`.
> 2. Elimina o reemplaza las credenciales por defecto dentro de `app.py`.
> 3. Cambia la contraseña de la base de datos si el repositorio llegó a subirse con la contraseña real en algún momento.

Ejemplo de `.gitignore` recomendado:
```
.streamlit/secrets.toml
__pycache__/
*.pyc
venv/
```

## ☁️ Despliegue en Streamlit Cloud

1. Sube el repositorio a GitHub (sin el archivo `secrets.toml`).
2. Crea una nueva app en [Streamlit Community Cloud](https://streamlit.io/cloud) apuntando a `app.py`.
3. En **Settings → Secrets**, agrega tus credenciales con el mismo formato mostrado arriba (`[db]`).
4. Streamlit Cloud no permite instalar el driver ODBC de Microsoft; por eso la app usa automáticamente `pymssql` como respaldo (definido en `packages.txt` y en la lógica de conexión de `app.py`).

## 👥 Roles de usuario

| Rol | Permisos |
|---|---|
| **Administrador** | Acceso completo, incluida la gestión de usuarios y roles |
| **Almacenero** | Gestión de productos, entradas y salidas |
| **Logística** | Gestión de entradas, salidas y guías de remisión |
| **Operario** | Acceso a las secciones operativas del almacén |

## 🗺️ Roadmap

- [ ] Formulario funcional para registrar nuevas entradas
- [ ] Formulario funcional para registrar nuevas salidas
- [ ] Formulario funcional para nuevas guías de remisión
- [ ] Alta de nuevos usuarios desde la interfaz
- [ ] Generación real de reportes (exportación a PDF / Excel)
- [ ] Hash seguro de contraseñas (actualmente se compara en texto plano)

## ✍️ Autor

Desarrollado por estudiantes
