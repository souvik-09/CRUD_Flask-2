from flask import Flask, jsonify, request
from config import SECRET_KEY, db
from Models.product import Product
from os import environ, path, getcwd
from dotenv import load_dotenv

load_dotenv(path.join(getcwd(), '.env'))


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = environ.get('DB_URI')
    app.config["SQLALCHEMY_ECHO"] = False
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = SECRET_KEY
    db.init_app(app)
    print("DB Initialized Successfully")

    with app.app_context():
        @app.route('/')
        def index():
            return jsonify("Hello World!")

        @app.route('/create', methods=['POST'])
        def add_product():
            if request.method == 'POST':
                product_name = request.form['product_name']
                quantity = request.form['quantity']
                price = request.form['price']
                product = Product(product_name=product_name, quantity=quantity, price=price)
                db.session.add(product)
                db.session.commit()

                product_dict = {
                    'id': product.id,
                    'product_name': product.product_name,
                    'quantity': product.quantity,
                    'price': product.price
                }

                return jsonify(product_dict)

        @app.route('/read', methods=['GET'])
        def retrieve_all_products():
            product = Product.query.all()
            product_list = []

            for products in product:
                product_dict = {
                    'id': products.id,
                    'product_name': products.product_name,
                    'quantity': products.quantity,
                    'price': products.price
                }
                product_list.append(product_dict)

            return jsonify(product_list)

        @app.route('/read/<int:id>')
        def retrieve_single_product(id):
            product = Product.query.filter_by(id=id).first()
            if product:
                product_dict = {
                    'id': product.id,
                    'product_name': product.product_name,
                    'quantity': product.quantity,
                    'price': product.price
                }
                return jsonify(product_dict)
            else:
                return jsonify(f"Product with id {id} Doesn't exist!")

        @app.route('/update/<int:id>', methods=['PUT', 'PATCH'])
        def update_product(id):
            product = db.session.get(Product, id)
            if not product:
                return jsonify({'message': 'Product not found'})

            if request.method == 'PUT':

                product_name = request.form['product_name']
                quantity = request.form['quantity']
                price = request.form['price']
                product.product_name = product_name
                product.quantity = quantity
                product.price = price
            elif request.method == 'PATCH':
                # Handle partial update with PATCH method
                if 'product_name' in request.form:
                    product.product_name = request.form['product_name']
                if 'quantity' in request.form:
                    product.quantity = request.form['quantity']
                if 'price' in request.form:
                    product.price = request.form['price']

            db.session.add(product)  # Add the updated object to the session
            db.session.commit()

            # Create a dictionary representation of the updated People object
            product_dict = {
                'id': product.id,
                'product_name': product.product_name,
                'quantity': product.quantity,
                'price': product.price
            }

            return jsonify(product_dict)

        @app.route('/delete/<int:id>/', methods=['DELETE'])
        def delete_product(id):
            if request.method == 'DELETE':
                product = Product.query.filter_by(id=id).first()
                if product:
                    db.session.delete(product)
                    db.session.commit()
                    return jsonify("Product Successfully Deleted!")
                else:
                    return jsonify(f"Product cannot be deleted because none of the people exists with id {id}")

        # db.drop_all()
        db.create_all()
        db.session.commit()
        return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='localhost', port=5069)
