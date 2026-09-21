from flask_app.config.mysql_connection import connect_to_mysql
from flask import flash

class Mision:
    def __init__(self, data):
        self.id_mision = data.get('id_mision')
        self.nombre = data.get('nombre') or data.get('titulo') or ''
        self.titulo = self.nombre
        self.descripcion = data.get('descripcion') or ''
        self.fecha = data.get('fecha')
        self.voluntarios_necesarios = data.get('voluntarios_necesarios')
        self.id_usuario = data.get('id_usuario') or data.get('usuario_id')
        self.usuario_id = self.id_usuario
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        
        self.lider = None
        self.voluntarios = []

    @classmethod
    def guardar(cls, formulario):
        """Inserta una nueva misión asegurando claves válidas."""
        datos = dict(formulario)
        if not datos.get('nombre'):
            datos['nombre'] = datos.get('titulo', '')

        query = """
            INSERT INTO misiones (nombre, fecha, voluntarios_necesarios, descripcion, id_usuario)
            VALUES (%(nombre)s, %(fecha)s, %(voluntarios_necesarios)s, %(descripcion)s, %(id_usuario)s);
        """
        return connect_to_mysql('voluntame_db').query_db(query, datos)

    @classmethod
    def obtener_todas_futuras(cls):
        """Obtiene las misiones futuras asociando la información del líder."""
        query = """
            SELECT misiones.*, 
                   usuarios.nombre AS lider_nombre, 
                   usuarios.apellido AS lider_apellido
            FROM misiones
            JOIN usuarios ON misiones.id_usuario = usuarios.id_usuario
            WHERE misiones.fecha >= CURDATE()
            ORDER BY misiones.fecha ASC;
        """
        resultados = connect_to_mysql('voluntame_db').query_db(query)
        misiones = []
        
        if not resultados:
            return misiones

        for fila in resultados:
            mision = cls(fila)
            mision.lider = {
                'nombre': fila.get('lider_nombre'),
                'apellido': fila.get('lider_apellido')
            }
            misiones.append(mision)
        return misiones

    @classmethod
    def obtener_por_id_con_relaciones(cls, formulario):
        query = "SELECT * FROM misiones WHERE id_mision = %(id_mision)s;"
        resultado = connect_to_mysql('voluntame_db').query_db(query, formulario)
        if not resultado:
            return False
        return cls(resultado[0])

    @classmethod
    def eliminar(cls, formulario):
        query = "DELETE FROM misiones WHERE id_mision = %(id_mision)s;"
        return connect_to_mysql('voluntame_db').query_db(query, formulario)

    @staticmethod
    def validar_mision(formulario):
        es_valido = True
        nombre = formulario.get('nombre') or formulario.get('titulo') or ''
        descripcion = formulario.get('descripcion', '')
        fecha = formulario.get('fecha', '')
        voluntarios = formulario.get('voluntarios_necesarios', '')

        if len(str(nombre).strip()) < 3:
            flash("El nombre de la misión debe tener al menos 3 caracteres.", "mision")
            es_valido = False

        if len(str(descripcion).strip()) < 5:
            flash("La descripción debe tener al menos 5 caracteres.", "mision")
            es_valido = False

        if not fecha:
            flash("Debes seleccionar una fecha válida.", "mision")
            es_valido = False

        try:
            vol_num = int(voluntarios)
            if vol_num < 2 or vol_num > 20:
                flash("Los voluntarios necesarios deben estar entre 2 y 20.", "mision")
                es_valido = False
        except (ValueError, TypeError):
            flash("Ingresa un número válido de voluntarios.", "mision")
            es_valido = False

        return es_valido