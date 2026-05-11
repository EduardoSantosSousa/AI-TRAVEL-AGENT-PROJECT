from langchain_core.messages import HumanMessage, AIMessage
from src.chains.itinerary_chain import generate_itinerary
from utils.logger import get_logger
from utils.custom_exception import CustomException

logger = get_logger(__name__)

class TravelPlanner:

    def __init__(self):
        self.messages = []
        self.city=""
        self.interests = []
        self.itinerary = ""
        self.days = 1
        self.start_date = ""
        self.budget = "medium"
        self.pace = "moderate"
        self.trip_type = "solo"
        self.start_time = "09:00"
        self.end_time = "20:00"
        self.restrictions = []

        logger.info("Intilaized TravelPlanner instance")

    def set_city(self, city:str ):
        try:
            self.city = city 
            self.messages.append(HumanMessage(content=city))
            logger.info("City set sucessfully")
        except Exception as e:
            logger.error(f"error while setting city: {e}")
            raise CustomException("Failed to set city", e)
        
    def set_interests(self, interests_str:str): 
        try:
            self.interests = [i.strip() for i in interests_str.split(",")]
            self.messages.append(HumanMessage(content=interests_str))
            logger.info("Interest also set sucesfully..")
        except Exception as e:
            logger.error(f"error while setting interests: {e}")
            raise CustomException("Failed to set interest", e)

    async def create_itinerary(self):
        try:
            logger.info(f"Generating itinerary for {self.city} and for interests: {self.interests}")
            itinerary =  await generate_itinerary(
                city=self.city,
                interests=self.interests,
                days=self.days,
                start_date=self.start_date,
                budget=self.budget,
                pace=self.pace,
                trip_type=self.trip_type,
                start_time=self.start_time,
                end_time=self.end_time,
                restrictions=self.restrictions,
            )

            self.itinerary = itinerary
            return itinerary
        
        except Exception as e:
            logger.error(f"error while creating itinerary: {e}")
            raise CustomException("Failed to create itinerary", e)

    def set_preferences(
        self,
        days: int,
        start_date: str,
        budget: str,
        pace: str,
        trip_type: str,
        start_time: str,
        end_time: str,
        restrictions: list[str] | None = None,
    ):
        self.days = days
        self.start_date = start_date
        self.budget = budget
        self.pace = pace
        self.trip_type = trip_type
        self.start_time = start_time
        self.end_time = end_time
        self.restrictions = restrictions or []
    






