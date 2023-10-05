import random
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    __tablename__ = 'cafe'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe={
        "can_take_calls":random_cafe.can_take_calls,
        "coffee_price":random_cafe.coffee_price,
        "has_sockets":random_cafe.has_sockets,
        "has_toilet":random_cafe.has_toilet,
        "has_wifi":random_cafe.has_wifi,
        "id":random_cafe.id,
        "img_url":random_cafe.img_url,
        "location":random_cafe.location,
        "map_url":random_cafe.map_url,
        "name":random_cafe.name,
        "seats":random_cafe.seats})


@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe))
    print("print result")
    print(result)
    all_cafes = result.scalars().all()
    print("print all_cafes")
    print(all_cafes)
    cafes_list = []
    for cafe in all_cafes:
        print(type(cafe))
        cafe_dict = cafe.to_dict()
        print(cafe_dict)
        cafes_list.append(cafe_dict)
    return jsonify(cafes=cafes_list)


@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("location")
    print(query_location)

    try:
        # Search for the cafe at the specified location
        cafes = db.session.query(Cafe).filter(Cafe.location == query_location).all()
        if cafes:
            # Convert the cafes to dictionaries and return as a list
            cafes_list = [cafe.to_dict() for cafe in cafes]
            return jsonify(cafes=cafes_list)
        else:
            # If no cafes are found, return a 404 error response
            return jsonify(error={"Not Found": "Sorry, we don't have cafes at that location."}), 404

    except NoResultFound:
        # Handle the case where no cafes match the location
        return jsonify(error={"Not Found": "Sorry, we don't have cafes at that location."}), 404


## HTTP POST - Create Record
@app.route("/add", methods=["Post"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_sockets=bool(request.form.get("has_sockets")),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        coffee_price=request.form.get("coffee_price"),
    )

    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


## HTTP PUT/PATCH - Update Record

@app.route("/update-price/<int:cafe_id>", methods=["Patch"])
def patch_cafe_detail(cafe_id):
    cafe = db.get_or_404(Cafe,cafe_id)
    new_price = request.args.get("new_price")
    try:
        if cafe:
            cafe.coffee_price = new_price
            db.session.commit()
            return jsonify(response={"success": "Successfully updated the price."})
        else:
            # If no cafes are found, return a 404 error response
            return jsonify(error={"Bad Request": "Sorry, we don't have cafes at that location."}), 404

    except NoResultFound:
        # Handle the case where no cafe match the location
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404


## HTTP DELETE - Delete Record
@app.route("/report-closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe = db.get_or_404(Cafe,cafe_id)
    api_key = request.args.get("api-key")
    try:
        if api_key == "" :
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully delete the cafe."})
        else:
            return jsonify(error={"error": "Sorry, that is not allowed. Make sure you have the correct api_key"}), 404
    except NoResultFound:
        # Handle the case where no cafe match the location
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database"}), 404


if __name__ == '__main__':
    app.run(debug=True)
