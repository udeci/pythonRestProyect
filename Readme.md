crear usuario
curl -X POST -H "Content-Type: application/json" -d '{"username": "usuario_prueba", "password": "mipassword123"}' http://127.0.0.1:5000/register

hacer login
curl -X POST -H "Content-Type: application/json" -d '{"username": "usuario_prueba", "password": "mipassword123"}' http://127.0.0.1:5000/login


falla al ingresar
curl -X POST -H "Content-Type: application/json" -d '{"username": "usuario_prueba", "password": "password_incorrecta"}' http://127.0.0.1:5000/login