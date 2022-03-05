import os
from turtle import title
from urllib import response
from xml.dom.pulldom import ErrorHandler
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
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():
    get_drinks = Drink.query.order_by(Drink.id).all()
    drinks = []
    try:
        if len(get_drinks) > 0:
            for drink in get_drinks:
                drinks.append(drink.short())
            return jsonify({
                'success' : True,
                'drinks' : drinks
            }), 200

        elif len(get_drinks) == 0:
            return jsonify({
                'success' : False,
                'erorr' : 'Unable to find drinks'
            }), 404
    except ValueError as e:
        print(e)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    get_drinks = Drink.query.order_by(Drink.id).all()
    drinks = []
    try:
        if len(get_drinks) > 0:
            for drink in get_drinks:
                drinks.append(drink.long())
            
            return jsonify({
                'success' : True,
                'drinks' : drinks
            }), 200
        
        elif len(get_drinks) == 0:
            return jsonify({
                'success' : False,
                'erorr' : 'Unable to find drinks'
            }), 404
    except ValueError as e:
        print(e)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    body = json.loads(request.data.decode('utf-8'))
    try:
        if 'title' in body and 'recipe' in body:
            drink_title = body['title']
            drink_recipe = json.dumps(body['recipe'])
            drink = Drink(title=drink_title, recipe=drink_recipe)
            drink.insert()
            return jsonify({
                "success" : True,
                "drinks" : drink.long()
            }), 200
        else:
            return jsonify({
                "success" : False,
                "error" : 422,
                "message" : "no title or no recipe in body"
            }), 422
    except ValueError as e:
        print(e)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(token, drink_id):
    body = json.loads(request.data.decode('utf-8'))
    drink_title = body.get('title', None)
    drink_recipe = json.dumps(body.get('recipe', None))
    try:
        drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
        if drink is None:
            abort(404)
        else:
            drink.title = drink_title
            drink.recipe = drink_recipe
            drink.update()
            return jsonify({
                'success' : True,
                'drinks' : drink.long()
            }), 200
    except ValueError as e:
        print(e)
        abort(422)
        


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):
    drink = Drink.query.filter(Drink.id==drink_id).one_or_none()
    if drink is None:
        abort(404)
    else:
        drink.delete()
        return jsonify({
            'success' : True,
            'delete' : drink_id
        }), 200

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success" : False,
        "error" : 404,
        "message" : "NotFound"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(auth):
    return jsonify({
        'success' : False,
        'error': auth.error,
        'status_code' : auth.status_code
    })


if __name__ == "__main__":
    app.debug = True
    app.run()
