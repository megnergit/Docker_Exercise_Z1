import unittest
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, inspect
from currency_conversion import get_current_rate, create_mock_table, convert_currency
# ===========================================================


class TestCurrencyConversion(unittest.TestCase):

    def test_get_current_rate(self):
        """
        Testing the function 'get_current_rate'. 

        - Check the reply from the website, if the type of 
          the return value is pandas DataFrame.

        - Check if the datatype is correct. 

        - Check if 'success' column is all True.

        - Check if a table with the name 'exchange_rate' is 
          created in the database.

        """

        TEST_KEY = "36713a14ec549b80bded5bc3c14aab27"
        df = get_current_rate(TEST_KEY)

        self.assertEqual(type(df), type(pd.DataFrame()))
        self.assertEqual(df['rates'].dtype, np.float64)
        self.assertTrue(df['success'].all())

        engine = create_engine(
            "postgresql://postgres:PostgreSQL@localhost:5432")
        insp = inspect(engine)
        self.assertTrue(insp.has_table('exchange_rate'))
    # ---------------------------------------------------------

    def test_create_mock_table(self):
        """
        Testing the function 'create_mock_table'. Check 
        if a table with the name 'train_price' is created in 
        the database. 

        """

        engine = create_engine(
            "postgresql://postgres:PostgreSQL@localhost:5432")
        insp = inspect(engine)

        create_mock_table(engine, 'EUR')
        self.assertTrue(insp.has_table('train_price'))

    # ---------------------------------------------------------
    def test_convert_currency(self):
        """
        Testing the function 'convert_currency'. Get 'target_currency'
        of the last entry of the table, and test if it is same with
        the 'TEST_CURRENCY'.

        """
        TEST_KEY = "36713a14ec549b80bded5bc3c14aab27"
        TEST_CURRENCY = 'RUB'
        df = get_current_rate(TEST_KEY)

        engine = create_engine(
            "postgresql://postgres:PostgreSQL@localhost:5432")

        last_train_currency = convert_currency(engine, TEST_CURRENCY, df)
        self.assertEqual(last_train_currency, TEST_CURRENCY)


# ===========================================================
if __name__ == '__main__':

    unittest.main()
