import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES

@app.route('/drinks')
def get_drinks():
    all_drinks = Drink.query.all()
    drinks = []
    for drink in all_drinks:
        print("lol")
        drinks.append(drink.short())
    print("lol")
    return jsonify({"success": True, "drinks": drinks})

@app.route('/drinks-detail')
@requires_auth(permission="get:drinks-detail")
def drinks_detail(payload):
    all_drinks = Drink.query.all()
    drinks = []
    for drink in all_drinks:
        drinks.append(drink.long())
    return jsonify({"success": True, "drinks": drinks})

@app.route('/drinks', methods=['POST'])
@requires_auth(permission="post:drinks")
def post_drinks(payload):
    data = request.get_json()
    if isinstance(data["recipe"], list):
        ingredients_list = json.dumps(data["recipe"])
    else:
        ingredients_list = json.dumps([data["recipe"]])
    drink_name = data["title"]
    new_drink = Drink(
        title=drink_name,
        recipe=ingredients_list)
    new_drink.insert()
    return  jsonify({'success': True, 'drinks': [new_drink.long()]})


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth(permission="patch:drinks")
def patch_drinks(payload, drink_id):
    try:
        data = request.get_json()
        drink = Drink.query.get(drink_id)
    except:
        abort(422)
    if "title" in data:
        drink.title = data["title"]
    if "recipe" in data:
        if isinstance(data["recipe"], list):
            drink.recipe = json.dumps(data["recipe"])
        else:
            drink.recipe = json.dumps([data["recipe"]])
    drink.update()
    return  jsonify({'success': True, 'drinks': [drink.long()]})


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth(permission="delete:drinks")
def delete_drinks(payload, drink_id):
    try:
        drink = Drink.query.get(drink_id)
    except:
        abort(422)
    drink.delete()
    return  jsonify({'success': True, 'delete': drink_id})

## Error Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

@app.errorhandler(404)
def not_found(error):
    return  jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
                    "success": False, 
                    "error": error.status_code,
                    "message": error.error
                    }), error.status_code
