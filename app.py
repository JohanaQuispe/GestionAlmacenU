import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import hashlib
import time

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="UNITY PERÚ SAC - Gestión de Almacén",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONSTANTES DE CONEXIÓN ---
# Las credenciales se leen desde st.secrets (Streamlit Cloud -> Settings -> Secrets).
# En local, si no existen en st.secrets, usa estos valores por defecto para no romper
# el desarrollo en tu propia máquina.
try:
    SERVER = st.secrets["db"]["server"]
    DATABASE = st.secrets["db"]["database"]
    USERNAME = st.secrets["db"]["username"]
    PASSWORD = st.secrets["db"]["password"]
except Exception:
    SERVER = 'localhost'
    DATABASE = 'ALMACEN_UNITY'
    USERNAME = 'sa'
    PASSWORD = 'leoyjoha13'

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .main { background-color: #f1f5f9; }
    div.block-container { padding-top: 1.2rem; }

    /* ---------- TIPOGRAFÍA GENERAL ---------- */
    .unity-title {
        color: #0f172a;
        font-weight: 700;
        font-size: 1.9rem;
        margin-bottom: 0.1rem;
    }
    .unity-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        margin-bottom: 1.3rem;
    }

    /* ---------- TOPBAR ---------- */
    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: white;
        padding: 0.8rem 1.4rem;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        margin-bottom: 1.4rem;
    }
    .topbar .tb-titles h1 {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
    }
    .topbar .tb-titles p {
        font-size: 0.8rem;
        color: #94a3b8;
        margin: 0;
    }
    .topbar .tb-right {
        display: flex;
        align-items: center;
        gap: 1.1rem;
    }
    .tb-bell {
        position: relative;
        font-size: 1.3rem;
        color: #64748b;
    }
    .tb-bell .tb-badge {
        position: absolute;
        top: -6px;
        right: -8px;
        background: #ef4444;
        color: white;
        font-size: 0.6rem;
        font-weight: 700;
        border-radius: 50%;
        padding: 1px 5px;
    }
    .tb-user {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .tb-avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .tb-user .tb-name { font-size: 0.85rem; font-weight: 600; color: #1e293b; }
    .tb-user .tb-role { font-size: 0.7rem; color: #94a3b8; }

    /* ---------- KPI CARDS ---------- */
    .kpi-card {
        background: white;
        padding: 1rem 1.2rem;
        border-radius: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border-left: 4px solid #3b82f6;
        transition: transform 0.15s;
        height: 100%;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.08);
    }
    .kpi-card .kpi-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
    }
    .kpi-card .kpi-icon {
        font-size: 1.3rem;
        opacity: 0.85;
    }
    .kpi-card .kpi-label {
        font-size: 0.72rem;
        color: #94a3b8;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .kpi-card .kpi-value {
        font-size: 1.7rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0.15rem 0;
    }
    .kpi-card .kpi-delta {
        font-size: 0.72rem;
        color: #64748b;
    }
    .kpi-card.blue-light { border-left-color: #3b82f6; }
    .kpi-card.green-light { border-left-color: #22c55e; }
    .kpi-card.orange-light { border-left-color: #f59e0b; }
    .kpi-card.purple-light { border-left-color: #a855f7; }
    .kpi-card.red-light { border-left-color: #ef4444; }

    /* ---------- SIDEBAR ---------- */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #16213e 0%, #0d1b30 100%) !important;
        padding-top: 0.5rem;
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }

    .sidebar-logo {
        text-align: center;
        padding: 1rem 0 1.1rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 0.8rem;
    }
    .sidebar-logo .logo-box {
        width: 34px;
        height: 34px;
        margin: 0 auto 0.4rem auto;
        background: white;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1rem;
    }
    .sidebar-logo .logo-box span { color: #16213e !important; }
    .sidebar-logo h2 {
        font-weight: 700;
        font-size: 1.05rem;
        margin: 0;
        letter-spacing: 0.5px;
        color: white !important;
    }
    .sidebar-logo p {
        font-size: 0.68rem;
        opacity: 0.55;
        margin: 0;
    }

    .sidebar-section-label {
        font-size: 0.65rem;
        font-weight: 700;
        letter-spacing: 0.6px;
        opacity: 0.4;
        text-transform: uppercase;
        margin: 0.6rem 0 0.3rem 0.4rem;
    }

    .user-info {
        padding: 0.7rem 0.9rem;
        background: rgba(255,255,255,0.06);
        border-radius: 10px;
        margin: 0.6rem 0 0.8rem 0;
    }
    .user-info .user-name { font-size: 0.88rem; font-weight: 700; color: white !important; margin: 0; }
    .user-info .user-detail { font-size: 0.68rem; color: rgba(255,255,255,0.45) !important; margin: 0; }
    .user-info .user-role {
        display: inline-block;
        padding: 0.1rem 0.55rem;
        border-radius: 12px;
        font-size: 0.6rem;
        font-weight: 700;
        background: #3b82f6;
        color: white !important;
        margin-top: 0.3rem;
    }

    [data-testid="stSidebar"] .stButton > button {
        background: transparent;
        color: rgba(255,255,255,0.75) !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 0.8rem;
        font-weight: 500;
        text-align: left;
        justify-content: flex-start;
        transition: all 0.15s;
        width: 100%;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.08);
        color: white !important;
    }
    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(59,130,246,0.35);
    }

    /* ---------- BOTONES GENERALES ---------- */
    .main .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        border: none;
        border-radius: 9px;
        padding: 0.55rem 1rem;
        font-weight: 600;
        font-size: 0.85rem;
        transition: all 0.2s;
        width: 100%;
    }
    .main .stButton > button:hover {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59,130,246,0.3);
    }

    /* ---------- LOGIN ---------- */
    .login-panel-dark {
        background: linear-gradient(160deg, #16213e 0%, #0d1b30 100%);
        border-radius: 18px;
        padding: 3rem 2rem;
        text-align: center;
        color: white;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        min-height: 480px;
    }
    .login-panel-dark .logo-box-lg {
        width: 50px;
        height: 50px;
        margin: 0 auto 0.9rem auto;
        background: white;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        color: #16213e;
        font-size: 1.4rem;
    }
    .login-panel-dark h1 {
        color: white;
        font-size: 1.5rem;
        letter-spacing: 1px;
        margin-bottom: 0.1rem;
    }
    .login-panel-dark p {
        color: rgba(255,255,255,0.55);
        font-size: 0.85rem;
    }
    .login-panel-dark .deco {
        margin-top: 1.8rem;
        font-size: 2.2rem;
        opacity: 0.8;
    }
    .login-container {
        background: white;
        padding: 2.6rem 2.4rem;
        border-radius: 18px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.06);
        min-height: 480px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .login-title {
        text-align: center;
        color: #1e293b;
        font-size: 1.7rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .login-subtitle {
        text-align: center;
        color: #94a3b8;
        margin-bottom: 1.6rem;
        font-size: 0.9rem;
    }

    /* ---------- BADGES ---------- */
    .badge {
        display: inline-block;
        padding: 0.22rem 0.65rem;
        border-radius: 20px;
        font-size: 0.68rem;
        font-weight: 700;
        white-space: nowrap;
    }
    .badge-success { background: #dcfce7; color: #166534; }
    .badge-danger { background: #fee2e2; color: #991b1b; }
    .badge-warning { background: #fef3c7; color: #92400e; }
    .badge-info { background: #dbeafe; color: #1e40af; }
    .badge-gray { background: #f1f5f9; color: #475569; }

    /* ---------- TABLA PERSONALIZADA ---------- */
    .table-card {
        background: white;
        border-radius: 14px;
        padding: 1.1rem 1.2rem 0.6rem 1.2rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.83rem;
    }
    .custom-table thead th {
        text-align: left;
        color: #94a3b8;
        text-transform: uppercase;
        font-size: 0.65rem;
        letter-spacing: 0.4px;
        font-weight: 700;
        padding: 0.55rem 0.7rem;
        border-bottom: 1px solid #e2e8f0;
        white-space: nowrap;
    }
    .custom-table tbody td {
        padding: 0.65rem 0.7rem;
        border-bottom: 1px solid #f1f5f9;
        color: #334155;
        white-space: nowrap;
    }
    .custom-table tbody tr:hover td { background: #f8fafc; }
    .custom-table .mono { font-weight: 600; color: #1e293b; }
    .custom-table .muted { color: #94a3b8; font-size: 0.78rem; }
    .table-caption {
        color: #94a3b8;
        font-size: 0.78rem;
        margin: 0.6rem 0 1rem 0.2rem;
    }
    .check-yes { color: #16a34a; font-weight: 800; }
    .check-no { color: #dc2626; font-weight: 800; }

    /* ---------- ACCIONES RÁPIDAS ---------- */
    .quick-actions-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e293b;
        margin: 0.4rem 0 0.6rem 0.1rem;
    }

    /* ---------- MOVIMIENTOS RECIENTES (lista) ---------- */
    .move-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.55rem 0.2rem;
        border-bottom: 1px solid #f1f5f9;
    }
    .move-item:last-child { border-bottom: none; }
    .move-left { display: flex; flex-direction: column; gap: 0.15rem; }
    .move-title { font-size: 0.82rem; font-weight: 600; color: #1e293b; }
    .move-sub { font-size: 0.72rem; color: #94a3b8; }
    .move-time { font-size: 0.7rem; color: #cbd5e1; white-space: nowrap; }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE CONEXIÓN ---
def _obtener_conexion():
    """
    Crea la conexión a SQL Server.
    Intenta primero con pyodbc + el driver de Microsoft (típico en tu PC local).
    Si no está disponible (como en Streamlit Cloud, que no permite instalar el
    driver de Microsoft), usa pymssql como respaldo, que no lo necesita.
    Devuelve (conexion, estilo_de_parametro).
    """
    try:
        import pyodbc
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};"
            "TrustServerCertificate=yes;"
        )
        conn = pyodbc.connect(conn_str, timeout=30)
        return conn, "qmark"
    except Exception:
        import pymssql
        conn = pymssql.connect(
            server=SERVER, user=USERNAME, password=PASSWORD,
            database=DATABASE, timeout=30
        )
        return conn, "pyformat"

def _adaptar_query(query, estilo):
    """Convierte los placeholders '?' (pyodbc) a '%s' (pymssql) si hace falta."""
    if estilo == "pyformat":
        return query.replace("?", "%s")
    return query

def ejecutar_consulta(query, params=None):
    conn = None
    try:
        conn, estilo = _obtener_conexion()
        query = _adaptar_query(query, estilo)
        if params:
            df = pd.read_sql(query, conn, params=params)
        else:
            df = pd.read_sql(query, conn)
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass

def ejecutar_comando(query, params=None):
    conn = None
    try:
        conn, estilo = _obtener_conexion()
        query = _adaptar_query(query, estilo)
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass


# --- FUNCIONES DE AUTENTICACIÓN ---
@st.cache_data(ttl=60)
def obtener_usuarios():
    query = """
        SELECT usuario, nombre, rol
        FROM usuarios_sistema
        WHERE activo = 1
        ORDER BY nombre
    """
    df = ejecutar_consulta(query)
    if df.empty:
        return pd.DataFrame([
            {"usuario": "JohanaQuispe", "nombre": "Johana Quispe", "rol": "Administrador"},
            {"usuario": "IngridAbyar", "nombre": "Ingrid Aybar", "rol": "Administrador"},
            {"usuario": "KeyLachoque", "nombre": "Keyla Choque", "rol": "Almacenero"},
            {"usuario": "KennyChucari", "nombre": "Kenny Chucari", "rol": "Logistica"},
            {"usuario": "LeonelDsetole", "nombre": "Leonel Sotelo", "rol": "Operario"},
        ])
    return df

def autenticar_usuario(usuario, password):
    query = """
        SELECT usuario, password_hash, nombre, rol
        FROM usuarios_sistema
        WHERE usuario = ? AND activo = 1
    """
    df = ejecutar_consulta(query, params=[usuario])
    if not df.empty:
        if df.iloc[0]['password_hash'] == password:
            update_query = """
                UPDATE usuarios_sistema
                SET ultimo_acceso = GETDATE()
                WHERE usuario = ?
            """
            ejecutar_comando(update_query, params=[usuario])
            return True, df.iloc[0]['nombre'], df.iloc[0]['rol']
    return False, None, None

# --- CATÁLOGO AMPLIADO DE PRODUCTOS (datos de muestra) ---
def _catalogo_muestra():
    filas = [
        # codigo, descripcion, categoria, marca, unidad, stock, precio, ubicacion
        ("ART001", "Laptop HP 14\" Core i5", "Laptops", "HP", "UND", 45, 2650.00, "A-01-01"),
        ("ART002", "Laptop Dell Inspiron 15", "Laptops", "Dell", "UND", 28, 2450.00, "A-01-02"),
        ("ART003", "Laptop Lenovo ThinkPad E14", "Laptops", "Lenovo", "UND", 19, 3100.00, "A-01-03"),
        ("ART004", "Laptop Asus VivoBook 15", "Laptops", "Asus", "UND", 33, 2200.00, "A-01-04"),
        ("ART005", "Laptop Acer Aspire 5", "Laptops", "Acer", "UND", 22, 2050.00, "A-01-05"),
        ("ART006", "Laptop HP Pavilion x360", "Laptops", "HP", "UND", 12, 2890.00, "A-01-06"),
        ("ART007", "Laptop Dell Latitude 5420", "Laptops", "Dell", "UND", 9, 3450.00, "A-01-07"),
        ("ART008", "Laptop Lenovo IdeaPad 3", "Laptops", "Lenovo", "UND", 26, 1980.00, "A-01-08"),
        ("ART009", "Monitor LG 27\" 4K", "Monitores", "LG", "UND", 30, 1350.00, "B-02-01"),
        ("ART010", "Monitor Samsung 24\" FHD", "Monitores", "Samsung", "UND", 41, 620.00, "B-02-02"),
        ("ART011", "Monitor AOC 21.5\" LED", "Monitores", "AOC", "UND", 37, 430.00, "B-02-03"),
        ("ART012", "Monitor HP 24\" IPS", "Monitores", "HP", "UND", 24, 590.00, "B-02-04"),
        ("ART013", "Monitor Dell 27\" UltraSharp", "Monitores", "Dell", "UND", 15, 1580.00, "B-02-05"),
        ("ART014", "Monitor LG 22\" Full HD", "Monitores", "LG", "UND", 29, 480.00, "B-02-06"),
        ("ART015", "Monitor ViewSonic 24\"", "Monitores", "ViewSonic", "UND", 18, 560.00, "B-02-07"),
        ("ART016", "Mouse Óptico Logitech", "Accesorios", "Logitech", "UND", 75, 35.00, "C-03-01"),
        ("ART017", "Teclado Inalámbrico Logitech", "Accesorios", "Logitech", "UND", 60, 89.00, "C-03-02"),
        ("ART018", "Teclado Mecánico Redragon", "Accesorios", "Redragon", "UND", 22, 149.00, "C-03-03"),
        ("ART019", "Mousepad Gamer XL", "Accesorios", "Genérico", "UND", 54, 28.00, "C-03-04"),
        ("ART020", "Webcam HD Logitech C920", "Accesorios", "Logitech", "UND", 17, 249.00, "C-03-05"),
        ("ART021", "Audífonos USB con Micrófono", "Accesorios", "HyperX", "UND", 33, 119.00, "C-03-06"),
        ("ART022", "Hub USB-C 6 en 1", "Accesorios", "Ugreen", "UND", 40, 99.00, "C-03-07"),
        ("ART023", "Cable HDMI 2m", "Accesorios", "Genérico", "UND", 88, 22.00, "C-03-08"),
        ("ART024", "Adaptador USB-C a HDMI", "Accesorios", "Ugreen", "UND", 46, 45.00, "C-03-09"),
        ("ART025", "Base Refrigerante para Laptop", "Accesorios", "Genérico", "UND", 31, 65.00, "C-03-10"),
        ("ART026", "Impresora Epson L3250", "Impresoras", "Epson", "UND", 20, 780.00, "D-04-01"),
        ("ART027", "Impresora HP LaserJet Pro M15w", "Impresoras", "HP", "UND", 14, 690.00, "D-04-02"),
        ("ART028", "Impresora Canon Pixma G2160", "Impresoras", "Canon", "UND", 11, 720.00, "D-04-03"),
        ("ART029", "Impresora Epson EcoTank L4260", "Impresoras", "Epson", "UND", 9, 950.00, "D-04-04"),
        ("ART030", "Impresora Brother HL-L2350DW", "Impresoras", "Brother", "UND", 7, 810.00, "D-04-05"),
        ("ART031", "Impresora HP DeskJet 2775", "Impresoras", "HP", "UND", 16, 420.00, "D-04-06"),
        ("ART032", "Disco Duro Externo 1TB", "Almacenamiento", "Seagate", "UND", 25, 240.00, "A-02-01"),
        ("ART033", "SSD Kingston 480GB", "Almacenamiento", "Kingston", "UND", 34, 175.00, "A-02-02"),
        ("ART034", "USB Kingston 32GB", "Almacenamiento", "Kingston", "UND", 90, 25.00, "A-02-03"),
        ("ART035", "Memoria RAM 8GB DDR4", "Almacenamiento", "Kingston", "UND", 42, 130.00, "A-02-04"),
        ("ART036", "Estabilizador de Voltaje 1000W", "Otros", "Forza", "UND", 21, 95.00, "E-05-01"),
        ("ART037", "UPS Regulador 600VA", "Otros", "Forza", "UND", 13, 189.00, "E-05-02"),
        ("ART038", "Silla Ergonómica de Oficina", "Otros", "Genérico", "UND", 8, 450.00, "E-05-03"),
        ("ART039", "Extensión Eléctrica 5 Tomas", "Otros", "Genérico", "UND", 58, 32.00, "E-05-04"),
        ("ART040", "Ventilador USB para Laptop", "Otros", "Genérico", "UND", 27, 55.00, "E-05-05"),
    ]
    df = pd.DataFrame(filas, columns=[
        "codigo", "descripcion", "categoria", "marca", "unidad", "stock", "precio", "ubicacion"
    ])
    # días en inventario, determinísticos por código (para el gráfico de antigüedad)
    df["dias_inventario"] = [(int(c[3:]) * 7) % 55 + 1 for c in df["codigo"]]
    return df

# --- FUNCIONES DE CARGA DE DATOS ---
@st.cache_data(ttl=300)
def cargar_productos():
    query = """
        SELECT
            Cod_Articulo as codigo,
            Descripcion as descripcion,
            Unidad_Medida as unidad,
            Stock_Actual as stock,
            Precio_Unitario as precio
        FROM articulo
        WHERE Activo = 1
        ORDER BY Cod_Articulo
    """
    df = ejecutar_consulta(query)
    if df.empty:
        return _catalogo_muestra()
    return df

@st.cache_data(ttl=300)
def cargar_categorias():
    df = cargar_productos()
    if not df.empty:
        if 'categoria' in df.columns:
            return df
        categorias = []
        for desc in df['descripcion']:
            d = desc.lower()
            if 'laptop' in d:
                categorias.append('Laptops')
            elif 'monitor' in d:
                categorias.append('Monitores')
            elif any(k in d for k in ['teclado', 'mouse', 'webcam', 'audífono', 'audifono', 'hub', 'cable', 'adaptador', 'base', 'mousepad']):
                categorias.append('Accesorios')
            elif 'impresora' in d:
                categorias.append('Impresoras')
            elif any(k in d for k in ['disco', 'ssd', 'usb', 'memoria ram']):
                categorias.append('Almacenamiento')
            else:
                categorias.append('Otros')
        df['categoria'] = categorias
        return df
    return pd.DataFrame()

@st.cache_data(ttl=300)
def cargar_movimientos(limite=50):
    query = """
        SELECT TOP ?
            Tipo_Movimiento as tipo,
            Numero_Documento as documento,
            Fecha as fecha,
            Cod_Articulo as codigo,
            Descripcion as descripcion,
            Cantidad as cantidad,
            Proveedor_Cliente as cliente
        FROM vista_movimientos_completos
        ORDER BY fecha DESC
    """
    df = ejecutar_consulta(query, params=[limite])
    if not df.empty:
        return df

    productos = _catalogo_muestra()
    now = datetime.now()
    muestras = [
        ("ENTRADA", "CE-2024-0018", 2, "ART001", "Proveedor HP Perú SAC"),
        ("SALIDA", "CS-2024-0027", 4, "ART010", "Cliente Comercial San Martín SAC"),
        ("ENTRADA", "CE-2024-0017", 6, "ART026", "Proveedor Epson Perú SAC"),
        ("SALIDA", "CS-2024-0026", 22, "ART017", "Cliente Distribuidora Andina SAC"),
        ("ENTRADA", "CE-2024-0016", 26, "ART032", "Proveedor Seagate Perú"),
        ("SALIDA", "CS-2024-0025", 30, "ART003", "Cliente Importaciones Asia SAC"),
    ]
    filas = []
    for tipo, doc, horas, cod, cliente in muestras:
        prod = productos[productos["codigo"] == cod].iloc[0]
        filas.append({
            "tipo": tipo, "documento": doc, "fecha": now - timedelta(hours=horas),
            "codigo": cod, "descripcion": prod["descripcion"], "cantidad": int(prod["stock"] % 10 + 1),
            "cliente": cliente
        })
    return pd.DataFrame(filas)

@st.cache_data(ttl=300)
def cargar_entradas():
    query = """
        SELECT
            Numero_Entrada as numero,
            Fecha as fecha,
            Proveedor as proveedor,
            Doc_Referencia as doc_referencia,
            Estado as estado
        FROM entradas_almacen
        ORDER BY Fecha DESC
    """
    df = ejecutar_consulta(query)
    if not df.empty:
        return df

    proveedores = ["HP Perú SAC", "Dell Perú SAC", "Logitech SAC", "Epson Perú SAC",
                   "Kingston Perú SAC", "Samsung Perú SAC", "Lenovo Perú SAC",
                   "Importaciones Asia SAC", "Canon Perú SAC", "Brother Perú SAC"]
    estados = ["Completa", "Completa", "Completa", "Con Observación", "Completa", "Pendiente"]
    base = datetime(2024, 1, 10)
    filas = []
    for i in range(1, 26):
        filas.append({
            "numero": f"CE-2024-{i:04d}",
            "fecha": base + timedelta(days=i),
            "proveedor": proveedores[i % len(proveedores)],
            "doc_referencia": f"FACT-{100 + i:03d}-{2024}",
            "estado": estados[i % len(estados)],
        })
    df = pd.DataFrame(filas)
    return df.sort_values("fecha", ascending=False).reset_index(drop=True)

@st.cache_data(ttl=300)
def cargar_salidas():
    query = """
        SELECT
            Numero_Salida as numero,
            Fecha as fecha,
            Proyecto as proyecto,
            Guia_Remision as guia,
            Estado as estado
        FROM salidas_almacen
        ORDER BY Fecha DESC
    """
    df = ejecutar_consulta(query)
    if not df.empty:
        return df

    clientes = ["Proyecto A - Retail Norte", "Proyecto B - Sede Central", "Proyecto C - Sucursal Sur",
                "Proyecto D - Campaña Digital", "Proyecto E - Ampliación Almacén", "Proyecto F - Renovación TI"]
    estados = ["Despachado", "En Tránsito", "Entregado", "Pendiente", "Entregado", "Despachado"]
    base = datetime(2024, 1, 12)
    filas = []
    for i in range(1, 31):
        filas.append({
            "numero": f"CS-2024-{i:04d}",
            "fecha": base + timedelta(days=i),
            "proyecto": clientes[i % len(clientes)],
            "guia": f"GR-{ (i % 20) + 1:03d}-2024",
            "estado": estados[i % len(estados)],
        })
    df = pd.DataFrame(filas)
    return df.sort_values("fecha", ascending=False).reset_index(drop=True)

@st.cache_data(ttl=300)
def cargar_guias():
    query = """
        SELECT
            Numero_Guia as numero,
            Fecha as fecha,
            Destinatario as destinatario,
            Transporte as transporte,
            Estado as estado,
            Firma_Cliente as firma
        FROM guias_remision
        ORDER BY Fecha DESC
    """
    df = ejecutar_consulta(query)
    if not df.empty:
        return df

    destinatarios = ["Cliente A - Retail Norte", "Cliente B - Sede Central", "Cliente C - Sucursal Sur",
                      "Cliente D - Campaña Digital", "Cliente E - Ampliación Almacén"]
    transportes = ["Transportes Rápidos SAC", "Logística Norte EIRL", "Cargo Express SA",
                   "Fletes Unidos SA", "Transportes Sur EIRL"]
    estados = ["Entregado", "En Tránsito", "Pendiente", "Entregado", "Despachado"]
    firmas = [True, False, False, True, True]
    base = datetime(2024, 1, 15)
    filas = []
    for i in range(1, 21):
        filas.append({
            "numero": f"GR-{i:03d}-2024",
            "fecha": base + timedelta(days=i),
            "destinatario": destinatarios[i % len(destinatarios)],
            "transporte": transportes[i % len(transportes)],
            "estado": estados[i % len(estados)],
            "firma": firmas[i % len(firmas)],
        })
    df = pd.DataFrame(filas)
    return df.sort_values("fecha", ascending=False).reset_index(drop=True)

# --- FUNCIONES DE ESTADÍSTICAS ---
def calcular_estadisticas(df_productos):
    total_productos = len(df_productos)
    stock_total = df_productos['stock'].sum() if not df_productos.empty else 0
    stock_bajo = len(df_productos[df_productos['stock'] <= 5]) if not df_productos.empty else 0
    return {
        'total_productos': total_productos,
        'stock_total': stock_total,
        'stock_bajo': stock_bajo
    }

def badge_html(valor, mapa):
    clase = mapa.get(valor, "badge-gray")
    return f'<span class="badge {clase}">{valor}</span>'

def render_tabla(df, columnas, titulo_caption=None):
    """Renderiza un DataFrame como tabla HTML con estilos personalizados.
    columnas: lista de tuplas (campo, encabezado, formateador_opcional)
    """
    filas_html = []
    for _, row in df.iterrows():
        celdas = []
        for campo, _, formateador in columnas:
            valor = row[campo]
            if formateador:
                valor = formateador(valor)
            celdas.append(f"<td>{valor}</td>")
        filas_html.append(f"<tr>{''.join(celdas)}</tr>")

    encabezados = "".join([f"<th>{h}</th>" for _, h, _ in columnas])
    tabla = f"""
    <div class="table-card">
    <div style="overflow-x:auto;">
    <table class="custom-table">
        <thead><tr>{encabezados}</tr></thead>
        <tbody>{''.join(filas_html)}</tbody>
    </table>
    </div>
    </div>
    """
    st.markdown(tabla, unsafe_allow_html=True)
    if titulo_caption:
        st.markdown(f'<p class="table-caption">{titulo_caption}</p>', unsafe_allow_html=True)

# --- INICIALIZAR ESTADO DE SESIÓN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "usuario_nombre" not in st.session_state:
    st.session_state.usuario_nombre = ""
if "usuario_rol" not in st.session_state:
    st.session_state.usuario_rol = ""
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "Dashboard"

# --- PÁGINA DE LOGIN ---
def mostrar_login():
    st.write("")
    st.write("")
    col1, col2, col3 = st.columns([0.6, 1, 1])

    with col2:
        st.markdown("""
            <div class="login-panel-dark">
                <div class="logo-box-lg">U</div>
                <h1>UNITY PERÚ SAC</h1>
                <p>Gestión de Almacén</p>
                <div class="deco">🚚</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="login-container">
                <h1 class="login-title">Bienvenido</h1>
                <p class="login-subtitle">Inicie sesión para continuar</p>
        """, unsafe_allow_html=True)

        df_usuarios = obtener_usuarios()

        if not df_usuarios.empty:
            opciones = {}
            for _, row in df_usuarios.iterrows():
                opciones[row['usuario']] = f"{row['nombre']} ({row['rol']})"

            usuario_seleccionado = st.selectbox(
                "Usuario",
                options=list(opciones.keys()),
                format_func=lambda x: opciones[x],
                key="login_usuario"
            )

            password = st.text_input(
                "Contraseña",
                type="password",
                placeholder="Ingrese su contraseña",
                key="login_password"
            )

            if st.button("Iniciar Sesión", use_container_width=True, type="primary"):
                if usuario_seleccionado and password:
                    autenticado, nombre, rol = autenticar_usuario(usuario_seleccionado, password)
                    if autenticado:
                        st.session_state.autenticado = True
                        st.session_state.usuario = usuario_seleccionado
                        st.session_state.usuario_nombre = nombre
                        st.session_state.usuario_rol = rol
                        st.rerun()
                    else:
                        st.error("❌ Contraseña incorrecta")
                else:
                    st.warning("⚠️ Por favor completa todos los campos")

            with st.expander("Ver todos los usuarios (desarrollo)"):
                st.dataframe(df_usuarios[['usuario', 'nombre', 'rol']], hide_index=True)
        else:
            st.error("❌ No se encontraron usuarios en el sistema")

        st.markdown("""
            <p style="text-align: center; color: #94a3b8; font-size: 0.72rem; margin-top: 1.4rem;">
                © 2026 UNITY PERÚ SAC - Todos los derechos reservados
            </p>
            </div>
        """, unsafe_allow_html=True)

# --- SIDEBAR ---
def mostrar_sidebar():
    with st.sidebar:
        st.markdown("""
            <div class="sidebar-logo">
                <div class="logo-box"><span>U</span></div>
                <h2>UNITY PERÚ SAC</h2>
                <p>Gestión de Almacén</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class="user-info">
                <p class="user-detail">Usuario actual</p>
                <p class="user-name">{st.session_state.usuario_nombre}</p>
                <p class="user-detail">@{st.session_state.usuario}</p>
                <span class="user-role">{st.session_state.usuario_rol}</span>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<p class="sidebar-section-label">Menú principal</p>', unsafe_allow_html=True)

        opciones_menu = {
            "Dashboard": "📊",
            "Productos": "📦",
            "Entradas": "📥",
            "Salidas": "📤",
            "Guías de Remisión": "📄",
            "Reportes": "📈",
        }

        if st.session_state.usuario_rol == "Administrador":
            opciones_menu["Usuarios y Roles"] = "👥"

        for opcion, icono in opciones_menu.items():
            if st.button(
                f"{icono}   {opcion}",
                key=f"menu_{opcion}",
                use_container_width=True,
                type="primary" if st.session_state.pagina_actual == opcion else "secondary"
            ):
                st.session_state.pagina_actual = opcion
                st.rerun()

        st.markdown('<p class="sidebar-section-label">Accesos rápidos</p>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Entrada", key="quick_entrada", use_container_width=True):
                st.session_state.pagina_actual = "Entradas"
                st.rerun()
        with col2:
            if st.button("📤 Salida", key="quick_salida", use_container_width=True):
                st.session_state.pagina_actual = "Salidas"
                st.rerun()

        st.divider()

        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            for key in ['autenticado', 'usuario', 'usuario_nombre', 'usuario_rol']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# --- TOPBAR REUTILIZABLE ---
def mostrar_topbar(titulo, subtitulo, alertas=3):
    iniciales = "".join([p[0] for p in st.session_state.usuario_nombre.split()[:2]]).upper() or "U"
    st.markdown(f"""
        <div class="topbar">
            <div class="tb-titles">
                <h1>{titulo}</h1>
                <p>{subtitulo}</p>
            </div>
            <div class="tb-right">
                <div class="tb-bell">🔔<span class="tb-badge">{alertas}</span></div>
                <div class="tb-user">
                    <div class="tb-avatar">{iniciales}</div>
                    <div>
                        <div class="tb-name">{st.session_state.usuario_nombre}</div>
                        <div class="tb-role">{st.session_state.usuario_rol}</div>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- PÁGINA: DASHBOARD ---
def mostrar_dashboard():
    mostrar_topbar("Dashboard", "Resumen general de la gestión del almacén")

    df_productos = cargar_categorias()
    df_movimientos = cargar_movimientos(10)
    df_entradas = cargar_entradas()
    df_salidas = cargar_salidas()
    stats = calcular_estadisticas(df_productos)

    ingresos_mes = int(df_entradas.shape[0] * 6.1) if not df_entradas.empty else 152
    salidas_mes = int(df_salidas.shape[0] * 3.2) if not df_salidas.empty else 98
    alertas = stats['stock_bajo'] if stats['stock_bajo'] > 0 else 27

    # --- KPIs ---
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
            <div class="kpi-card blue-light">
                <div class="kpi-top"><span class="kpi-label">Productos Totales</span><span class="kpi-icon">📦</span></div>
                <div class="kpi-value">{stats['total_productos']:,}</div>
                <div class="kpi-delta">Todos los productos registrados</div>
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div class="kpi-card green-light">
                <div class="kpi-top"><span class="kpi-label">Ingresos (Este mes)</span><span class="kpi-icon">📥</span></div>
                <div class="kpi-value">{ingresos_mes:,}</div>
                <div class="kpi-delta">Productos ingresados</div>
            </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
            <div class="kpi-card orange-light">
                <div class="kpi-top"><span class="kpi-label">Salidas (Este mes)</span><span class="kpi-icon">📤</span></div>
                <div class="kpi-value">{salidas_mes:,}</div>
                <div class="kpi-delta">Productos despachados</div>
            </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
            <div class="kpi-card purple-light">
                <div class="kpi-top"><span class="kpi-label">En Inventario</span><span class="kpi-icon">🗄️</span></div>
                <div class="kpi-value">{int(stats['stock_total']):,}</div>
                <div class="kpi-delta">Unidades disponibles</div>
            </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
            <div class="kpi-card red-light">
                <div class="kpi-top"><span class="kpi-label">Alertas (30 días)</span><span class="kpi-icon">⚠️</span></div>
                <div class="kpi-value">{alertas}</div>
                <div class="kpi-delta">Productos por vencer</div>
            </div>
        """, unsafe_allow_html=True)

    st.write("")

    # --- Gráficos y movimientos ---
    col_a, col_b, col_c = st.columns([1, 1.1, 1.1])

    with col_a:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.markdown("**Productos por antigüedad**")
        if not df_productos.empty and "dias_inventario" in df_productos.columns:
            bins = [0, 15, 30, 999]
            etiquetas = ["0 - 15 días", "16 - 30 días", "Más de 30 días"]
            df_productos["rango"] = pd.cut(df_productos["dias_inventario"], bins=bins, labels=etiquetas)
            data_rango = df_productos["rango"].value_counts().reindex(etiquetas).reset_index()
            data_rango.columns = ["Rango", "Cantidad"]
            fig_donut = go.Figure(data=[go.Pie(
                labels=data_rango["Rango"],
                values=data_rango["Cantidad"],
                hole=0.62,
                marker=dict(colors=["#22c55e", "#f59e0b", "#ef4444"]),
                textinfo="percent"
            )])
            fig_donut.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, font=dict(size=10)),
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("Sin datos de antigüedad")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.markdown("**Movimientos recientes**")
        if not df_movimientos.empty:
            df_mv = df_movimientos.copy()
            df_mv["fecha"] = pd.to_datetime(df_mv["fecha"])
            ahora = datetime.now()
            filas = []
            for _, row in df_mv.sort_values("fecha", ascending=False).head(6).iterrows():
                delta = ahora - row["fecha"]
                horas = int(delta.total_seconds() // 3600)
                tiempo = f"Hace {horas} h" if horas < 24 else f"Hace {int(horas//24)} d"
                clase = "badge-success" if row["tipo"] == "ENTRADA" else "badge-warning"
                etiqueta = "ENTRADA" if row["tipo"] == "ENTRADA" else "SALIDA"
                filas.append(f"""
                    <div class="move-item">
                        <div class="move-left">
                            <span class="badge {clase}">{etiqueta}</span>
                            <span class="move-title">{row['descripcion']}</span>
                            <span class="move-sub">Serie: {row['codigo']}</span>
                        </div>
                        <div class="move-time">{tiempo}</div>
                    </div>
                """)
            st.markdown("".join(filas), unsafe_allow_html=True)
        else:
            st.info("No hay movimientos recientes")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_c:
        st.markdown('<div class="table-card">', unsafe_allow_html=True)
        st.markdown("**Productos por categoría**")
        if not df_productos.empty:
            data_cat = df_productos['categoria'].value_counts().reindex(
                ["Laptops", "Monitores", "Accesorios", "Impresoras", "Almacenamiento", "Otros"]
            ).fillna(0).reset_index()
            data_cat.columns = ['Categoría', 'Cantidad']
            fig_bar = px.bar(
                data_cat,
                x="Categoría",
                y="Cantidad",
                color="Categoría",
                color_discrete_sequence=["#3b82f6"] * 6,
            )
            fig_bar.update_layout(
                margin=dict(t=10, b=10, l=10, r=10),
                height=300,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No hay datos de categorías")
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.markdown('<p class="quick-actions-title">⚡ Acciones rápidas</p>', unsafe_allow_html=True)
    acciones = st.columns(6)
    etiquetas_acciones = [
        ("📥 Nueva Entrada", "Entradas"),
        ("📤 Nueva Salida", "Salidas"),
        ("📦 Nuevo Producto", "Productos"),
        ("📄 Nueva Guía", "Guías de Remisión"),
        ("⚠️ Ver Alertas", "Productos"),
        ("📈 Ver Reportes", "Reportes"),
    ]
    for col, (etiqueta, destino) in zip(acciones, etiquetas_acciones):
        with col:
            if st.button(etiqueta, key=f"accion_{etiqueta}", use_container_width=True):
                st.session_state.pagina_actual = destino
                st.rerun()

# --- PÁGINA: PRODUCTOS ---
def mostrar_productos():
    mostrar_topbar("Productos", "Catálogo de productos del almacén")

    df_productos = cargar_categorias()

    col_busqueda, col_cat, col_accion = st.columns([2.2, 1.3, 1])
    with col_busqueda:
        buscar = st.text_input("🔍 Buscar producto...", placeholder="Código o descripción", label_visibility="collapsed")
    with col_cat:
        categorias_disp = ["Todas"] + sorted(df_productos['categoria'].unique().tolist()) if not df_productos.empty else ["Todas"]
        categoria_sel = st.selectbox("Categoría", categorias_disp, label_visibility="collapsed")
    with col_accion:
        if st.button("➕ Nuevo Producto", type="primary", use_container_width=True):
            st.info("Funcionalidad en desarrollo")

    df_filtrado = df_productos.copy()
    if buscar:
        df_filtrado = df_filtrado[
            df_filtrado.astype(str).apply(lambda x: x.str.contains(buscar, case=False, na=False)).any(axis=1)
        ]
    if categoria_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_sel]

    if not df_filtrado.empty:
        def estado_fmt(stock):
            return badge_html("Ok" if stock > 5 else "Bajo", {"Ok": "badge-success", "Bajo": "badge-danger"})

        columnas = [
            ("codigo", "Código", lambda v: f'<span class="mono">{v}</span>'),
            ("descripcion", "Descripción", None),
            ("categoria", "Categoría", None),
            ("marca", "Marca", None) if "marca" in df_filtrado.columns else None,
            ("unidad", "Und.", None),
            ("stock", "Stock", lambda v: int(v)),
            ("precio", "Precio", lambda v: f"S/. {v:,.2f}"),
            ("stock", "Estado", estado_fmt),
        ]
        columnas = [c for c in columnas if c is not None]
        render_tabla(df_filtrado, columnas)
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_productos)} productos")
    else:
        st.info("No se encontraron productos")

# --- PÁGINA: ENTRADAS ---
def mostrar_entradas():
    mostrar_topbar("Entradas", "Control de entradas al almacén")

    df_entradas = cargar_entradas()

    col_busqueda, col_estado, col_accion = st.columns([2.2, 1.3, 1])
    with col_busqueda:
        buscar = st.text_input("🔍 Buscar entrada...", placeholder="N° entrada o proveedor", label_visibility="collapsed")
    with col_estado:
        estados_disp = ["Todos"] + sorted(df_entradas['estado'].unique().tolist()) if not df_entradas.empty else ["Todos"]
        estado_sel = st.selectbox("Estado", estados_disp, label_visibility="collapsed")
    with col_accion:
        if st.button("➕ Nueva Entrada", type="primary", use_container_width=True):
            st.info("Funcionalidad en desarrollo")

    df_filtrado = df_entradas.copy()
    if buscar:
        df_filtrado = df_filtrado[
            df_filtrado.astype(str).apply(lambda x: x.str.contains(buscar, case=False, na=False)).any(axis=1)
        ]
    if estado_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['estado'] == estado_sel]

    if not df_filtrado.empty:
        mapa_estado = {
            "Completa": "badge-success",
            "Con Observación": "badge-danger",
            "Pendiente": "badge-warning",
        }
        columnas = [
            ("numero", "N° Entrada", lambda v: f'<span class="mono">{v}</span>'),
            ("fecha", "Fecha", lambda v: pd.to_datetime(v).strftime("%d/%m/%Y")),
            ("proveedor", "Proveedor", None),
            ("doc_referencia", "Doc. Referencia", lambda v: f'<span class="muted">{v}</span>'),
            ("estado", "Estado", lambda v: badge_html(v, mapa_estado)),
        ]
        render_tabla(df_filtrado, columnas)
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_entradas)} entradas")
    else:
        st.info("No hay entradas registradas")

# --- PÁGINA: SALIDAS ---
def mostrar_salidas():
    mostrar_topbar("Salidas", "Control de salidas del almacén")

    df_salidas = cargar_salidas()

    col_busqueda, col_estado, col_accion = st.columns([2.2, 1.3, 1])
    with col_busqueda:
        buscar = st.text_input("🔍 Buscar salida...", placeholder="N° salida o proyecto", label_visibility="collapsed")
    with col_estado:
        estados_disp = ["Todos"] + sorted(df_salidas['estado'].unique().tolist()) if not df_salidas.empty else ["Todos"]
        estado_sel = st.selectbox("Estado", estados_disp, label_visibility="collapsed")
    with col_accion:
        if st.button("➕ Nueva Salida", type="primary", use_container_width=True):
            st.info("Funcionalidad en desarrollo")

    df_filtrado = df_salidas.copy()
    if buscar:
        df_filtrado = df_filtrado[
            df_filtrado.astype(str).apply(lambda x: x.str.contains(buscar, case=False, na=False)).any(axis=1)
        ]
    if estado_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['estado'] == estado_sel]

    if not df_filtrado.empty:
        mapa_estado = {
            "Despachado": "badge-info",
            "En Tránsito": "badge-warning",
            "Entregado": "badge-success",
            "Pendiente": "badge-danger",
        }
        columnas = [
            ("numero", "N° Salida", lambda v: f'<span class="mono">{v}</span>'),
            ("fecha", "Fecha", lambda v: pd.to_datetime(v).strftime("%d/%m/%Y")),
            ("proyecto", "Oppy / Proyecto", None),
            ("guia", "Guía Remisión", lambda v: f'<span class="muted">{v}</span>'),
            ("estado", "Estado", lambda v: badge_html(v, mapa_estado)),
        ]
        render_tabla(df_filtrado, columnas)
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_salidas)} salidas")
    else:
        st.info("No hay salidas registradas")

# --- PÁGINA: GUÍAS DE REMISIÓN ---
def mostrar_guias():
    mostrar_topbar("Guías de Remisión", "Gestión de guías de remisión")

    df_guias = cargar_guias()

    col_busqueda, col_estado, col_accion = st.columns([2.2, 1.3, 1])
    with col_busqueda:
        buscar = st.text_input("🔍 Buscar guía...", placeholder="N° guía o destinatario", label_visibility="collapsed")
    with col_estado:
        estados_disp = ["Todos"] + sorted(df_guias['estado'].unique().tolist()) if not df_guias.empty else ["Todos"]
        estado_sel = st.selectbox("Estado", estados_disp, label_visibility="collapsed")
    with col_accion:
        if st.button("➕ Nueva Guía", type="primary", use_container_width=True):
            st.info("Funcionalidad en desarrollo")

    df_filtrado = df_guias.copy()
    if buscar:
        df_filtrado = df_filtrado[
            df_filtrado.astype(str).apply(lambda x: x.str.contains(buscar, case=False, na=False)).any(axis=1)
        ]
    if estado_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado['estado'] == estado_sel]

    if not df_filtrado.empty:
        mapa_estado = {
            "Entregado": "badge-success",
            "En Tránsito": "badge-warning",
            "Pendiente": "badge-danger",
            "Despachado": "badge-info",
        }
        columnas = [
            ("numero", "N° Guía", lambda v: f'<span class="mono">{v}</span>'),
            ("fecha", "Fecha", lambda v: pd.to_datetime(v).strftime("%d/%m/%Y")),
            ("destinatario", "Destinatario", None),
            ("transporte", "Transporte", None),
            ("estado", "Estado", lambda v: badge_html(v, mapa_estado)),
            ("firma", "Firma Cliente", lambda v: '<span class="check-yes">✓</span>' if v else '<span class="check-no">✗</span>'),
        ]
        render_tabla(df_filtrado, columnas)
        st.caption(f"Mostrando {len(df_filtrado)} de {len(df_guias)} guías")
    else:
        st.info("No hay guías registradas")

# --- PÁGINA: REPORTES ---
def mostrar_reportes():
    mostrar_topbar("Reportes", "Generación de reportes del sistema")

    reportes = [
        ("📊", "Reporte de Inventario", "Estado actual del inventario"),
        ("📥", "Reporte de Entradas", "Historial de entradas"),
        ("📤", "Reporte de Salidas", "Historial de salidas"),
        ("📦", "Reporte por Productos", "Análisis por producto"),
        ("📅", "Reporte por Fechas", "Rango de fechas"),
        ("🔄", "Reporte de Movimientos", "Todos los movimientos"),
    ]
    cols = st.columns(3)
    for i, (icono, titulo, desc) in enumerate(reportes):
        with cols[i % 3]:
            st.markdown(f"""
                <div class="table-card" style="text-align:center; margin-bottom:1rem;">
                    <div style="font-size:1.8rem;">{icono}</div>
                    <div style="font-weight:700; color:#0f172a; margin:0.3rem 0 0.1rem 0;">{titulo}</div>
                    <div style="color:#94a3b8; font-size:0.78rem;">{desc}</div>
                </div>
            """, unsafe_allow_html=True)

# --- PÁGINA: USUARIOS ---
def mostrar_usuarios():
    mostrar_topbar("Usuarios y Roles", "Gestión de usuarios del sistema")

    if st.session_state.usuario_rol != "Administrador":
        st.error("⚠️ No tienes permisos para acceder a esta sección")
        return

    df_usuarios = obtener_usuarios()

    if not df_usuarios.empty:
        col1, col2 = st.columns([3, 1])
        with col1:
            columnas = [
                ("usuario", "Usuario", lambda v: f'<span class="mono">{v}</span>'),
                ("nombre", "Nombre", None),
                ("rol", "Rol", lambda v: badge_html(v, {
                    "Administrador": "badge-info", "Almacenero": "badge-success",
                    "Logistica": "badge-warning", "Operario": "badge-gray"
                })),
            ]
            render_tabla(df_usuarios, columnas)
        with col2:
            if st.button("➕ Nuevo Usuario", type="primary", use_container_width=True):
                st.info("Funcionalidad en desarrollo")
    else:
        st.info("No hay usuarios registrados")

# --- MAIN ---
def main():
    if not st.session_state.autenticado:
        mostrar_login()
        return

    mostrar_sidebar()

    pagina = st.session_state.pagina_actual

    if pagina == "Dashboard":
        mostrar_dashboard()
    elif pagina == "Productos":
        mostrar_productos()
    elif pagina == "Entradas":
        mostrar_entradas()
    elif pagina == "Salidas":
        mostrar_salidas()
    elif pagina == "Guías de Remisión":
        mostrar_guias()
    elif pagina == "Reportes":
        mostrar_reportes()
    elif pagina == "Usuarios y Roles":
        mostrar_usuarios()
    else:
        st.info("Página en desarrollo")

if __name__ == "__main__":
    main()
