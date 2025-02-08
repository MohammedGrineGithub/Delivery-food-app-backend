import os
import json
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError
from django.apps import apps
import datetime

def parse_time(time_str):
    try:
        return datetime.datetime.strptime(time_str, "%H:%M:%S").time()
    except ValueError:
        return None

def load_some_data(sender, **kwargs):
    print("******************** LOAD DATA *********************\n\n")
    from tdm.models import Wilaya, Location, CuisingType, Rating, Restaurant, RestaurantMenu, Category, Item, AppImage, DeliveryPerson, Link

    # *********************** 1) Load data from others.json ************************
    """Check if data exists in the database, if not, load from others.json."""
    # Get the path of others.json
    json_path = os.path.join(os.path.dirname(__file__), 'others.json')

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"{json_path} not found.")

    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    print("************** 'others.json' FILE HAS BEEN LOADED ********\n\n")
    try:
        # Load Wilayas
        if not Wilaya.objects.exists() and "wilayas" in data:
            print("Start loading Wilayas ..............\n")
            Wilaya.objects.bulk_create([Wilaya(name=item["name"]) for item in data["wilayas"]])
            print("***************** Wilayas has been loaded with success *****************\n\n")
        else :
            print("--------- Wilaya objects already exists ---------\n\n")

        # Load CuisingType
        if not CuisingType.objects.exists() and "cuisine_type" in data:
            print("Start loading Cuisine Types ..............\n")
            CuisingType.objects.bulk_create([CuisingType(name=item["name"]) for item in data["cuisine_type"]])
            print("***************** CuisineTypes has been loaded with success *****************\n\n")
        else :
            print("--------- CuisineType objects already exists ---------\n\n")

        # Load Delivery Persons
        if not DeliveryPerson.objects.exists() and "Delivery Person" in data:
            print("Start loading DeliveryPersons ..............\n")
            DeliveryPerson.objects.bulk_create([
                DeliveryPerson(full_name=item["fullName"], phone=item["phone"])
                for item in data["Delivery Person"]
            ])
            print("***************** DeliveryPersons has been loaded with success *****************\n\n")
        else :
            print("--------- DeliveryPerson objects already exists ---------\n\n")

        # Loading links
        if not Link.objects.exists() and "Links" in data:
            print("Start loading Links ..............\n")
            links_to_create = []
            for item in data["Links"]:
                restaurant = Restaurant.objects.get(id=item["restaurantId"])
                if restaurant:
                    links_to_create.append(Link(name=item["name"], url=item["url"], restaurant=restaurant))
                    Link.objects.bulk_create(links_to_create)
                    print("***************** Link has been loaded with success *****************\n\n")
        else :
            print("--------- Link objects already exists ---------\n\n")

    except OperationalError:
        print("??????? Exception in loading Wilayas, CuisineTypes, DeliveryPersons ?????????????")

    # *********************** 1) Load data from Restaurants.json ************************
    json_path = os.path.join(os.path.dirname(__file__), 'Restaurants.json')

    if not os.path.exists(json_path):
        raise FileNotFoundError(f"{json_path} not found.")

    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    print("************** 'Restaurants.json' FILE HAS BEEN LOADED ********\n\n")

    try:
        if not Restaurant.objects.exists() and "Restaurant" in data:
            print("Start loading Restaurants ..............\n")

            for r_data in data["Restaurant"]:
                # Create AppImage for logo and banner
                logo = AppImage.objects.create(url=r_data["logo"]["url"])
                banner_logo = AppImage.objects.create(url=r_data["banner_logo"]["url"])

                # Get existing Wilaya
                wilaya = Wilaya.objects.get(id=r_data["location"]["wilayaId"])

                # Create Location
                location = Location.objects.create(
                    address=r_data["location"]["address"],
                    wilaya=wilaya,
                    latitude=r_data["location"]["latitude"],
                    longitude=r_data["location"]["longitude"]
                )

                # Get existing CuisineType
                cuisine_type = CuisingType.objects.get(id=r_data["cuisine_type"])

                # Create Rating
                rating = Rating.objects.create(
                    reviewers_count=r_data["rating"]["reviewers_count"],
                    rating=r_data["rating"]["rating"]
                )

                # Create RestaurantMenu
                menu = RestaurantMenu.objects.create()

                # Create Restaurant
                restaurant = Restaurant.objects.create(
                    restaurant_name=r_data["restaurant_name"],
                    logo=logo,
                    banner_logo=banner_logo,
                    location=location,
                    cuisine_type=cuisine_type,
                    rating=rating,
                    phone=r_data["phone"],
                    email=r_data["email"],
                    delivery_price=r_data["delivery_price"],
                    delivery_duration=r_data["delivery_duration"],
                    menu=menu,
                    opening_time=parse_time(r_data.get("opening_time", "00:00:00")),
                    closing_time=parse_time(r_data.get("closing_time", "23:59:59"))
                )

                # Create Categories and Items
                for category_data in r_data.get("menu", []):
                    category = Category.objects.create(name=category_data["name"], restaurant_menu=menu)

                    for item_data in category_data.get("items", []):
                        # Create AppImage for item photo
                        item_photo = AppImage.objects.create(url=item_data["photo"]["url"])

                        # Create Item
                        Item.objects.create(
                            name=item_data["name"],
                            ingredients=item_data["ingredients"],
                            price=item_data["price"],
                            category=category,
                            photo=item_photo
                        )

            print("***************** Restaurants have been loaded successfully *****************\n\n")
        else:
            print("--------- Restaurant objects already exist ---------\n\n")
             
    except OperationalError:
        print("??????? Exception in loading Restaurants ?????????????")

class TdmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tdm'

    def ready(self):
        post_migrate.connect(load_some_data, sender=self)
