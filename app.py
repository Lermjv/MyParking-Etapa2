from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for
)

import csv, math,json


app = Flask(__name__)
app.secret_key = 'secretkey'

@app.route('/')
def initial():
    return redirect(url_for('login'))

#tela de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': #espera o usuário enviar dados
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        
        if User.verify_username_password(username, password): #verifica se usuario e senha consedem entrada
            return redirect(url_for('profile') + '?username=' + username) #redireciona para pagina principal passando nome do usuário

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = request.args.get('username')
    return render_template('menu.html', user = username)


@app.route('/localizador')
def localizador():
    return render_template('localizador.html')

@app.route('/parking')
def parking_listings():
    latitude = request.args.get('latitude')
    longitude = request.args.get('longitude')
    radius = request.args.get('radius')

    if latitude is None or longitude is None:
        # Da erro caso não sejam fornecidos lat ou long
        return jsonify({'error': 'Localização inválida'})

    latitude = float(latitude)
    longitude = float(longitude)
    radius = float(radius)

    # Filtra vagas disponíveis em base de sua distancia
    nearby_spots = Vaga.get_nearby_parking_spots(latitude, longitude, radius)

    spots_json = json.dumps([spot.__dict__ for spot in nearby_spots])

    return render_template('parking_listings.html', spots=spots_json,latitude = latitude,longitude = longitude,vagas=nearby_spots)

# Classe que remete a ações do usuário
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'
    
    def verify_username_password(username, password):
        with open ('banco_usuarios.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if row[0] == username:
                    if row[1] == password:
                        return True


# Classe que remete a ações realizadas sobre a vaga
class Vaga:
    def __init__(self, nome, endereço, preço, avaliabilidade, latitude, longitude, distancia):
        self.nome = nome
        self.endereço = endereço
        self.preço = preço
        self.avaliabilidade = avaliabilidade
        self.latitude = latitude
        self.longitude = longitude
        self.distancia = distancia

    # Filtra vagas de acordo com distancia requerida elo usuário e disponibilidade
    def get_nearby_parking_spots(user_latitude, user_longitude, radius):
        
        # recebe vagas disponiveis do banco de dados
        parking_spots = Vaga.lê_banco_vagas()

        # distância máxima do usuário até a vaga em kilometros 
        MAX_RADIUS = radius/1000  

        nearby_spots = []
        for spot in parking_spots:
            spot_latitude = float(spot.latitude)
            spot_longitude = float(spot.longitude)
            spot.distancia = Vaga.calculate_distance(user_latitude, user_longitude, spot_latitude, spot_longitude)

            if spot.distancia <= MAX_RADIUS:
                spot.distancia = round(spot.distancia, 3)
                nearby_spots.append(spot)

        return nearby_spots


    def lê_banco_vagas():
        vagas=[]
        with open ('banco_vagas.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                if row[3] == '1':
                    vagas.append(Vaga(row[0],row[1],row[2],row[3],row[4],row[5],row[6]))

            return vagas

    def calculate_distance(lat1, lon1, lat2, lon2):
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Calculo de distancia a partir de longitude e latidude
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        radius = 6371  # Raio da Terra
        distance = radius * c

        return distance