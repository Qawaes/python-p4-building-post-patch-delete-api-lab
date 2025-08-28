#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


@app.route('/')
def home():
    return '<h1>Bakery API with CRUD</h1>'


@app.route('/bakeries', methods=['GET'])
def get_bakeries():
    bakeries = [bakery.to_dict() for bakery in Bakery.query.all()]
    return make_response(jsonify(bakeries), 200)


@app.route('/bakeries/<int:id>', methods=['GET'])
def get_bakery(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response(jsonify({"error": "Bakery not found"}), 404)
    return make_response(jsonify(bakery.to_dict()), 200)


@app.route('/baked_goods/by_price', methods=['GET'])
def baked_goods_by_price():
    baked_goods = BakedGood.query.order_by(BakedGood.price.desc()).all()
    baked_goods_serialized = [bg.to_dict() for bg in baked_goods]
    return make_response(jsonify(baked_goods_serialized), 200)


@app.route('/baked_goods/most_expensive', methods=['GET'])
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).first()
    if not most_expensive:
        return make_response(jsonify({"error": "No baked goods found"}), 404)
    return make_response(jsonify(most_expensive.to_dict()), 200)


@app.route('/baked_goods', methods=['POST'])
def create_baked_good():
    data = request.form or request.json  # handle both form-data and JSON
    try:
        new_bg = BakedGood(
            name=data['name'],
            price=float(data['price']),
            bakery_id=int(data['bakery_id'])
        )
        db.session.add(new_bg)
        db.session.commit()
        return make_response(jsonify(new_bg.to_dict()), 201)
    except Exception as e:
        return make_response(jsonify({"error": str(e)}), 400)

@app.route('/bakeries/<int:id>', methods=['PATCH'])
def update_bakery(id):
    bakery = Bakery.query.get(id)
    if not bakery:
        return make_response(jsonify({"error": "Bakery not found"}), 404)

    data = request.form or request.json
    for key, value in data.items():
        if hasattr(bakery, key):
            setattr(bakery, key, value)

    db.session.commit()
    return make_response(jsonify(bakery.to_dict()), 200)


# ----------------- DELETE ROUTE -----------------

@app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    bg = BakedGood.query.get(id)
    if not bg:
        return make_response(jsonify({"error": "Baked good not found"}), 404)

    db.session.delete(bg)
    db.session.commit()
    return make_response(jsonify({"message": "Baked good deleted"}), 200)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
