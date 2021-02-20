from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json


POSTGRES_PASSWORD = '12qwaszx'

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://postgres:{POSTGRES_PASSWORD}@localhost:5432/main_data_storage'
db = SQLAlchemy(app)
  

class MainData(db.Model):  
    __tablename__ = 'main_data_storage'
    id_number = db.Column(db.Integer, primary_key=True,autoincrement=True)
    person_id = db.Column(db.String, unique=True)
    person_name = db.Column(db.String)
    methods = db.Column(db.String)
    main_photo = db.Column(db.String)
    thumbnail = db.Column(db.String)

CORS(app)

@app.route('/get-main-data')
def getData():
    therapists = MainData.query.all()
    results = [
            {
                'id_number': therapist.id_number,
                'person_id': therapist.person_id,
                'person_name': therapist.person_name,
                'person_methods': therapist.methods,
                'main_photo': therapist.main_photo,
                'thumbnail': therapist.thumbnail
            } for therapist in therapists]
    return json.dumps(results)


if __name__ == '__main__':
    app.run()