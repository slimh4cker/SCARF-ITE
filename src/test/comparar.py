# Código para comparar un rostro en vivo con los registrados

# comparar.py
import numpy as np
import json
from db.config import conectar

# Umbral para decidir si el rostro coincide con algún usuario
THRESHOLD = 0.45

def cargar_usuarios():
    """Carga todos los usuarios y sus embeddings desde la base de datos"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, embedding FROM usuarios")
    data = []
    for id, nombre, emb_json in cursor.fetchall():
        emb = np.array(json.loads(emb_json))
        data.append((id, nombre, emb))
    conn.close()
    return data

def comparar_embedding(nuevo_embedding):
    """
    Compara un embedding con los de la base de datos.
    
    Args:
        nuevo_embedding (np.array): vector del rostro a comparar

    Returns:
        nombre (str): nombre del usuario reconocido o "DESCONOCIDO"
        distancia (float): distancia mínima encontrada
    """
    usuarios = cargar_usuarios()
    if not usuarios:
        return "DESCONOCIDO", None

    distancias = [np.linalg.norm(u[2] - nuevo_embedding) for u in usuarios]
    idx_min = np.argmin(distancias)
    distancia_min = distancias[idx_min]

    if distancia_min < THRESHOLD:
        return usuarios[idx_min][1], distancia_min
    else:
        return "DESCONOCIDO", distancia_min

# Ejemplo de uso
if __name__ == "__main__":
    # Supón que tienes un embedding de prueba
    ejemplo_embedding = np.random.rand(128)  # solo para demo
    nombre, distancia = comparar_embedding(ejemplo_embedding)
    print(f"Usuario reconocido: {nombre}, distancia: {distancia}")
