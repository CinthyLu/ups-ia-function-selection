from datetime import datetime, timedelta
from sqlalchemy import func
import pandas as pd

def top_selling():
    """
    Obtiene los 5 productos más vendidos del último mes.
    Retorna una lista de diccionarios.
    """
    session = SessionLocal()
    try:
        hace_un_mes = datetime.now() - timedelta(days=30)

        # Agrupamos ventas por producto usando registros del último mes
        resultados = (
            session.query(
                Producto.product_name,
                func.sum(RegistroInventario.ventas_diarias).label("ventas")
            )
            .join(RegistroInventario)
            .filter(RegistroInventario.created_at >= hace_un_mes)
            .group_by(Producto.product_name)
            .order_by(func.sum(RegistroInventario.ventas_diarias).desc())
            .limit(5)
            .all()
        )

        data = [
            {"product": r.product_name, "ventas": int(r.ventas or 0)}
            for r in resultados
        ]

        return data

    finally:
        session.close()



def least_selling():
    """
    Obtiene los 5 productos con menor venta en el último mes.
    Retorna una lista de diccionarios.
    """
    session = SessionLocal()
    try:
        hace_un_mes = datetime.now() - timedelta(days=30)

        resultados = (
            session.query(
                Producto.product_name,
                func.sum(RegistroInventario.ventas_diarias).label("ventas")
            )
            .join(RegistroInventario)
            .filter(RegistroInventario.created_at >= hace_un_mes)
            .group_by(Producto.product_name)
            .order_by(func.sum(RegistroInventario.ventas_diarias).asc())
            .limit(5)
            .all()
        )

        data = [
            {"product": r.product_name, "ventas": int(r.ventas or 0)}
            for r in resultados
        ]

        return data

    finally:
        session.close()



def generate_excel(month=None):
    """
    Genera un archivo Excel con los registros del último mes o un mes indicado.
    Retorna la ruta del archivo generado.
    """
    session = SessionLocal()
    try:
        if month:
            año, mes = map(int, month.split("-"))
            inicio = datetime(año, mes, 1)
            if mes == 12:
                fin = datetime(año + 1, 1, 1)
            else:
                fin = datetime(año, mes + 1, 1)
        else:
            fin = datetime.now()
            inicio = fin - timedelta(days=30)

        query = (
            session.query(
                RegistroInventario.id,
                RegistroInventario.product_id,
                RegistroInventario.created_at,
                RegistroInventario.quantity_available,
                RegistroInventario.ventas_diarias,
                RegistroInventario.total_value
            )
            .filter(RegistroInventario.created_at >= inicio)
            .filter(RegistroInventario.created_at < fin)
        )

        df = pd.read_sql(query.statement, session.bind)

        file_path = f"reporte_{inicio.date()}_{fin.date()}.xlsx"
        df.to_excel(file_path, index=False)

        return file_path

    finally:
        session.close()


def generate_csv(month=None):
    """
    Genera un archivo CSV con los registros del último mes o del mes especificado.
    Retorna la ruta del archivo generado.
    """
    session = SessionLocal()
    try:
        if month:
            # formato esperado: "2025-01"
            año, mes = map(int, month.split("-"))
            inicio = datetime(año, mes, 1)
            if mes == 12:
                fin = datetime(año + 1, 1, 1)
            else:
                fin = datetime(año, mes + 1, 1)
        else:
            fin = datetime.now()
            inicio = fin - timedelta(days=30)

        query = (
            session.query(
                RegistroInventario.id,
                RegistroInventario.product_id,
                RegistroInventario.created_at,
                RegistroInventario.quantity_available,
                RegistroInventario.ventas_diarias,
                RegistroInventario.total_value
            )
            .filter(RegistroInventario.created_at >= inicio)
            .filter(RegistroInventario.created_at < fin)
        )

        df = pd.read_sql(query.statement, session.bind)

        file_path = f"reporte_{inicio.date()}_{fin.date()}.csv"
        df.to_csv(file_path, index=False)

        return file_path

    finally:
        session.close()
