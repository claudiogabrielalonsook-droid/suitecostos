# Reporte de Costos - Comparación Cantidad Prevista vs Producida

Una aplicación Streamlit para analizar órdenes de producción cerradas y comparar la cantidad prevista con la cantidad producida.

## Características

- ✅ **Interfaz Web**: Aplicación interactiva con Streamlit
- 📊 **Comparación Automática**: Compara cantidad prevista vs producida
- 📅 **Filtrado por Fechas**: Fechas inclusivas (>= y <=)
- 📈 **Estadísticas**: Resumen de OPs cumplidas y excedidas
- 📥 **Descarga en Excel**: Exporta los resultados directamente
- 🔄 **Transformación Automática**: Siempre aplica transformaciones antes de mostrar/descargar
- 📝 **Consulta Dinámica**: Lee la consulta SQL de `query.txt` y la ejecuta con los parámetros seleccionados

## Estructura del Proyecto

```
CostosReporteComparacion_Gabi/
├── app.py                 # Aplicación principal de Streamlit
├── db.py                  # Módulo de conexión a base de datos
├── transformacion.py      # Módulo de transformación de datos
├── query.txt              # Consulta SQL parametrizable
├── .env                   # Variables de entorno (no subir a Git)
├── requirements.txt       # Dependencias del proyecto
├── iniciar_app.bat        # Ejecutable para abrir la app (Windows CMD)
├── iniciar_app.ps1        # Ejecutable para abrir la app (PowerShell)
├── GUIA_RAPIDA.txt        # Guía rápida de uso
├── README.md              # Este archivo
└── venv/                  # Entorno virtual de Python
```

## Instalación

### 1. Clonar o descargar el repositorio

```bash
cd CostosReporteComparacion_Gabi
```

### 2. Crear entorno virtual

```bash
python -m venv venv
```

### 3. Activar entorno virtual

**En Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**En Windows (CMD):**
```cmd
.\venv\Scripts\activate.bat
```

**En macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Editar el archivo `.env`:

```env
SQL_SERVER=10.1.0.82\SQLSERVERBD02
SQL_PORT=
SQL_DATABASE=MetricsPROD
SQL_USER=usrLAF
SQL_PASSWORD=usrLAF01
ODBC_DRIVER=SQL Server Native Client 11.0
```

## Uso

### Ejecutar la aplicación Streamlit

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en: http://localhost:8501

### Uso de la Interfaz

1. **Seleccionar Fechas**: Elige la fecha de inicio y cierre en el sidebar
   - Las fechas son **inclusivas** (>= y <=)
2. **Ejecutar Consulta**: Click en "🔄 Ejecutar Consulta"
3. **Ver Resultados**: Los resultados aparecerán en una tabla interactiva con:
   - Estadísticas resumidas (Total OPs, Cumplidas, Excedidas, Variación %)
   - Tabla detallada con todas las OPs y sus comparaciones
4. **Descargar Excel**: Click en "⬇️ Descargar Excel" para descargar los datos

## Estructura de la Consulta SQL

La consulta se lee desde `query.txt` y es parametrizable con fechas.

El WHERE filtra:

- **OPs Cerradas**: `o.Situacao = 'E'` y `ISNULL(ws.Name, '') = 'Cerrada'`
- **Rango de Fechas**: `o.DtEncerramento >= {fecha_inicio} AND o.DtEncerramento <= {fecha_cierre}` (ambas inclusivas)
- **Excluye Ciertos Lanzamientos**: `c.TipoLancamento <> 'L'`

### Modificar la Consulta

Para cambiar la consulta SQL:
1. Abre `query.txt`
2. Modifica la consulta según necesites
3. Asegúrate de incluir los placeholders `{fecha_inicio}` y `{fecha_cierre}` en el WHERE

Ejemplo:
```sql
WHERE
    o.Situacao = 'E'
    AND ISNULL(ws.Name, '') = 'Cerrada'
    AND c.TipoLancamento <> 'L'
    AND o.DtEncerramento >= '{fecha_inicio}'
    AND o.DtEncerramento <= '{fecha_cierre}'
```

## Transformación de Datos

La función `transformar_df()` en `transformacion.py` se ejecuta **siempre** antes de mostrar o descargar datos. Esta función:

1. **Limpia columnas**: Elimina espacios en blanco de los nombres
2. **Renombra columnas**: `Qtde` → `Cantidad`
3. **Crea ValorUnitario**: Calcula el valor unitario
4. **Elimina columnas innecesarias**: Remove todas las columnas no relevantes
5. **Transforma datos**: Extrae información de campos compuestos

Las columnas que se eliminan están definidas en la lista `columnas_eliminar` en `transformacion.py`.

## Columnas Principales en los Resultados

| Columna | Descripción |
|---------|-----------|
| `NumOrdem` | Número de la orden de producción |
| `TituloOP` | Descripción/título de la OP |
| `NomeCliente` | Nombre del cliente |
| `DtEncerramento` | Fecha de cierre de la OP |
| `QtdPrevista` | Cantidad prevista/presupuestada |
| `CantidadProducida` | Cantidad real producida |
| `Diferencia` | QtdPrevista - CantidadProducida |
| `Variacion_%` | Porcentaje de variación |
| `Estado` | "✓ Cumplido" o "✗ Excedido" |
| `ValorTotalPrevisto` | Valor presupuestado total |
| `ValorTotalFaturado` | Valor facturado total |
| `CustoTotalPrevisto` | Costo presupuestado total |
| `CustoTotalReal` | Costo real total |

## Troubleshooting

### Error: "No existe el archivo query.txt"
- Verifica que `query.txt` exista en el directorio raíz del proyecto

### Error: "Faltan variables de entorno: SQL_SERVER o SQL_DATABASE"
- Verifica que el archivo `.env` exista y tenga las variables configuradas correctamente

### Error: "Connection refused" o "Database connection failed"
- Verifica que puedas conectarte a la base de datos desde tu máquina
- Confirma que el SQL Server esté en línea
- Verifica las credenciales en `.env`

### Error: "No se encontraron registros"
- Verifica que existan OPs cerradas en el período especificado
- Revisa que la fecha de cierre sea mayor o igual a la fecha de inicio

### Streamlit no arranca
```bash
# Limpia la caché de Streamlit
streamlit cache clear

# Intenta ejecutar de nuevo
streamlit run app.py
```

## Archivos Generados

Los archivos Excel se guardan automáticamente en:
```
C:\Users\[tu_usuario]\Downloads\reporte_costos_YYYYMMDD_YYYYMMDD.xlsx
```

## Dependencias Principales

- **streamlit**: Framework web interactivo
- **pandas**: Manipulación de datos
- **pyodbc**: Conexión a SQL Server
- **openpyxl**: Generación de archivos Excel
- **python-dotenv**: Gestión de variables de entorno

## Notas Importantes

⚠️ **Transformación Obligatoria**: La función `transformar_df()` se ejecuta **siempre**, antes de mostrar o descargar cualquier dato. Esto asegura que:
- Los datos se limpian y transforman consistentemente
- Las columnas innecesarias siempre se eliminan
- El Excel descargado contiene datos transformados

## Autor

Generado por GitHub Copilot

## Licencia

Privado - Uso interno únicamente

