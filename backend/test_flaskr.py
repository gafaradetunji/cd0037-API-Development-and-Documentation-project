import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = database_path = 'postgresql://postgres:miami@localhost:5432/trivia'
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

#2
    def test_get_paginated_question(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['current_questions'])
        self.assertTrue(len(data['total_questions']))
        self.assertTrue(data['category'])

#3
    def test_delete_question_by_id(self):
        res = self.client().delete('/questions/1')
        data = json.loads(res.data)

        options = Question.query.filter(Question.id == 1).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted', 1])
        self.assertTrue(len(data['questions']))
        self.assertEqual(options, None)

    def test_404_question_does_not_exist(self):
        res = self.client().delete('/questions/10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message', 'Cannot Process your request'])

#4
    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))

    def test_405_if_creation_is_not_allowed(self):
        res = self.client().post('/questions/40', json=self.question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Method not allowed')

#5
    def test_search_term(self):
        res = self.client().post('/search', json={'searchTerm': 'neil'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_question'])
        self.assertTrue(len(data['questions']))

    def test_search_term_not_found(self):
        res = self.client().post('/question', json={'searchTerm': ' nvbscmsks'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message', 'page not found'])

#6
    def test_get_question_categories(self):
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertTrue(data['total_question'])
        self.assertTrue(data['category'])

    def test_404_get_question_categories(self):
        res = self.client().get('/questions/10000/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'page not found')

#7
    def test_get_quiz_questions(self):
        res = self.client().post('/quizzes', json={'questions':[10,6,7],'category':{'id':0,'type':'All'}})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'])

    def test_404_get_question_categories_if_not_found(self):
        res = self.client().post('/quizzes/10000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'page not found')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()