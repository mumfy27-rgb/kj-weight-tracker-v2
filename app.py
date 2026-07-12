from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from datetime import date, datetime
import json
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    kj = db.Column(db.Integer, nullable=False)
    protein = db.Column(db.Integer, nullable=False)
    favourite = db.Column(db.Boolean, default=False)

BASE_DIR = Path(__file__).resolve().parent


def load_data(filename):
    file_path = BASE_DIR / filename

    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_data(filename, data):
    file_path = BASE_DIR / filename

    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


weights = load_data("weights.json")
foods = load_data("foods.json")
today_foods = load_data("food_log.json")


# Clean old display-only fields from the saved food log
food_log_cleaned = False

for food in today_foods:
    if "display_date" in food:
        food.pop("display_date")
        food_log_cleaned = True

    if "date" not in food:
        food["date"] = date.today().isoformat()
        food_log_cleaned = True

if food_log_cleaned:
    save_data("food_log.json", today_foods)


@app.route("/foods")
def food_database():
    database_foods = Food.query.all()
    return render_template("foods.html", foods=database_foods)


@app.route("/")
def home():
    today = date.today().isoformat()

    today_foods_with_indexes = [
        (
            index,
            {
                **food,
                "display_date": datetime.strptime(
                    food["date"],
                    "%Y-%m-%d"
                ).strftime("%d %b %Y")
            }
        )
        for index, food in enumerate(today_foods)
        if food.get("date") == today
    ]

    total_kj = sum(
        food["kj"]
        for index, food in today_foods_with_indexes
    )

    protein = sum(
        food["protein"]
        for index, food in today_foods_with_indexes
    )

    current_weight = weights[-1]["weight"] if weights else 0
    kj_remaining = 8500 - total_kj

    return render_template(
        "index.html",
        total_kj=total_kj,
        protein=protein,
        current_weight=current_weight,
        kj_goal=8500,
        kj_remaining=kj_remaining,
        today_foods=today_foods_with_indexes,
        weights=weights
    )


@app.route("/add_food", methods=["GET", "POST"])
def add_food():

    if request.method == "POST":
        food_name = request.form["food_name"]
        kj = int(request.form["kj"])
        protein = int(request.form["protein"])
        favourite = "favourite" in request.form

        new_food = Food(
            name=food_name,
            kj=kj,
            protein=protein,
            favourite=favourite
        )

        db.session.add(new_food)
        db.session.commit()
        return redirect(url_for("food_database"))

    return render_template(
        "add_food.html",
        editing=False,
        food=None
    )


@app.route("/edit_food/<int:food_index>", methods=["GET", "POST"])
def edit_food(food_index):

    food = db.session.get(Food, food_index)

    if food is None:
        return redirect(url_for("food_database"))

    if request.method == "POST":
        food.name = request.form["food_name"]
        food.kj = int(request.form["kj"])
        food.protein = int(request.form["protein"])
        food.favourite = "favourite" in request.form

        db.session.commit()

        return redirect(url_for("food_database"))

    return render_template(
        "add_food.html",
        editing=True,
        food=food,
        food_index=food.id
    )

@app.route("/delete_food/<int:food_index>")
def delete_food(food_index):

    food = db.session.get(Food, food_index)

    if food is not None:
        db.session.delete(food)
        db.session.commit()

    return redirect(url_for("food_database"))

@app.route("/add_to_today/<int:food_index>")
def add_to_today(food_index):

    if 0 <= food_index < len(foods):
        food = foods[food_index]

        today_foods.append({
            "date": date.today().isoformat(),
            "name": food["name"],
            "kj": food["kj"],
            "protein": food["protein"]
        })

        save_data("food_log.json", today_foods)

    return redirect(url_for("food_database"))


@app.route("/remove_from_today/<int:food_index>")
def remove_from_today(food_index):

    if 0 <= food_index < len(today_foods):
        today_foods.pop(food_index)
        save_data("food_log.json", today_foods)

    return redirect(url_for("home"))


@app.route("/add_weight", methods=["GET", "POST"])
def add_weight():

    if request.method == "POST":
        weight = float(request.form["weight"])
        weight_date = request.form["date"]

        weights.append({
            "date": weight_date,
            "weight": weight
        })

        save_data("weights.json", weights)

        return redirect(url_for("home"))

    return render_template("add_weight.html")


with app.app_context():
    db.create_all()

    if Food.query.count() == 0:
        for food in foods:
            new_food = Food(
                name=food["name"],
                kj=food["kj"],
                protein=food["protein"],
                favourite=food["favourite"]
            )

            db.session.add(new_food)

        db.session.commit()
        print("Foods migrated to SQLite.")

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)