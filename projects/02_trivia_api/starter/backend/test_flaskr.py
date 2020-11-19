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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question":"What celebrity was often called the King?",
            "answer":"Kingsley Amis",
            "category": 1,
            "difficulty": 3
        }

        self.incomplete_question = {
            "question": "",
            "answer": "definitely",
            "category": 1,
            "difficulty": 5
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    #----------------------------------------------------------------------------#
    # Test every endpoint.
    #----------------------------------------------------------------------------#

    # GET "/categories"
    def test_success_get_categories(self):
        pass

    def test_405_put_method(self):
        pass

    # GET "/questions"
    def test_success_get_questions_page(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'] > 0)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])

    def test_404_beyond_range(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # DELETE "/questions/{question_id}"
    def test_success_delete_question(self):
        res = self.client().delete('/questions/5')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 5).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(question, None)

    def test_422_question_id_nonexistent(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # POST "/questions"
    def test_success_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        question = Question.query.filter(Question.answer == "Kingsley Amis").one_or_none()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertFalse(question == None)

    def test_422_empty_answer(self):
        res = self.client().post('/questions', json=self.incomplete_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # POST "/questions/search"
    def test_success_search_for_title(self):
        res = self.client().post('/questions/search', json={"searchTerm":"title"})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data["total_questions"] >= 1)

    def test_422_empty_search_term(self):
        res = self.client().post('/questions/search', json={"searchTerm":""})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    # GET "/categories/{category_id}/questions"
    def test_success_questions_by_category(self):
        res = self.client().get('/categories/3/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']) > 0)
        self.assertEqual(data['current_category'], 3)

    def test_404_category_not_found(self):
        res = self.client().get('/categories/3000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    # POST "/quizzes"
    def test_success_first_question_all(self):
        payload = {"previous_questions":[5, 9, 12],"quiz_category":{"id":4,"type":"History"}}
        res = self.client().post('/quizzes', json=payload)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_422_no_category_supplied(self):
        payload = {"previous_questions":[5, 9, 12]}
        res = self.client().post('/quizzes', json=payload)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()