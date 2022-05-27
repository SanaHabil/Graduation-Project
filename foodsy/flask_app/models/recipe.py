from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re
from flask_bcrypt import Bcrypt
from flask_app.models import user


EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
PASSWORD_REGEX = re.compile(r'^(?=.*?[A-Z])(?=(.*[\d]){1,}).{8,}$') 

class Recipe:
    def __init__( self , data ):
        self.id = data['id']
        self.title = data['title']
        self.details = data['details']
        self.user_id = data['user_id']
        self.image_name = data['image_name']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.users_who_favoraited=[]

    @staticmethod
    def validate_recipe_on_submit(data):
        is_valid = True
        if  len(data['title']) < 3:
            flash(" Title must be at least 3 characters.","create")
            is_valid = False
        if  len(data['details']) < 3:
            flash("Details must be at least 3 characters.","create")
            is_valid = False
        return is_valid

    @staticmethod
    def validate_recipe_on_update(data):
        is_valid = True
        if  len(data['title']) < 3:
            flash(" Title must be at least 3 characters.","update")
            is_valid = False
        if  len(data['details']) < 3:
            flash("Details must be at least 3 characters.","update")
            is_valid = False
        return is_valid

    @classmethod
    def add_recipe(cls, data):
        query = "INSERT INTO recipes (title, details, user_id,image_name, created_at, updated_at) VALUES (%(title)s,%(details)s,%(user_id)s,%(image_name)s,NOW(),NOW());"
        result = connectToMySQL('foodsy_schema').query_db(query,data)
        return result

    @classmethod
    def get_all_recipes(cls):
        query = "SELECT * FROM recipes;"
        results = connectToMySQL('foodsy_schema').query_db(query)
        all_recipes = []
        for recipe in results:
            all_recipes.append(cls(recipe))
        return all_recipes

    @classmethod
    def show_one_recipe(cls,data):
        query ="SELECT * FROM recipes WHERE id = %(id)s;"
        results = connectToMySQL('foodsy_schema').query_db(query,data)
        this_recipe = cls(results[0])
        return this_recipe

    @classmethod
    def update_one_recipe(cls,data):
            query = "UPDATE recipes SET title=%(title)s, details=%(details)s, image_name=%(image_name)s, updated_at=NOW() WHERE id = %(id)s;"
            return connectToMySQL('foodsy_schema').query_db(query,data)

    @classmethod
    def delete(cls, id):
        query  = f"DELETE FROM recipes WHERE id = {id};"
        return connectToMySQL('foodsy_schema').query_db(query)         

    @classmethod
    def unfavorited_recipe(cls,data):
        query = "SELECT * FROM recipes WHERE recipes.id NOT IN ( SELECT recipe_id FROM favorites WHERE user_id = %(id)s );"
        results = connectToMySQL('foodsy_schema').query_db(query,data)
        recipes = []
        for row in results:
            recipes.append(cls(row))
        print(recipes)
        return recipes   

    
    