from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, Float, String
import sys
import pdb
import pandas as pd
import requests
# ===========================================================

# ACCESS_KEY = '36713a14ec549b80bded5bc3c14aab27'
# TARGET_CURRENCY = 'EUR'

args = sys.argv
TARGET_CURRENCY = args[1]
ACCESS_KEY = args[2]

# ===========================================================
# update current exchange rate


def get_current_rate(ACCESS_KEY: str) -> pd.DataFrame:
    """Get current currency exchange rate from the website api.exchangeratesapi.io

    Parameters
    ----------
    ACCESS_KEY : str
        An access key that is needed when you extractn the data from 
        the web site. It has to be obtained before you run this application, 
        manually from the website. The access key will be given as one 
        of the arguments for 'docker exec' command. Current version uses
        3 currencies only, USD, EUR, and RUB.

    Returns
    -------
    df : pd.DataFrame 
        a table of currency exchange rates in pandas DataFrame form. 

    """
    BASE_URL = "http://api.exchangeratesapi.io/v1/"
    MESSAGE = 'latest&base=EUR&symbols=USD,EUR,RUB?'

    target = BASE_URL + MESSAGE+'access_key='+ACCESS_KEY
    reply_in_json = requests.get(target)

    df = pd.io.json.read_json(reply_in_json.text)
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'currency'}, inplace=True, errors='ignore')

    return df


# ===========================================================
# data model for mock table
Base = declarative_base()


class Train(Base):
    """A class for an each individual train in the mock-up table. 

    Attributes
    ----------
        id : integer
            serial number for an entry. 

        type : str
            type of a train, e.g., guterzug, nightliner, ice.

        price : float
            price of the train in the currency given in 'currency'.

        currency : str
            three-digit code of currency. [USD|EUR|RUB]

        price_in_target_currency : float
            price of the train in the desired currency given in 'target_currency'.

        target_currency : str
            three-digit code of currency into which the prices are converted. 
            [USD|EUR|RUB].

    """
    __tablename__ = 'train_price'
    id = Column(Integer, primary_key=True)
    type = Column(String(256))
    price = Column(Float)
    currency = Column(String(3))
    price_in_target_currency = Column(Float)
    target_currency = Column(String(3))

    def __repr__(self):
        return f"Train(id={self.id!r}, type={self.type!r}, price={self.price!r}, \
            currency={self.currency!r}, \
            price_in_target_currency={self.price_in_target_currency!r}, \
            target_currency={self.target_currency!r})"

# ===========================================================
# create mock table in postgres DB


def create_mock_table(engine, TARGET_CURENCY: str) -> None:
    """Create a mock-up table that shows prices of trains in various currency.
    The function create a table in postgres database, and exit. No returning 
    parameters

    Parameters
    ----------
        engine : SQL database engine. 

        TARGET_CURRENCY : str
            The name of the currency into which the existing price is to be 
            converted. Here it is used just as a place holder.

    Returns
    -------
        None.

    """

    Base.metadata.drop_all(engine, checkfirst=True)
    Base.metadata.create_all(engine)

    train1 = Train(type='gueterzug', price=4000, currency='RUB',
                   price_in_target_currency=0, target_currency=TARGET_CURRENCY)
    train2 = Train(type='nightliner', price=140, currency='USD',
                   price_in_target_currency=0, target_currency=TARGET_CURRENCY)
    train3 = Train(type='ice', price=300, currency='EUR',
                   price_in_target_currency=0, target_currency=TARGET_CURRENCY)

    train_list = [train1, train2, train3]

    with Session(engine) as session:
        session.begin()
        try:
            session.add_all(train_list)
        except:
            session.rollback()
            raise
        else:
            session.commit()

# ===========================================================
# convert currency


def convert_currency(engine, TARGET_CURRENCY: str, df: pd.DataFrame) -> None:
    """Convert the prices in the price list in the mock-up table 
       to TARGET_CURRENCY.

    Parameters
    ----------
        engine : SQL database engine. 

        TARGET_CURRENCY : str
            The name of the currency into which the existing price is to be 
            converted. One can choose from [UDS|EUR|RUB].

    Returns
    -------
        None.

    """

    with Session(engine) as session:
        try:
            trains = session.query(Train).all()
            print(
                f'\033[36m#=================================================================\033[0m')
            print(f'# id type price currency new_price new_currency')
            for train in trains:
                base_rate = df[df['currency'] ==
                               train.currency]['rates'].values[0]
                target_rate = df[df['currency'] ==
                                 TARGET_CURRENCY]['rates'].values[0]
                converted_price = train.price * target_rate / base_rate
                train.price_in_target_currency = converted_price
                train.target_currency = TARGET_CURRENCY
                print(f'{train.id:3} {train.type:12} {train.price:8.2f} {train.currency:5} \
                    {train.price_in_target_currency:8.2f} {train.target_currency:5}')

        except:
            session.rollback()
            raise()
        else:
            session.commit()


# ===========================================================
if __name__ == '__main__':
    df = get_current_rate(ACCESS_KEY)
    print(
        f'\033[33m#=================================================================\033[0m')
    print(df)
    engine = create_engine("postgresql://postgres:PostgreSQL@localhost:5432")
    create_mock_table(engine, TARGET_CURRENCY)
    convert_currency(engine, TARGET_CURRENCY, df)
