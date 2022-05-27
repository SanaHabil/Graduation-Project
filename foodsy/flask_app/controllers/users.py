from pickle import GET
import re
from unittest import result
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

@app.route('/')
def index():
    return render_template('images_slideshow.html')

@app.route('/testing')
def testing():
    return render_template('testing.html')
    
@app.route('/login_pg')
def login_pg():
    return render_template('login.html')     

@app.route('/home')
def home_page():
    return render_template('images_slideshow.html')

@app.route('/slideshow')
def slideshow_page():
    return render_template('slideshow.html')


@app.route('/register', methods=['POST'])
def register():
    if not user.User.validate_user(request.form):
        # we redirect to the template with the form.
        return redirect('/')
    # ... do other things
    pw_hash = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
    # put the pw_hash into the data dictionary
    data = {
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email_address": request.form['email_address'],
        "address": request.form['address'],
        "state": request.form['state'],
        "password" : pw_hash,
        "confirm_password" : pw_hash,
    }
    # Call the save @classmethod on User
    id = user.User.add_user(data)
    # store user id into session
    session['user_id'] = id
    return redirect("/results")

@app.route('/results')
def show_results():
    if 'user_id' not in session:
        return redirect('/reset')
    userdata ={
        'id': session['user_id']
    } 
    all_recipes = recipe.Recipe.get_all_recipes()
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("results.html",all_recipes=all_recipes, current_user = user.User.show_one_user(userdata), files=files, unfavorited_recipes=recipe.Recipe.unfavorited_recipe(userdata))

@app.route('/reset')
def reset():
    session.clear()
    return redirect("/home")

@app.route('/login', methods=['POST'])
def login():
    # see if the username provided exists in the database
    data = { "email_address" : request.form["email_address"] }
    user_in_db = user.User.get_by_email(data)
    # user is not registered in the db
    if not user_in_db:
        flash("Invalid Email/Password", "login")
        return redirect('/login_pg')
    if not bcrypt.check_password_hash(user_in_db.password, request.form['password']):
        # if we get False after checking the password
        flash("Invalid Email/Password", "login")
        return redirect('/login_pg')
    # if the passwords matched, we set the user_id into session
    session['user_id'] = user_in_db.id
    # never render on a post!!!
    return redirect('/results')

@app.route('/edit_user')
def  edituser():
    if 'user_id' not in session:
        return redirect('/reset')
    userdata ={
        'id': session['user_id']
    } 
    return render_template("edit_user_profile.html", current_user = user.User.show_one_user(userdata) )

@app.route('/edit_user/<int:id>')
def edit_user(id):
    if 'user_id' not in session:
        return redirect('/reset')
    user_data={
            'id': id
    }
    data ={
        'id': session['user_id']
    } 
    return render_template("edit_user_profile.html",current_user = user.User.show_one_user(data), one_user = user.User.show_one_user(user_data))

@app.route('/edit/<id>',methods=['POST'])    
def edit(id):
    if not user.User.validate_user_on_update(request.form):
        return redirect('/edit_user')
    pw_hash = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
    # put the pw_hash into the data dictionary
    data = {
        "id": id,
        "first_name": request.form['first_name'],
        "last_name": request.form['last_name'],
        "email_address": request.form['email_address'],
        "address": request.form['address'],
        "state": request.form['state'],
        "password" : pw_hash,
        "confirm_password" : pw_hash,
    }
    user.User.update(data)
    return redirect('/results')

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
        "image_name" : request.files['file'].filename
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


@app.route('/display/<filename>')
def display(filename):
    #return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)

@app.route("/recipes/edit",methods=['POST'])
def edit_one_recipe():
    if not recipe.Recipe.validate_recipe_on_update(request.form):
        return redirect(request.referrer)
    if 'user_id' not in session:
        return redirect('/reset')
    data = {
        "id": request.form['id'],
        "title": request.form['title'],
        "details": request.form['details'],
        "image_name": request.form['image_name'],
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

@app.route('/like/recipe',methods=['POST'])
def like_recipe():
    data = {
        'user_id': request.form['user_id'],
        'recipe_id': request.form['like_recipe']
    }
    user.User.add_favorite(data)
    #return redirect(f"/results/{request.form['user_id']}")
    return redirect("/results")

@app.route('/delete_fav/<int:id>')
def delete_fav_recipe(id):
    if 'user_id' not in session:
        return redirect('/reset')
    data ={
        'recipe_id':id,
        "user_id": session['user_id']
    } 
    userdata ={
        'id': session['user_id']
    }
    user.User.delete_favorite(data)
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    #return render_template("user_fav_recipes.html",current_user= user.User.show_one_user(userdata),files=files)
    return redirect('/results')

@app.route('/my_fav_recipes/<id>')
def show_one(id):
    data={
            "id": id
    }
    print(data)
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("user_fav_recipes.html",current_user= user.User.show_one_user_fav(data),files=files)



if __name__=="__main__":
    app.run(debug=True)






