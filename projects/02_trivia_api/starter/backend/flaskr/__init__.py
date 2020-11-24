import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


#----------------------------------------------------------------------------#
# Random Utility Functions.
#----------------------------------------------------------------------------#

def get_category_map():
  all_categories = Category.query.all()
  categories = {}
  for category in all_categories:
    categories[category.id] = category.type
  return categories

#----------------------------------------------------------------------------#
# Main App.
#----------------------------------------------------------------------------#

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  CORS(app, resources={r"/": {"origins": "*"}})

  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  @app.route('/categories')
  def get_categories():
    try:
      category_map = get_category_map()
    except:
      abort(500)
    return jsonify({"success": True, "categories": category_map})

  @app.route('/questions')
  def get_questions():
    try:
      page = request.args.get('page', 1, type=int)
      all_questions = Question.query.order_by(Question.id.asc()).all()
      question_slice = all_questions[(page-1)*QUESTIONS_PER_PAGE:page*QUESTIONS_PER_PAGE]
      questions = [question.format() for question in question_slice]
      assert len(questions) > 0
    except:
      abort(404)
    return jsonify({"questions": questions, "total_questions": len(all_questions), "categories": get_category_map(), "current_category": None})

  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.get(question_id)
      question.delete()
    except:
      abort(422)
    return jsonify({'success': True})

  @app.route('/questions', methods=['POST'])
  def post_question():
    try:
      data = request.get_json()
      assert len(data["question"]) > 0
      assert len(data["answer"]) > 0
    except:
      abort(422)
    try:
      new_question = Question(
        question=data["question"],
        answer=data["answer"],
        category=data["category"],
        difficulty=data["difficulty"])
      new_question.insert()
    except:
      abort(500) 
    return  jsonify({'success': True})

  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    try:
      data = request.get_json()
      searchTerm = data.get("searchTerm", "")
      assert searchTerm != ""
    except:
      abort(422)
    try:
      all_questions = Question.query.all()
      questions = []
      for question in all_questions:
        if searchTerm.upper() in question.question.upper():
          questions.append(question.format())
    except:
      abort(422)
    return jsonify({"questions": questions, "total_questions": len(questions), "current_category": None})

  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def questions_by_category(category_id):
    try:
      category_match = Category.query.filter(Category.id == category_id).all()
      assert len(category_match) != 0
    except:
      abort(404)
    try:
      questions_in_category = Question.query.filter(Question.category == str(category_id)).all()
      questions_formatted = [question.format() for question in questions_in_category]
    except:
      abort(422)
    return jsonify({"questions": questions_formatted, "total_questions": len(questions_formatted), "current_category": category_id})

  @app.route('/quizzes', methods=['POST'])
  def quiz_question():
    try:
      # collect remaining candidate questions in question_fresh
      data = request.get_json()
      past_questions = [str(q) for q in data["previous_questions"]]
      if data["quiz_category"]["id"] == 0:
        questions_all = Question.query.all()
      else:
        questions_all = Question.query.filter(Question.category == str(data["quiz_category"]["id"]))
      questions_fresh = [question.format() for question in questions_all if str(question.id) not in past_questions]
    except:
      abort(422)
    try:
      if len(questions_fresh) == 0:
        next_question = None
      else:
        next_question = random.choice(questions_fresh)
    except:
      abort(422)
    return jsonify({"previousQuestions": data["previous_questions"], "question": next_question})
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
  
  @app.errorhandler(500)
  def internal_server_error(error):
    return jsonify({
      "success": False, 
      "error": 500,
      "message": "server error"
      }), 500

  return app

    