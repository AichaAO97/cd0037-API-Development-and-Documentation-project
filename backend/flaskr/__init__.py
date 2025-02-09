import os
from sre_constants import SUCCESS
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}}) 
    
    
    
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response
    
    
    

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=['GET'])
    def retrieve_categories():
        try: 
            selection = Category.query.order_by(Category.id).all()
                    
            categories = {}
            for category in selection:
                categories[category.id] = category.type
                
            if len(categories) == 0:
                abort(404)
            
            return jsonify({
                    "categories" : categories,
                })
        except:
            abort(400)
        
        
        
        
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

    @app.route("/questions", methods=['GET'])
    def retrieve_questions():
        try: 
            ## Get Questions 
            selection_Q = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection_Q)
            total_questions = len(current_questions)
            
            if total_questions == 0:
                abort(404)
            ## Get Categories
            selection_C = Category.query.order_by(Category.id).all()         
            categories = {}
            for category in selection_C:
                categories[category.id] = category.type
            
            return jsonify(
                {
                    "questions": current_questions,
                    "total_questions": total_questions,
                    "categories": categories,
                    "current_category": None
                }
            )
        except:
            abort(404)



    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()    
            question.delete()
            
            return jsonify({
                    "success" : True,
                })
        except:
            abort(422)
    
    

    """
    @TODO :
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route("/questions", methods=['POST'])
    def create_or_search_question():
        body = request.get_json()
        question = body.get("question", None)
        answer = body.get("answer", None)
        category = body.get("category", None)
        difficulty = body.get("difficulty", None) 
        search_term = body.get("searchTerm", None)
        try:
            # if the user provided a search term, retrieve relevent questions
            if search_term:
                try:
                    selection = Question.query.filter(Question.question.ilike("%{}%".format(search_term))).all()
                    questions = paginate_questions(request, selection)
                    print(questions)
                    return jsonify({
                        "questions" : questions,
                        "total_questions": len(questions),
                        "current_category": None,
                    })
                    
                except:
                    abort(404)

            # Else:  create a new question  
            else:      
                question = Question(question=question, answer=answer, category=category, difficulty=difficulty)  
                question.insert()
                return jsonify({
                        "success" : True,
                    })    
        except:
            abort(405)    
        
        



    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    
    @app.route("/categories/<int:category_id>/questions", methods=['GET'])
    def get_questions_by_category(category_id):
        try:

            selection = Question.query.order_by(Question.id).filter(Question.category == category_id ).all()
            questions = paginate_questions(request, selection)
            return jsonify({
                "questions": questions,
                "total_questions": len(questions),
                "current_category": category_id,
            })
        except:
            abort(404)
        

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
    
    @app.route("/quizzes", methods=['POST'])
    def get_quiz_questions():
        body = request.get_json()
        previous_questions = body.get("previous_questions", None)
        quiz_category = body.get("quiz_category", None)

        try:
            if quiz_category['id'] == 0:
                selection = Question.query.filter(~Question.id.in_(previous_questions)).all()
                
            else: 
                selection = Question.query.filter(~Question.id.in_(previous_questions), Question.category == quiz_category["id"]).all()
            
            questions = [question.format() for question in selection]
            random_question = random.choice(questions)
            
            return jsonify({
                "question": random_question,
            })
            
        except:
            abort(422)



    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"error": 404, "message": "resource not found"}),
            404,
        )
        
    @app.errorhandler(405)
    def not_allowed(error):
        return (
            jsonify({"error": 405, "message": "method not allowed"}),
            405,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"error": 422, "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return (
            jsonify({"error": 400, "message": "bad request"}),
            400,
        )
        
    
    @app.errorhandler(500)
    def bad_request(error):
        return (
            jsonify({"error": 500, "message": "Internal Server Error"}),
            500,
        )


    return app

