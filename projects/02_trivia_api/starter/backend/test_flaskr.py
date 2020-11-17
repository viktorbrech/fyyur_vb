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

    def test_405_post_method(self):
        pass

    # GET "/questions"
    def test_success_get_questions_page(self):
        pass

    def test_404_beyond_range(self):
        pass

    # DELETE "/questions/{question_id}"
    def test_success_delete_question(self):
        pass

    def test_422_question_id_nonexistent(self):
        pass

    # POST "/questions"
    def test_success_create_question(self):
        pass

    def test_422_empty_answer(self):
        pass

    # POST "/questions/search"
    def test_success_search_for_title(self):
        pass

    def test_422_empty_search_term(self):
        pass

    # GET "/categories/{category_id}/questions"
    def test_success_(self):
        pass

    def test_404_category_not_found(self):
        pass

    # POST "/quizzes"
    def test_success_first_question_all(self):
        pass

    def test_404_no_question_left(self):
        pass



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()