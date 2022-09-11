import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category
from settings import DB_NAME_TEST, DB_USER, DB_PASSWORD


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = DB_NAME_TEST
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            DB_USER, DB_PASSWORD, "localhost:5432", self.database_name
            )
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
            
        self.new_question = { "answer": "Scarab", "category": 4, "difficulty": 4, "id": 25, "question": "Which dung beetle was worshipped by the ancient Egyptians?" }

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    
    
#################### GET CATEGORIES
    def test_get_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])


    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/categories/1")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data["message"], "bad request")



##################### GET QUESTIONS
    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["categories"])
        self.assertEqual(data["current_category"], None)

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=500000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["message"], "resource not found")



##################### DELETE A QUESTION
    def test_delete_question(self):
        res = self.client().delete('/questions/13')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 13).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_422_if_question_does_not_exist(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["message"], "unprocessable")
    
    
        
##################### CREATE A QUESTION
    def test_create_new_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)


    def test_405_if_question_creation_not_allowed(self):
        res = self.client().post("/questions/45", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["message"], "method not allowed")



##################### SEARCH FOR A QUESTION
    def test_get_question_search_with_results(self):
        res = self.client().post("/questions", json={"searchTerm": "did"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertTrue(data["total_questions"])
        self.assertEqual(data["current_category"], None)

    def test_get_question_search_without_results(self):
        res = self.client().post("/questions", json={"searchTerm": "appleapple"})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["total_questions"], 0)



##################### SEARCH FOR QUESTIONS BY CATEGORY
    def test_get_questions_by_category(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])
        self.assertEqual(data["total_questions"], 3)
        self.assertEqual(data["current_category"], 1)

    def test_no_questions_for_this_category(self):
        res = self.client().get("/categories/10/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data["message"], "resource not found")



##################### QUIZZES
    def test_get_questions_to_play(self):
        res = self.client().post("/quizzes", json={"quiz_category": {'id': 1, 'type': 'science'}, "previous_questions": [] })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])


    def test_no_questions_for_this_category(self):
        res = self.client().post("/quizzes", json={"quiz_category": {'id': 10, 'type': 'science'}, "previous_questions": [] })
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["message"], "unprocessable")








# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()