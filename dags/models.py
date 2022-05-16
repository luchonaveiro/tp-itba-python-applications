"""Dummy data model definition."""

from sqlalchemy import Column, Date, Float, String, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class StockValue(Base):
    """Stock value data model."""

    __tablename__ = "stock_value"

    __table_args__ = (UniqueConstraint("symbol", "date"),)

    symbol = Column(String)
    date = Column(Date)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)

    __mapper_args__ = {"primary_key": [symbol, date]}

    def __init__(self, symbol, date, open_value, high_value, low_value, close_value):
        self.symbol = symbol
        self.date = date
        self.open = open_value
        self.high = high_value
        self.low = low_value
        self.close = close_value

    def __repr__(self):
        return f"""
        <StockValue(symbol='{self.symbol}', 
                    date='{self.date}', 
                    open='{self.open}', 
                    high='{self.high}, 
                    low='{self.low}', 
                    close='{self.close}'
        )>"""
