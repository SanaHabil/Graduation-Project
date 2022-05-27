from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re
from flask_app.models import recipe
from flask_bcrypt import Bcrypt


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=(.*[\d]){1,}).{8,}$') 

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email_address = data['email_address']
        self.address = data['address']
        self.state = data['state']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.recipes = []



    @staticmethod
    def validate_user(data):
        query = "SELECT * FROM users WHERE email_address=%(email_address)s;"
        result = connectToMySQL('foodsy_schema').query_db(query,data)
        is_valid = True
        if len(result) >= 1:
            flash("Email Address is in use!","register")
            is_valid = False
        if not EMAIL_REGEX.match(data['email_address']): 
            flash("Invalid email address!","register")
            is_valid = False 
        if  len(data['first_name']) < 3:
            flash(" Name must be at least 2 characters.","register")
            is_valid = False
        if  len(data['last_name']) < 3:
            flash("Last Name must be at least 2 characters.","register")
            is_valid = False
        if  len(data['address']) < 3:
            flash("Address must be at least 2 characters.","register")
            is_valid = False
        if  len(data['state']) == 2:
            flash("Please choose a State","register")
            is_valid = False
        if  not PASSWORD_REGEX.match(data['password']):
            flash("PLease Choose a Password at least 8 characters, one Uppercase, and One number.", "register")
            is_valid = False
        if  data['password'] != data['confirm_password']:
            flash("Passwords don't match, try again!", "register")
            is_valid = False        
        return is_valid

    @staticmethod
    def validate_user_on_update(data):
        query = "SELECT * FROM users WHERE email_address=%(email_address)s;"
        result = connectToMySQL('foodsy_schema').query_db(query,data)
        is_valid = True

        if  len(data['first_name']) < 3:
            flash(" Name must be at least 2 characters.","update")
            is_valid = False
        if  len(data['last_name']) < 3:
            flash("Last Name must be at least 2 characters.","update")
            is_valid = False
        if  len(data['address']) < 3:
            flash("Address must be at least 2 characters.","update")
            is_valid = False
        if  len(data['state']) == 2:
            flash("Please choose a State","update")
            is_valid = False    
        if  not PASSWORD_REGEX.match(data['password']):
            flash("PLease Choose a Password at least 8 characters, one Uppercase, and One number.", "update")
            is_valid = False
        if data['password'] == '':
            flash("Passwords can't be empty, try again!", "update")
            is_valid = False          
        if len(data['password'])  < 1 :
            flash("PLease Choose a Password at least 8 characters, one Uppercase, and One number.", "update")
        if  data['password'] != data['confirm_password']:
            flash("Passwords don't match, try again!", "update")
            is_valid = False        
        return is_valid

    @classmethod
    def add_user(cls, data):
        query = "INSERT INTO users (first_name, last_name, email_address, address,state, password, created_at, updated_at) VALUES (%(first_name)s,%(last_name)s,%(email_address)s,%(address)s,%(state)s,%(password)s,NOW(),NOW());"
        result = connectToMySQL('foodsy_schema').query_db(query,data)
        return result

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL('foodsy_schema').query_db(query)
        emails = []
        for email in results:
            emails.append(cls(email) )
        return emails

    @classmethod
    def show_one_user(cls,data):
        query = "SELECT * FROM users WHERE id= %(id)s;"
        results = connectToMySQL('foodsy_schema').query_db(query,data)
        print(results)
        this_user = cls(results[0])
        return this_user

        
    @classmethod
    def get_by_email(cls,data):
        query = "SELECT * FROM users WHERE email_address = %(email_address)s;"
        result = connectToMySQL('foodsy_schema').query_db(query,data)
        # Didn't find a matching user
        if len(result) < 1:
            return False
        return cls(result[0])

    @classmethod
    def update(cls,data):
            query = "UPDATE users SET first_name=%(first_name)s,last_name=%(last_name)s, email_address = %(email_address)s,address = %(address)s, state = %(state)s, password = %(password)s,updated_at=NOW() WHERE id = %(id)s;"
            return connectToMySQL('foodsy_schema').query_db(query,data)


    @classmethod
    def add_favorite(cls,data):
        query = "INSERT INTO favorites (user_id,recipe_id) VALUES (%(user_id)s,%(recipe_id)s);"
        return connectToMySQL('foodsy_schema').query_db(query,data)



    @classmethod    
    def show_one_user_fav(cls, data):
            query ="SELECT * FROM users LEFT JOIN favorites ON users.id = favorites.user_id LEFT JOIN recipes ON recipes.id = favorites.recipe_id WHERE users.id = %(id)s;"
            results = connectToMySQL('foodsy_schema').query_db(query,data)
            user = cls(results[0])
            for row_from_db in results:
                if row_from_db['recipes.id'] == None:
                    break
                userdata = {
                        "id" : row_from_db['recipes.id'],
                        "title" : row_from_db['title'],
                        "details" : row_from_db['details'],
                        "image_name": row_from_db['image_name'],
                        "user_id" : row_from_db['user_id'],
                        "created_at" : row_from_db['created_at'],
                        "updated_at" : row_from_db['updated_at'],
                }
                user.recipes.append(recipe.Recipe(userdata))
            return user

    @classmethod
    def delete_favorite(cls,data):
        query = "DELETE from favorites WHERE recipe_id = %(recipe_id)s AND user_id= %(user_id)s"
        print(data)
        return connectToMySQL('foodsy_schema').query_db(query,data)