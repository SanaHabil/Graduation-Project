from pickle import GET
import re
from flask_app import app
from flask import Flask, flash, request, redirect, url_for, render_template, session
from flask import send_from_directory
import urllib.request
import os
from werkzeug.utils import secure_filename
from flask_app.models import user
from flask_app.models import recipe
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

UPLOAD_FOLDER = 'flask_app/static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#UPLOAD_FOLDER = join(dirname(realpath(__file__)), 'static/uploads/..')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    

app.secret_key = 'login and register'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload_recipe')
def upload_recipe_page():
    if 'user_id' not in session:
        return redirect('/reset')
    data ={
        'id': session['user_id']
    } 
    return render_template('add_recipe.html', current_user = user.User.show_one_user(data))

@app.route('/upload_photo', methods=['POST'])
def upload_image():
    if 'user_id' not in session:
        return redirect('/reset')
    userdata ={
        'id': session['user_id']
    } 
    data = {
        "title": request.form['title'],
        "details": request.form['details'],
        "user_id" : request.form['user_id'],
        }
    all_recipes = recipe.Recipe.get_all_recipes()    
    if not recipe.Recipe.validate_recipe_on_submit(data):
        # we redirect to the template with the form.
        return redirect(request.url)        
    recipe.Recipe.add_recipe(data)
        
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
        #if request.method == 'POST':
    #for file in request.files.getlist('file'):        
    if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #file.save(file.filename)
            #print('upload_image filename: ' + filename)
            #flash('Image successfully uploaded and displayed below')
            #return render_template('results.html', current_user = user.User.show_user(userdata),all_recipes=all_recipes, data=data, filename=filename )
            return redirect('/results')
            #return redirect('/results')
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


#@app.route('/display/<filename>')
#def display_image(filename):
    #print('display_image filename: ' + filename)
    # return redirect(url_for('static', filename='uploads/' + filename), code=301)
#   return redirect(url_for('static', filename='uploads/' +  str(user_id)), code=301)


@app.route("/recipes/edit",methods=['POST'])
def edit_one_recipe():
    if not recipe.Recipe.validate_recipe_on_update(request.form):
        return  redirect(request.referrer)
    if 'user_id' not in session:
        return redirect('/reset')
    data = {
        "id": request.form['id'],
        "title": request.form['title'],
        "details": request.form['details'],
        "user_id" : request.form['user_id'],
        }
    recipe.Recipe.update_one_recipe(data)
    return redirect('/results')

@app.route('/edit_recipe/<int:id>')
def edit_recipe(id):    
    if 'user_id' not in session:
        return redirect('/reset')
    recipe_data = {
            "id": id
    }
    data ={
        "id": session['user_id']
    } 
    return render_template("edit_user_recipe.html",current_user = user.User.show_one_user(data), one_recipe = recipe.Recipe.show_one_recipe(recipe_data))
    
@app.route('/recipes/<int:id>')
def view_instructions_page(id):
    if 'user_id' not in session:
        return redirect('/reset')
    recipe_data={
            'id': id
    }
    data ={
        'id': session['user_id']
    } 
    print(data)
    return render_template("view_instructions.html",current_user = user.User.show_one_user(data), one_recipe = recipe.Recipe.show_one_recipe(recipe_data))

@app.route('/delete/<int:id>')
def delete_recipe(id):
    recipe.Recipe.delete(id)
    return redirect('/results')


if __name__=="__main__":
    app.run(debug=True)

