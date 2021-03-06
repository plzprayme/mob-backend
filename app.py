# -*- coding: utf-8 -*-

from flask import Flask
from sqlalchemy import create_engine, text
from flask import jsonify
from flask_cors import CORS
from row_to_json import row2json

app = Flask(__name__)
CORS(app)
app.config.from_pyfile('config.py')

database = create_engine(app.config['DB_URL'], encoding='utf8')


@app.route('/')
def get_areas():
    sql = text('SELECT ar.id, name, latitude, longitude, pred_infected, susceptible, infected, site_area, duration, '
               'vent_rate, scale,  DATE_FORMAT(MAX(im.history), "%e, %M, %Y") AS date FROM areas AS ar JOIN images '
               'AS im WHERE ar.id = im.area_id AND im.is_svg = 0 GROUP BY ar.id')
    res = jsonify({})
    with database.connect() as db:
        rows = db.execute(sql)
        res = jsonify(row2json(rows))
    return res


@app.route('/area/<id>/images')
def get_images(id):
    sql = text('SELECT area_id, DATE_FORMAT(history, "%e, %M, %Y") AS date, image FROM images WHERE '
               'area_id = :id AND is_svg = :bool ORDER BY history DESC')
    res = jsonify({})
    with database.connect() as db:
        svg_image = db.execute(sql.params(id=id, bool=1))
        area_images = db.execute(sql.params(id=id, bool=0))
        res = {'svg': svg_image.fetchone()['image'], 'images': row2json(area_images)}
    return res


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
