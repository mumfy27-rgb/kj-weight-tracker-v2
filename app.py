from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

weights = []

foods = [
    {
        "name": "Overnight Oats",
        "kj": 1500,
        "protein": 35,
        "favourite": True
    },
    {
        "name": "Protein Water",
        "kj": 300,
        "protein": 30,
        "favourite": True 
    },
    {
        "name": "Ryvita and cheese ",
        "kj": 430,
        "protein": 10,
        "favourite": True
    },
    {
        "name": "Cottage Cheese",
        "kj": 420,
        "protein": 25,
        "favourite": True
    }
    
]

today_foods = []


@app.route("/foods")
def food_database():
    return render_template("foods.html", foods=foods)

@app.route("/")
def home():
    total_kj = sum(food["kj"] for food in today_foods)
    protein = sum(food["protein"] for food in today_foods)
    current_weight = weights[-1]["weight"] if weights else 0
    return render_template(
        "index.html",
        total_kj=total_kj,
        protein=protein,
        current_weight=current_weight,
        kj_goal=8500,
        today_foods=today_foods,
        weights=weights

    )


@app.route("/add_food", methods=["GET", "POST"])
def add_food():

    if request.method == "POST":
        food_name = request.form["food_name"]
        kj = int(request.form["kj"])
        protein = int(request.form["protein"])

        favourite = "favourite" in request.form

        new_food = {
            "name": food_name,
            "kj": kj,
            "protein": protein,
            "favourite": favourite
        }
        
        foods.append(new_food)
  

        return redirect(url_for("food_database"))

    return render_template(
        "add_food.html",
        editing=False,
        food=None      
        )

@app.route("/edit_food/<int:food_index>", methods=["GET","POST"])
def edit_food(food_index):
    if not 0 <= food_index < len(foods):
        return redirect(url_for("food_database"))

    food = foods[food_index]
    if request.method == "POST":
        food["name"] = request.form["food_name"]
        food["kj"] = int(request.form["kj"])
        food["protein"] = int(request.form["protein"])
        food["favourite"] = "favourite"  in request.form

        return redirect(url_for("food_database"))

    return render_template(
        "add_food.html",
        editing=True,
        food=food,
        food_index=food_index        
    )

@app.route("/delete_food/<int:food_index>")
def delete_food(food_index):

    if 0 <= food_index < len(foods):
        foods.pop(food_index)
    return redirect(url_for("food_database"))

@app.route("/add_to_today/<int:food_index>")
def add_to_today(food_index):

    if 0 <= food_index < len(foods):
        today_foods.append(foods[food_index])

    return redirect(url_for("food_database"))



@app.route("/remove_from_today/<int:food_index>")
def remove_from_today(food_index):

    if 0 <= food_index < len(today_foods):
        today_foods.pop(food_index)
    return redirect(url_for("home"))



@app.route("/add_weight", methods=["GET", "POST"])
def add_weight():


    if request.method == "POST":


        weight = float(request.form["weight"])
        date = request.form["date"]

        weights.append({
                "date":date,
                "weight": weight
        })

        return redirect(url_for("home"))
    
    return render_template("add_weight.html")
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)