#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

# Methods that do not need an ID: GET and POST
class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        restaurant_list = [
                {"id": restaurant.id, "name": restaurant.name, "address": restaurant.address} for restaurant in restaurants
            ]

        if restaurants:
            response_body = restaurant_list
            response_status = 200

        else:
            response_body = {"error":"No restaurants found"}
            response_status = 404

        response = make_response(jsonify(response_body), response_status)
        return response    
    
api.add_resource(RestaurantList, '/restaurants')    

class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        pizza_list = [
                {"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients} for pizza in pizzas
            ]

        if pizzas:
            response_body = pizza_list
            response_status = 200

        else:
            response_body = {"error":"No pizzas found"}
            response_status = 404

        response = make_response(jsonify(response_body), response_status)
        return response    
    
api.add_resource(PizzaList, '/pizzas')    

class CreateRestaurantPizza(Resource):
    def post(self):
        data = request.get_json() or {}
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")
        price = data.get("price")

        if not pizza_id or not restaurant_id or price is None:
            return {"errors":"Missing required fields: pizza_id, restaurant_id or price."}, 400

        if not (1 <= price <= 30):
            return {"errors":["validation errors"]}, 400
        
        pizza = Pizza.query.get(pizza_id)
        if not pizza:
            return{"errors":[f"Pizza with ID {pizza_id} not found."]}, 404
        
        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            return{"errors":[f"Restaurant with ID {restaurant_id} not found."]}, 404
        
        restaurant_pizza = RestaurantPizza(
            pizza_id=pizza_id,
            restaurant_id=restaurant_id,
            price=price
        )
        db.session.add(restaurant_pizza)
        db.session.commit()

        response_body = {
            "id" : restaurant_pizza.id,
            "pizza":{
                "id":pizza.id,
                "name":pizza.name,
                "ingredients":pizza.ingredients
            },
            "pizza_id": restaurant_pizza.pizza_id,
            "restaurant":{
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            },
            "restaurant_id":restaurant_pizza.restaurant_id,
            "price":restaurant_pizza.price
        }
        return response_body, 201
    
api.add_resource(CreateRestaurantPizza, '/restaurant_pizzas')    

class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        
        if restaurant:
            restaurant_details = {
            "address": restaurant.address,
            "id": restaurant.id,
            "name": restaurant.name,
            "restaurant_pizzas": [
                {
                    "id": pizza.id,
                    "pizza":{
                        "id": pizza.id,
                        "ingredients": pizza.ingredients,
                        "name": pizza.name
                    },
                    "pizza_id": pizza.id,
                    "price": pizza.price,
                    "restaurant_id": pizza.restaurant.id
                }
                for pizza in restaurant.pizzas
            ]
        }
            response_body = restaurant_details
            response_status = 200
        else: 
            response_body = {"error":"Restaurant not found"}
            response_status = 404

        response = make_response(jsonify(response_body), response_status)
        return response    
   
    def delete(self, id):
        restaurant = Restaurant.query.get(id)

        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            response_body = {'message':f'Restaurant with id {id} has been deleted successfully.'}
            response_status = 204
        else:
            response_body = {"error":"Restaurant not found"}
            response_status = 404

        response = make_response(jsonify(response_body), response_status)
        return response    
api.add_resource(RestaurantById, '/restaurants/<int:id>')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
