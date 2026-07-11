from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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

@app.route("/foods")
def food_database():
    return render_template("foods.html", foods=foods)

@app.route("/")
def home():
    return render_template(
        "index.html",
        total_kj=0,
        protein=0,
        current_weight=158.2,
        kj_goal=8500
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
    

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)