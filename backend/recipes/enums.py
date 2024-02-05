from enum import Enum


class Limits(Enum):
    MAX_LEN_INGREDIENT_NAME = 200
    MAX_LEN_MEASUREMENT_UNIT_NAME = 10

    MAX_LEN_TAG_NAME = 200
    MAX_LEN_TAG_SLUG = 200

    MAX_LEN_RECIPE_NAME = 200