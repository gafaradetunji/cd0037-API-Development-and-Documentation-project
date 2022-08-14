from logging import exception
import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sqlalchemy.sql.functions import func

from models import setup_db, Question, Category, db

QUESTIONS_PER_PAGE = 10
def question_paginate(request, selection):
    questions = request.args.get('questions', 1, type=int)
    start = (questions - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_question = questions[start:end]

    return current_question

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PATCH,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    #worked
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        main = {}
        for category in categories:
            main[category.id] = category.type

        return jsonify({
            'categories': main,
            'success': True
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    #worked
    @app.route('/questions')
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        
        current_question = question_paginate(request, questions)

        if current_question == 0:
            abort(404)

        categories = Category.query.all()
        main = {}
        for category in categories:
            main[category.id] = category.type

        return jsonify({
            'success': True,
            'current_question': current_question,
            'total_querstions': len(questions),
            'category': main,
            })
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """    
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        question = Question.query.filter(Question.id==id).one_or_none()
        all_questions = Question.query.all()
        
        if (question is None):
            abort(404)
        else:
            db.session.delete(question)
        return jsonify({
            'success': True,
            'total_question': len(all_questions)
        })
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    #worked
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        if (question is None or answer is None or difficulty is None or category is None):
            abort(422)

        question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
        db.session.add(question)
        db.session.commit()

        return jsonify({
            'success': True,
            'new_question': question.id
        })
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    #worked
    @app.route('/search', methods=['POST'])
    def search_questions():
        body = request.get_json()

        search = body.get('searchTerm', None)

        if search is None:
            abort(404)

        searched_questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%'+search+'%')).all()

        current_question = question_paginate(request, searched_questions)

        return jsonify({
            'success': True,
            'current_question': current_question,
            'total_questions': len(searched_questions),
            'current_category': None
        })
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    #worked
    @app.route('/categories/<int:id>/questions')
    def get_question_categories(id):
        category = Category.query.filter(Category.id == id).one_or_none()
        if category is None:
            abort(404)

        question = Question.query.filter(Question.category == id).all()
        current_question = question_paginate(request, question)


        return jsonify({
            'success': True,
            'question': current_question,
            'category': category.type,
            'total_questions': len(question)
        })
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    #worked
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        body = request.get_json()

        prev_question = body.get('questions', None)
        category = body.get('category', None)

        category_id = category.get('id')

        if prev_question is not None or category is not None:
            change = func.random()
            if category_id == 0:
                question = Question.query.order_by(change).filter(Question.id.notin_(prev_question)).first()

            else:
                question = Question.query.order_by(Question.category == category_id).filter(change).filter(Question.id.notin_(prev_question)).first()

            if question is None:
                return jsonify({'success': True})
            return jsonify({
                'success': True,
                'question': question.format()
            })

        
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(404)
    def page_not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'page not found'
        }),404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad Request'
        }),400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Not Processable'
        }),422

    @app.errorhandler(403)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 403,
            'message': 'Forbidden'
        }),403

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal Server error'
        }),500

    return app

