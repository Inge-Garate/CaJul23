from sqlalchemy import create_engine, text
from datetime import timedelta
import os

my_secret = os.environ['DB_CONNECTION_STRING']

engine = create_engine(my_secret)

def load_obras_from_db():
  with engine.connect() as connection:
    result = connection.execute(
      text("SELECT id_obra, nombre_obra FROM OBRAS ORDER BY id_obra"))
    obras = result.fetchall()
    return obras

def load_nombre_obra_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text("SELECT nombre_obra FROM OBRAS WHERE id_obra=:obra"),
      {"obra": obra})
    nombre_obra = ''.join(map(str, result.fetchone()))
    return nombre_obra

def load_nombre_empleado_from_db(empleado):
  with engine.connect() as connection:
    result = connection.execute(
      text("SELECT nombre FROM EMPLEADOS WHERE id_empleado=:empleado"),
      {"empleado": empleado})
    nombre_empleado = ''.join(map(str, result.fetchone()))
    return nombre_empleado

def load_monto_gastos_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text("SELECT SUM(CASE WHEN boolean_factura = 'si' THEN monto_gasto / 1.16 ELSE monto_gasto END) AS sum_result FROM GASTOS_OBRAS WHERE id_obra=:obra"),{"obra": obra})
    row = result.fetchone()
    # Check if row is None (no data found)
    if row is not None:
      monto_gastos = row[0]
      # Check if monto_gastos is None (no data found in the specific row)
      if monto_gastos is not None:
          return float(monto_gastos)
      else:
        # Handle the case when monto_gastos is None (return a default value or raise an exception)
        # For example, you can return 0.0 as the default value
        return 0.0
    else:
      # Handle the case when no data is found (return a default value or raise an exception)
    # For example, you can return 0.0 as the default value
        return 0.0
    
def load_monto_contratos_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text("SELECT SUM(monto_neto_contrato) /1.16 AS sum_result FROM CONTRATOS WHERE id_obra=:obra"),{"obra": obra})
    row = result.fetchone()
    # Check if row is None (no data found)
    if row is not None:
      monto_contratos=row[0]
      # Check if monto_gastos is None (no data found in the specific row)
      if monto_contratos is not None:
        return float(monto_contratos)
      else:
        # Handle the case when monto_gastos is None (return a default value or raise an exception)
        # For example, you can return 0.0 as the default value
        return 0.0
    else:
      # Handle the case when no data is found (return a default value or raise an exception)
    # For example, you can return 0.0 as the default value
        return 0.0

def load_contratos_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text(
        "SELECT id_obra, id_contrato, nombre_contrato, monto_neto_contrato, status_contrato FROM CONTRATOS WHERE id_obra=:obra"
      ), {"obra": obra})
    contratos = []
    for row in result.all():
      contratos.append(row._asdict())
    return contratos

def load_dropdwn_contratos_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text("SELECT id_contrato, nombre_contrato FROM CONTRATOS WHERE id_obra=:obra"), {"obra": obra})
    contratos = [{"id_contrato": row[0], "nombre_contrato": row[1]} for row in result.fetchall()]
    return contratos

def load_trabajadores_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text(
        "SELECT DISTINCT id_empleado, CONCAT(nombre, ' ', apellido_p, ' ', apellido_m) AS empleado FROM (SELECT ASISTENCIAS.id_empleado, ASISTENCIAS.id_asistencia, ASISTENCIAS.fecha, EMPLEADOS.puesto, EMPLEADOS.nombre, EMPLEADOS.apellido_p, EMPLEADOS.apellido_m,  OBRAS.nombre_obra, ASISTENCIAS.boolean_asistencia, ASISTENCIAS.notas FROM const231_db_ca.ASISTENCIAS INNER JOIN const231_db_ca.EMPLEADOS ON const231_db_ca.ASISTENCIAS.id_empleado=const231_db_ca.EMPLEADOS.id_empleado INNER JOIN const231_db_ca.OBRAS ON const231_db_ca.ASISTENCIAS.id_obra=const231_db_ca.OBRAS.id_obra AND const231_db_ca.OBRAS.id_obra=:obra) AS Empleados"
      ), {"obra": obra})
    trabajadores = []
    for row in result.all():
      trabajadores.append(row._asdict())
    return trabajadores

def load_asistencias_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text(
        "SELECT ASISTENCIAS.id_asistencia, ASISTENCIAS.fecha, EMPLEADOS.puesto, EMPLEADOS.nombre, EMPLEADOS.apellido_p,  OBRAS.nombre_obra, ASISTENCIAS.boolean_asistencia, ASISTENCIAS.notas FROM const231_db_ca.ASISTENCIAS INNER JOIN const231_db_ca.EMPLEADOS ON const231_db_ca.ASISTENCIAS.id_empleado=const231_db_ca.EMPLEADOS.id_empleado INNER JOIN const231_db_ca.OBRAS ON const231_db_ca.ASISTENCIAS.id_obra=const231_db_ca.OBRAS.id_obra AND const231_db_ca.OBRAS.id_obra=:obra AND boolean_asistencia='si'"
      ), {"obra": obra})
    asistencias = []
    for row in result.all():
      asistencias.append(row._asdict())
    return asistencias

def load_asistencias_sem_from_db(engine, obra):
  with engine.connect() as connection:
    result = connection.execute(
      text(
        "SELECT MAX(ASISTENCIAS.fecha) AS max_fecha, MIN(ASISTENCIAS.fecha) AS min_fecha, ASISTENCIAS.id_asistencia, ASISTENCIAS.fecha, EMPLEADOS.puesto, EMPLEADOS.nombre, EMPLEADOS.apellido_p, OBRAS.nombre_obra, ASISTENCIAS.boolean_asistencia, ASISTENCIAS.notas FROM const231_db_ca.ASISTENCIAS INNER JOIN const231_db_ca.EMPLEADOS ON const231_db_ca.ASISTENCIAS.id_empleado=const231_db_ca.EMPLEADOS.id_empleado INNER JOIN const231_db_ca.OBRAS ON const231_db_ca.ASISTENCIAS.id_obra=const231_db_ca.OBRAS.id_obra AND const231_db_ca.OBRAS.id_obra=:obra GROUP BY ASISTENCIAS.id_asistencia"
      ), {"obra": obra})
    asistencias = [row._asdict() for row in result.all()]
    for row in result.all():
      asistencias.append(row._asdict())
    return asistencias

def load_asistencias_empleado_from_db(engine, id_empleado):
  with engine.connect() as connection:
    result = connection.execute(
      text(
        "SELECT ASISTENCIAS.id_asistencia, ASISTENCIAS.fecha, EMPLEADOS.puesto, EMPLEADOS.nombre, EMPLEADOS.apellido_p, OBRAS.nombre_obra, ASISTENCIAS.boolean_asistencia, ASISTENCIAS.notas FROM const231_db_ca.ASISTENCIAS INNER JOIN const231_db_ca.EMPLEADOS ON const231_db_ca.ASISTENCIAS.id_empleado=const231_db_ca.EMPLEADOS.id_empleado INNER JOIN const231_db_ca.OBRAS ON const231_db_ca.ASISTENCIAS.id_obra=const231_db_ca.OBRAS.id_obra AND const231_db_ca.EMPLEADOS.id_empleado=:id_empleado GROUP BY ASISTENCIAS.fecha"
      ), {"id_empleado": id_empleado})
    asistencias = [row._asdict() for row in result.all()]
    for row in result.all():
      asistencias.append(row._asdict())
    return asistencias

def load_gastos_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text(
        "SELECT GASTOS_OBRAS.id_gasto, EMPLEADOS.nombre, GASTOS_OBRAS.fecha_gasto, GASTOS_OBRAS.monto_gasto, GASTOS_OBRAS.concepto_gasto, GASTOS_OBRAS.tipo_gasto, GASTOS_OBRAS.boolean_factura, CONTRATOS.nombre_contrato FROM const231_db_ca.GASTOS_OBRAS INNER JOIN const231_db_ca.CONTRATOS ON const231_db_ca.GASTOS_OBRAS.id_contrato=const231_db_ca.CONTRATOS.id_contrato INNER JOIN const231_db_ca.EMPLEADOS ON const231_db_ca.GASTOS_OBRAS.id_empleado=const231_db_ca.EMPLEADOS.id_empleado AND const231_db_ca.GASTOS_OBRAS.id_obra=:obra"
      ), {"obra": obra})
    gastos = []
    for row in result.all():
      gastos.append(row._asdict())
    return gastos

def load_workers_from_db():
  with engine.connect() as connection:
    result = connection.execute(
      text("SELECT id_empleado, nombre, apellido_p, apellido_m FROM const231_db_ca.EMPLEADOS ORDER BY nombre;"))
    empleados = result.fetchall()
    return empleados

def load_estimaciones_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text(
        "SELECT E.nombre_estimacion, E.notas, ROUND(SUM(CC.precio_unitario * VE.volumen), 2) AS monto,     ROUND(SUM(CC.precio_unitario * VE.volumen) * (C.porcentaje_f_garantia/100), 2) AS f_g FROM ESTIMACIONES AS E JOIN CONTRATOS AS C ON E.id_contrato = C.id_contrato JOIN VOLUMENES_ESTIMACIONES AS VE ON E.id_estimacion = VE.id_estimacion JOIN VOLUMENES_CONCEPTOS_CONTRATO AS VCC ON VE.id_volumen_conc = VCC.id_volumen_conc JOIN CONCEPTOS_CONTRATOS AS CC ON VCC.id_concepto = CC.id_concepto WHERE C.id_obra=:obra GROUP BY E.nombre_estimacion, E.notas, C.porcentaje_f_garantia;"
      ), {"obra": obra})
    estimaciones = []
    for row in result.all():
      estimaciones.append(row._asdict())
    return estimaciones

def load_monto_est_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text("SELECT ROUND(SUM(monto), 2) AS total_monto FROM (SELECT E.nombre_estimacion, E.notas, ROUND(SUM(CC.precio_unitario * VE.volumen), 2) AS monto,     ROUND(SUM(CC.precio_unitario * VE.volumen) * (C.porcentaje_f_garantia/100), 2) AS f_g FROM ESTIMACIONES AS E JOIN CONTRATOS AS C ON E.id_contrato = C.id_contrato JOIN VOLUMENES_ESTIMACIONES AS VE ON E.id_estimacion = VE.id_estimacion JOIN VOLUMENES_CONCEPTOS_CONTRATO AS VCC ON VE.id_volumen_conc = VCC.id_volumen_conc JOIN CONCEPTOS_CONTRATOS AS CC ON VCC.id_concepto = CC.id_concepto WHERE C.id_obra=:obra GROUP BY E.nombre_estimacion, E.notas, C.porcentaje_f_garantia) AS subquery;"),{"obra": obra})
    row = result.fetchone()
    # Check if row is None (no data found)
    if row is not None:
      monto_estimaciones=row[0]
      # Check if monto_gastos is None (no data found in the specific row)
      if monto_estimaciones is not None:
        return float(monto_estimaciones)
      else:
        # Handle the case when monto_gastos is None (return a default value or raise an exception)
        # For example, you can return 0.0 as the default value
        return 0.0
    else:
      # Handle the case when no data is found (return a default value or raise an exception)
    # For example, you can return 0.0 as the default value
        return 0.0

def load_monto_fg_from_db(obra):
  with engine.connect() as connection:
    result = connection.execute(
      text("SELECT ROUND(SUM(f_g), 2) AS total_fg FROM (SELECT E.nombre_estimacion, E.notas, ROUND(SUM(CC.precio_unitario * VE.volumen), 2) AS monto,     ROUND(SUM(CC.precio_unitario * VE.volumen) * (C.porcentaje_f_garantia/100), 2) AS f_g FROM ESTIMACIONES AS E JOIN CONTRATOS AS C ON E.id_contrato = C.id_contrato JOIN VOLUMENES_ESTIMACIONES AS VE ON E.id_estimacion = VE.id_estimacion JOIN VOLUMENES_CONCEPTOS_CONTRATO AS VCC ON VE.id_volumen_conc = VCC.id_volumen_conc JOIN CONCEPTOS_CONTRATOS AS CC ON VCC.id_concepto = CC.id_concepto WHERE C.id_obra=:obra GROUP BY E.nombre_estimacion, E.notas, C.porcentaje_f_garantia) AS subquery;"),{"obra": obra})
    row = result.fetchone()
    # Check if row is None (no data found)
    if row is not None:
      monto_fg=row[0]
      # Check if monto_gastos is None (no data found in the specific row)
      if monto_fg is not None:
        return float(monto_fg)
      else:
        # Handle the case when monto_gastos is None (return a default value or raise an exception)
        # For example, you can return 0.0 as the default value
        return 0.0
    else:
      # Handle the case when no data is found (return a default value or raise an exception)
    # For example, you can return 0.0 as the default value
        return 0.0