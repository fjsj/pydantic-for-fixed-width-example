import textwrap
from typing import ClassVar, List

from pydantic import BaseModel
from pydantic.types import conint, constr

# Example to generate a fixed width file from a JSON.
# The JSON input will have this format:
input_dict = {
    "pizzas": [
        {
            "quantity": 1,
            "name": "Mozzarella",
            "ingredients": ["Tomato sauce", "Mozzarella cheese"],
        },
        {
            "quantity": 20,
            "name": "Brazilian Calabresa",
            "ingredients": ["Tomato sauce", "Calabresa sausage", "Onion"],
        },
    ]
}
# and the fixed width output will have this format (fill char is `-`):
expected_output_txt = textwrap.dedent(
    """
    PIZZAS ORDER
    QUANTITY: 001
    NAME: Mozzarella--------------------
    INGREDIENTS: Tomato sauce------------------ Mozzarella cheese-------------
    QUANTITY: 020
    NAME: Brazilian Calabresa-----------
    INGREDIENTS: Tomato sauce------------------ Calabresa sausage------------- Onion-------------------------
    END OF PIZZAS ORDER
    """
).strip("\n")


STR_FILL_VALUE = "-"
INT_FILL_VALUE = "0"


class FixedWidthStr(BaseModel):
    _max_str_length: ClassVar[int] = 30

    __root__: constr(max_length=_max_str_length)

    def as_fixed_width(self):
        return self.__root__.ljust(self._max_str_length, STR_FILL_VALUE)


class FixedWidthPositiveInt(BaseModel):
    _max_str_length: ClassVar[int] = 3

    __root__: conint(gt=0, le=999)

    def as_fixed_width(self):
        return str(self.__root__).rjust(self._max_str_length, INT_FILL_VALUE)


class IngredientModel(BaseModel):
    __root__: FixedWidthStr

    def as_fixed_width(self):
        return self.__root__.as_fixed_width()


class PizzaModel(BaseModel):
    quantity: FixedWidthPositiveInt
    name: FixedWidthStr
    ingredients: List[IngredientModel]

    def as_fixed_width(self):
        quantity_fw = self.quantity.as_fixed_width()
        name_fw = self.name.as_fixed_width()
        ingredients_fw = " ".join(ing.as_fixed_width() for ing in self.ingredients)

        return (
            textwrap.dedent(
                """
                QUANTITY: {quantity_fw}
                NAME: {name_fw}
                INGREDIENTS: {ingredients_fw}
                """
            )
            .format(
                quantity_fw=quantity_fw,
                name_fw=name_fw,
                ingredients_fw=ingredients_fw,
            )
            .strip("\n")
        )


class OrderModel(BaseModel):
    pizzas: List[PizzaModel]

    def as_fixed_width(self):
        pizzas_fw = "\n".join(p.as_fixed_width() for p in self.pizzas)
        return (
            textwrap.dedent(
                """
                PIZZAS ORDER
                {pizzas_fw}
                END OF PIZZAS ORDER
                """
            )
            .format(pizzas_fw=pizzas_fw)
            .strip("\n")
        )


if __name__ == "__main__":
    found_output_txt = OrderModel.parse_obj(input_dict).as_fixed_width()
    print(found_output_txt)
    assert expected_output_txt == found_output_txt