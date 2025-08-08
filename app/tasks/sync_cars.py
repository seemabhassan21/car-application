import os
import json
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models import Car, Make, CarModel
from app.tasks.celery_worker import celery
from dotenv import load_dotenv
load_dotenv() 

CAR_API_URL = os.getenv("CAR_API_URL")
CAR_API_HEADERS = json.loads(os.getenv("CAR_API_HEADERS", "{}"))
DATABASE_URL = os.environ.get("SQLALCHEMY_DATABASE_URI")

engine = create_engine(DATABASE_URL)
Session = scoped_session(sessionmaker(bind=engine))

@celery.task(name="app.tasks.sync_cars.sync_cars")
def sync_cars():
    session = Session()
    total_saved = 0

    for year in range(2012, 2023):
        try:
            query = json.dumps({"Year": year})
            response = requests.get(CAR_API_URL, headers=CAR_API_HEADERS, params={"where": query})

            if response.status_code != 200:
                print(f"Failed to fetch data for year {year}: {response.status_code}")
                continue

            cars = response.json().get('results', [])

            for c in cars:
                make = session.query(Make).filter_by(name=c['Make']).first()
                if not make:
                    make = Make(name=c['Make'])
                    session.add(make)
                    session.flush()  

                car_model = session.query(CarModel).filter_by(
                    name=c['Model'],
                    year=c['Year'],
                    make_id=make.id
                ).first()
                if not car_model:
                    car_model = CarModel(
                        name=c['Model'],
                        year=c['Year'],
                        make_id=make.id
                    )
                    session.add(car_model)
                    session.flush()

                if not session.query(Car).filter_by(car_model_id=car_model.id).first():
                    car = Car(car_model_id=car_model.id)
                    session.add(car)
                    total_saved += 1

        except Exception as e:
            print(f"Error syncing year {year}: {str(e)}")
            session.rollback()

    try:
        if total_saved > 0:
            session.commit()
        print(f"Sync complete: {total_saved} new cars added.")
    except Exception as e:
        print(f"Failed to commit changes: {str(e)}")
        session.rollback()
    finally:
        session.close()
