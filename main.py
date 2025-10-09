import sqlite3
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt


app = Flask(__name__)
bcrypt = Bcrypt(app)
DATABASE = 'users.db'



def get_db_connection():
    """Establece una conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acceder a las filas como diccionarios
    return conn


def init_db():
    """Crea la tabla de usuarios si no existe."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


init_db()

@app.route('/register', methods=['POST'])
def register():
    """Endpoint para registrar un nuevo usuario."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Faltan datos de usuario o contraseña"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    try:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        conn.close()

        return jsonify({"message": f"Usuario '{username}' registrado exitosamente"}), 201

    except sqlite3.IntegrityError:
        return jsonify({"message": "El nombre de usuario ya existe"}), 409
    except Exception as e:
        return jsonify({"message": f"Error al registrar: {e}"}), 500



@app.route('/login', methods=['POST'])
def login():
    """Endpoint para iniciar sesión."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Faltan datos de usuario o contraseña"}), 400

    conn = get_db_connection()

    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user:
        password_hash = user['password_hash']
        if bcrypt.check_password_hash(password_hash, password):
            return jsonify({
                "message": "Login exitoso",
                "user_id": user['id'],
                "username": user['username'],
                "token": "ejemplo-de-token-jwt-generado-aqui"
            }), 200
        else:
            return jsonify({"message": "Usuario o contraseña inválidos"}), 401
    else:
        return jsonify({"message": "Usuario o contraseña inválidos"}), 401


if __name__ == '__main__':
    app.run(debug=True)