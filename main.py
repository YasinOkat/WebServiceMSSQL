from flask import Flask, jsonify, request
from datetime import datetime
import pyodbc

app = Flask(__name__)
db_connection_string = 'DRIVER={SQL Server};SERVER=localhost;DATABASE=Veritabani;UID=sa;PWD=1234'


def get_database_connection():
    conn = pyodbc.connect(db_connection_string)
    cursor = conn.cursor()
    return conn, cursor


@app.route("/", methods=['GET'])
def home():
    return "Merhaba."


@app.route('/login', methods=['POST'])
def login():
    conn, cursor = get_database_connection()

    data = request.get_json()
    kullaniciadi = data.get('kullaniciadi')
    sifre = data.get('sifre')

    query = "SELECT COUNT(*) FROM Kullanicilar WHERE KullaniciAdi = ? AND Sifre = ?"
    cursor.execute(query, kullaniciadi, sifre)
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    success = result[0] > 0
    return jsonify({'success': success})


@app.route('/getArabalar', methods=['GET'])
def get_arabalar():
    conn, cursor = get_database_connection()

    query = "SELECT Plaka FROM Arabalar"
    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    arabalar = [{'Plaka': row[0]} for row in result]
    return jsonify(arabalar)


@app.route('/arabaBirak', methods=['POST'])
def araba_birak():
    conn, cursor = get_database_connection()

    giris_saati_str = datetime.now()
    print(giris_saati_str)

    data = request.get_json()
    kilometer = data.get('kilometer')
    kullanilan_plaka = data.get('plaka')

    query = "UPDATE TBLLOG2 SET Kilometer = ?, GirisSaati = ? WHERE ID = (SELECT TOP(1) ID FROM" \
            " TBLLOG2 WHERE Plaka = ? ORDER BY ID DESC)"
    query2 = "DELETE FROM KullanilanArabalar2 WHERE KullanilanPlaka = ?"
    query3 = "INSERT INTO Arabalar (Plaka) VALUES (?)"

    cursor.execute(query, kilometer, giris_saati_str, kullanilan_plaka)
    cursor.execute(query2, kullanilan_plaka)
    cursor.execute(query3, kullanilan_plaka)
    conn.commit()

    cursor.close()
    conn.close()

    if request.content_type != 'application/json':
        return jsonify({'error': 'Request content-type should be application/json'}), 400

    return jsonify({'message': 'success'})


@app.route('/insertData', methods=['POST'])
def insert_data():
    conn, cursor = get_database_connection()

    data = request.get_json()
    plaka = data.get('plaka')
    ad = data.get('ad')
    hedef = data.get('hedef')
    amac = data.get('amac')
    cikis_saati_str = datetime.now()

    query = "INSERT INTO TBLLOG2 (CikisSaati, Plaka, Ad, Hedef, Amac) VALUES (?, ?, ?, ?, ?)"
    query2 = "INSERT INTO KullanilanArabalar2(KullaniciAdi, KullanilanPlaka, CikisSaati, GidilenYer) " \
             "VALUES (?, ?, ?, ?)"

    cursor.execute(query, cikis_saati_str, plaka, ad, hedef, amac)
    cursor.execute(query2, ad, plaka, cikis_saati_str, hedef)
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'success'})


@app.route('/deleteData', methods=['POST'])
def delete_data():
    try:
        conn, cursor = get_database_connection()

        data = request.get_json()
        plaka = data.get('plaka')
        print('plaka:', plaka)

        query = "DELETE FROM Arabalar WHERE Plaka = ?"
        cursor.execute(query, plaka)
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({'message': 'success'})
    except pyodbc.Error as e:
        return jsonify({'error': str(e)})


@app.route('/getKullanilanArabalar', methods=['GET'])
def get_kullanilan_arabalar():
    conn, cursor = get_database_connection()

    query = "SELECT * FROM KullanilanArabalar2"
    cursor.execute(query)
    result = cursor.fetchall()

    cursor.close()
    conn.close()

    kullanilan_arabalar = []
    for row in result:
        kullanilan_arabalar.append({
            'KullanilanPlaka': row[0],
            'KullaniciAdi': row[1],
            'GidilenYer': row[2],
            'CikisSaati': row[3]
        })

    print(kullanilan_arabalar)

    return jsonify(kullanilan_arabalar)


if __name__ == '__main__':
    app.run(debug=True, host='192.168.1.193')
