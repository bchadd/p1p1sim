from sqlalchemy import create_engine, MetaData, Engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, relationship, mapped_column
import pandas as pd
import json
from datetime import datetime
import random

class Base(DeclarativeBase):
    pass

class List(Base):
    __tablename__ = 'list'

    list_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)

    card_info_entries: Mapped['Info'] = relationship(back_populates='underlying_list',cascade='all, delete-orphan')

class Info(Base):
    __tablename__ = 'info'

    id: Mapped[str] = mapped_column(primary_key=True)
    list_id: Mapped[int] = mapped_column(ForeignKey('list.list_id'))
    name: Mapped[str] = mapped_column(nullable=False)
    png: Mapped[str] = mapped_column(nullable=False)

    underlying_list: Mapped['List'] = relationship(foreign_keys=[list_id],back_populates='card_info_entries')

class Picks(Base):
    __tablename__ = 'picks'

    pick_id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)
    timestamp: Mapped[str] = mapped_column(nullable=False)
    pick: Mapped[str] = mapped_column(nullable=False)
    card2: Mapped[str] = mapped_column(nullable=False)
    card3: Mapped[str] = mapped_column(nullable=False)
    card4: Mapped[str] = mapped_column(nullable=False)
    card5: Mapped[str] = mapped_column(nullable=False)
    card6: Mapped[str] = mapped_column(nullable=False)
    card7: Mapped[str] = mapped_column(nullable=False)
    card8: Mapped[str] = mapped_column(nullable=False)
    card9: Mapped[str] = mapped_column(nullable=False)
    card10: Mapped[str] = mapped_column(nullable=False)
    card11: Mapped[str] = mapped_column(nullable=False)
    card12: Mapped[str] = mapped_column(nullable=False)
    card13: Mapped[str] = mapped_column(nullable=False)
    card14: Mapped[str] = mapped_column(nullable=False)
    card15: Mapped[str] = mapped_column(nullable=False)

## set table schema

def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)

## create intermediary data structures

def create_list_df_from_(cube_name: str) -> pd.DataFrame:
    with open(f'cubes\{cube_name}.csv','r') as cc_csv:
        cc_df = pd.read_csv(cc_csv)
        return cc_df[['name','MTGO ID']].copy()
    
def to_list_from_(list_df: pd.DataFrame) -> list:
    return list_df['name'].tolist()

def generate_pack_from_(cube_list: list) -> list:
    return random.sample(cube_list,k=15)

def json_df_from_(json: json) -> pd.DataFrame:
    return pd.read_json(json)

def create_picks_object(picked_pack: list) -> Picks:
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
    return Picks(timestamp=timestamp,
                 pick=picked_pack[0],
                 card2=picked_pack[1],
                 card3=picked_pack[2],
                 card4=picked_pack[3],
                 card5=picked_pack[4],
                 card6=picked_pack[5],
                 card7=picked_pack[6],
                 card8=picked_pack[7],
                 card9=picked_pack[8],
                 card10=picked_pack[9],
                 card11=picked_pack[10],
                 card12=picked_pack[11],
                 card13=picked_pack[12],
                 card14=picked_pack[13],
                 card15=picked_pack[14])

## insert structures to tables

def add_list_to_(engine: Engine, list_df: pd.DataFrame) -> None:
    with Session(engine) as session, session.begin():
        list_df.to_sql(name='list',con=engine,if_exists='replace',index=False)

def add_info_to_(engine: Engine, json_df: pd.DataFrame) -> None:
    with Session(engine) as session, session.begin():
        json_df.to_sql(name='info',con=engine,if_exists='replace')

def add_pick_to_(engine: Engine, p1p1_obj: Picks) -> None:
    with Session(engine) as session, session.begin():
        session.add(p1p1_obj)