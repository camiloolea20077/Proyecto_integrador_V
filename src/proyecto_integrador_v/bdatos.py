import os
import sqlite3
import pandas as pd
from typing import Optional, List, Dict, Any

class Bdatos:
    """
    Clase para el manejo de una base de datos SQLite local.
    Permite crear tablas, insertar DataFrames y realizar consultas.
    """
    
    def __init__(self, db_path: str = "static/db/proyecto.db"):
        """
        Inicializa la conexión a la base de datos.
        
        Parameters:
        -----------
        db_path : str
            Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        # Crear directorios si no existen
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.connection = None
        self._conectar()
    
    def _conectar(self):
        """Establece conexión con la base de datos"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f" Conectado a la base de datos: {self.db_path}")
        except Exception as e:
            print(f" Error al conectar con la base de datos: {e}")
            raise
    
    def cerrar_conexion(self):
        """Cierra la conexión con la base de datos"""
        if self.connection:
            self.connection.close()
            print("Conexión cerrada")
    
    def crear_tabla(self, nombre_tabla: str, esquema: Dict[str, str]) -> bool:
        """
        Crea una nueva tabla en la base de datos.
        
        Parameters:
        -----------
        nombre_tabla : str
            Nombre de la tabla a crear
        esquema : Dict[str, str]
            Diccionario con nombre_columna: tipo_datos
            Ej: {"id": "INTEGER PRIMARY KEY", "nombre": "TEXT", "edad": "INTEGER"}
        
        Returns:
        --------
        bool
            True si la tabla se creó exitosamente
        """
        try:
            cursor = self.connection.cursor()
            
            # Construir la query de creación
            columnas = ", ".join([f"{col} {tipo}" for col, tipo in esquema.items()])
            query = f"CREATE TABLE IF NOT EXISTS {nombre_tabla} ({columnas})"
            
            cursor.execute(query)
            self.connection.commit()
            print(f" Tabla '{nombre_tabla}' creada exitosamente")
            return True
            
        except Exception as e:
            print(f" Error al crear la tabla '{nombre_tabla}': {e}")
            return False
    
    def insertar_dataframe(self, df: pd.DataFrame, nombre_tabla: str, 
                          if_exists: str = "replace") -> bool:
        """
        Inserta un DataFrame completo en una tabla.
        
        Parameters:
        -----------
        df : pd.DataFrame
            DataFrame a insertar
        nombre_tabla : str
            Nombre de la tabla destino
        if_exists : str
            Comportamiento si la tabla existe: 'fail', 'replace', 'append'
        
        Returns:
        --------
        bool
            True si la inserción fue exitosa
        """
        try:
            df.to_sql(nombre_tabla, self.connection, if_exists=if_exists, index=False)
            print(f" DataFrame insertado en tabla '{nombre_tabla}' ({len(df)} filas)")
            return True
            
        except Exception as e:
            print(f"Error al insertar DataFrame en '{nombre_tabla}': {e}")
            return False
    
    def consultar(self, query: str) -> Optional[pd.DataFrame]:
        """
        Ejecuta una consulta SQL y retorna los resultados como DataFrame.
        
        Parameters:
        -----------
        query : str
            Consulta SQL a ejecutar
        
        Returns:
        --------
        pd.DataFrame or None
            Resultados de la consulta o None si hay error
        """
        try:
            df = pd.read_sql_query(query, self.connection)
            print(f" Consulta ejecutada exitosamente ({len(df)} filas)")
            return df
            
        except Exception as e:
            print(f"Error al ejecutar consulta: {e}")
            return None
    
    def listar_tablas(self) -> List[str]:
        """
        Lista todas las tablas en la base de datos.
        
        Returns:
        --------
        List[str]
            Lista con nombres de las tablas
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = [fila[0] for fila in cursor.fetchall()]
            return tablas
            
        except Exception as e:
            print(f"Error al listar tablas: {e}")
            return []
    
    def obtener_info_tabla(self, nombre_tabla: str) -> Optional[pd.DataFrame]:
        """
        Obtiene información sobre las columnas de una tabla.
        
        Parameters:
        -----------
        nombre_tabla : str
            Nombre de la tabla
        
        Returns:
        --------
        pd.DataFrame or None
            Información de las columnas
        """
        try:
            query = f"PRAGMA table_info({nombre_tabla})"
            return self.consultar(query)
            
        except Exception as e:
            print(f"Error al obtener info de tabla '{nombre_tabla}': {e}")
            return None
    
    def eliminar_tabla(self, nombre_tabla: str) -> bool:
        """
        Elimina una tabla de la base de datos.
        
        Parameters:
        -----------
        nombre_tabla : str
            Nombre de la tabla a eliminar
        
        Returns:
        --------
        bool
            True si se eliminó exitosamente
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {nombre_tabla}")
            self.connection.commit()
            print(f"Tabla '{nombre_tabla}' eliminada")
            return True
            
        except Exception as e:
            print(f"Error al eliminar tabla '{nombre_tabla}': {e}")
            return False
    
    def contar_filas(self, nombre_tabla: str) -> int:
        """
        Cuenta el número de filas en una tabla.
        
        Parameters:
        -----------
        nombre_tabla : str
            Nombre de la tabla
        
        Returns:
        --------
        int
            Número de filas en la tabla
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
            resultado = cursor.fetchone()
            return resultado[0] if resultado else 0
            
        except Exception as e:
            print(f"Error al contar filas en '{nombre_tabla}': {e}")
            return 0
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cerrar_conexion()
