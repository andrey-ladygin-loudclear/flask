from flask import render_template

from app import app
from models.recipe import Recipe


@app.route('/')
@app.route('/<int:page>',methods=['GET'])
def dashboard(page=1):
    per_page = 10
    recipes = Recipe.query.order_by(Recipe.id.desc()).paginate(page, per_page, error_out=False)
    return render_template('dashboard.html', recipes=recipes)