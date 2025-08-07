from enum import Enum, IntEnum
from typing import List, Optional
from copy import deepcopy

class Floor(IntEnum):
    First = 0
    Second = 1
    Third = 2
    Fourth = 3
    Fifth = 4


class Color(Enum):
    Empty = ''
    Red = 'Red'
    Green = 'Green'
    Blue = 'Blue'
    Yellow = 'Yellow'
    Orange = 'Orange'


class Animal(Enum):
    Empty = ''
    Frog = 'Frog'
    Rabbit = 'Rabbit'
    Grasshopper = 'Grasshopper'
    Bird = 'Bird'
    Chicken = 'Chicken'

def floor_above(floor: Floor) -> Optional[Floor]:
    """
    Returns the floor directly above the given one, or None if at the top.
    """
    if floor.value < Floor.Fifth.value:
        return Floor(floor.value + 1)
    return None

class AttributeType(Enum):
    Floor = 'Floor'
    Color = 'Color'
    Animal = 'Animal'


class Hint(object):
    """Base class for all the hint classes"""
    pass


class AbsoluteHint(Hint):
    """
    Represents a hint on a specific floor. Examples:
    The third floor is red:
        AbsoluteHint(Floor.Third, Color.Red)
    The frog lives on the fifth floor:
        AbsoluteHint(Animal.Frog, Floor.Fifth)
    The orange floor is the floor where the chicken lives:
        AbsoluteHint(Color.Orange, Animal.Chicken)
    """
    def __init__(self, attr1, attr2):
        self._attr1 = attr1
        self._attr2 = attr2
        
    def contains_floor(self) -> bool:
        return isinstance(self._attr1, Floor) or isinstance(self._attr2, Floor)


class RelativeHint(Hint):
    """
    Represents a hint of a relation between two floor
    that are of a certain distance of each other.
    Examples:
    The red floor is above the blue floor:
        RelativeHint(Color.Red, Color.Red, 1)
    The frog lives three floor below the yellow floor:
        RelativeHint(Animal.Frog, Color.Yellow, -3)
    The third floor is two floors below the fifth floor:
        RelativeHint(Floor.Third, Floor.Fifth, -2)
    """
    def __init__(self, attr1, attr2, difference):
        self._attr1 = attr1
        self._attr2 = attr2
        self._difference = difference


class NeighborHint(Hint):
    """
    Represents a hint of a relation between two floors that are adjacent
    (first either above or below the second).
    Examples:
    The green floor is neighboring the floor where the chicken lives:
        NeighborHint(Color.Green, Animal.Chicken)
    The grasshopper is a neighbor of the rabbit:
        NeighborHint(Animal.Grasshopper, Animal.Rabbit)
    The yellow floor is neighboring the third floor:
        NeighborHint(Color.Yellow, Floor.Third)
    """
    def __init__(self, attr1, attr2):
        self._attr1 = attr1
        self._attr2 = attr2

class Story(object):
    def __init__(self):
        self._color = Color.Empty
        self._animal = Animal.Empty

class Assigment(object):
    """
    Tracks the current state of the floor assignments.
    Manages which animals and colors are still available and validates placements.

    Attributes:
        _tower: List[Story], holds the current color and animal on each floor.
        _free_animals: List[Animal], animals not yet assigned.
        _free_colors: List[Color], colors not yet assigned.
        _possibilities: float, running total of possible configurations.
    """
    def __init__(self):
        self._tower: List = [Story() for _ in range(5)]
        self._possibilities: int = 14400
        self._free_animals: List = [a for a in Animal if a.value != '']
        self._free_colors: List = [c for c in Color if c.value != '']

    def is_floor_animal_empty(self, floor: Floor) -> bool:
        return self._tower[floor]._animal == Animal.Empty

    def is_floor_color_empty(self, floor: Floor, color=Color.Empty) -> bool:
        return self._tower[floor]._color == color
    
    def is_free_animal(self, animal: Animal) -> bool:
        return animal in self._free_animals
        
    def is_free_color(self, color: Color) -> bool:
        return color in self._free_colors

    def is_valid_floor_animal_assigment(self,floor: Floor, animal: Animal) -> bool:
        return self.is_floor_animal_empty(floor) and self.is_free_animal(animal)

    def is_valid_floor_color_assigment(self,floor: Floor, color: Color) -> bool:
        return self.is_floor_color_empty(floor) and self.is_free_color(color)
        
    def is_color_already_applied(self,floor: Floor, color: Color) -> bool:
        return self._tower[floor]._color == color
        
    def is_animal_already_applied(self,floor: Floor, animal: Animal) -> bool:
        return self._tower[floor]._animal == animal
        
    def apply_animal(self, floor: Floor, animal: Animal) -> None:
        self._tower[floor]._animal = animal
        self._possibilities /= len(self._free_animals)
        self._free_animals.remove(animal)

    def apply_color(self, floor: Floor, color: Color) -> None:
        self._tower[floor]._color = color
        self._possibilities /= len(self._free_colors)
        self._free_colors.remove(color)


def helper_neighbor_hint(
    hint: NeighborHint,
    hints: List[Hint],
    assigment: Assigment
) -> int:
    """
    Handles NeighborHints by trying all valid floor pairs that are adjacent.
    
    Returns:
        int: Total valid configurations found.
    """
    possibilities = 0

    for floor in list(Floor)[:-1]:  # Floors 1 to 4 (excluding top floor)
        above = floor_above(floor)
        if not above:
            continue

        # case 1: attr1 on current floor, attr2 on floor above
        hints_case_1 = hints.copy()
        hints_case_1.append(AbsoluteHint(floor, hint._attr1))
        hints_case_1.append(AbsoluteHint(above, hint._attr2))
        possibilities += helper(hints_case_1, deepcopy(assigment))

        # case 2: attr2 on current floor, attr1 on floor above
        hints_case_2 = hints.copy()
        hints_case_2.append(AbsoluteHint(floor, hint._attr2))
        hints_case_2.append(AbsoluteHint(above, hint._attr1))
        possibilities += helper(hints_case_2, deepcopy(assigment))

    return possibilities    
    
def helper_relative_hint(
    hint: RelativeHint,
    hints: List[Hint],
    assigment: Assigment
) -> int:
    """
    Handles RelativeHints by trying floor pairs with the given difference.

    Returns:
        int: Total valid configurations found.
    """
    possibilities = 0

    floors = list(Floor)

    for floor in floors:
        index = floors.index(floor)
        attr1_index = index + hint._difference

        if 0 <= attr1_index < len(floors):
            attr1_index = floors[attr1_index]

            # attr1 on `attr1_index`, attr2 on `floor`
            hints_case = hints.copy()
            hints_case.append(AbsoluteHint(attr1_index, hint._attr1))
            hints_case.append(AbsoluteHint(floor, hint._attr2))
            possibilities += helper(hints_case, deepcopy(assigment))

    return possibilities
    
def helper_absolue_no_floor_hint(hint: AbsoluteHint, hints: List[Hint], assigment: Assigment) -> int:
    """
    Handles AbsoluteHints where neither attr is a Floor (Animal-Color or Color-Animal).
    Tries placing both on each floor and recurses.

    Returns:
        int: Total valid configurations found.
    """
    # hint of (Color, Animal) or (Animal, Color)
    possibilities: int = 0
    for floor in Floor:
        hints_copy: List[Hint] = hints.copy() 
        hints_copy.append(AbsoluteHint(floor, hint._attr1))
        hints_copy.append(AbsoluteHint(floor, hint._attr2))
        possibilities += helper(hints_copy, deepcopy(assigment))
    return possibilities
    
def apply_absolute_hint_if_valid(hint: AbsoluteHint, assigment: Assigment) -> bool:
    """
    Attempts to apply an AbsoluteHint to the assignment, if it's valid.

    Returns:
        bool: True if the hint was applied (or already matches), False otherwise.
    """
    if type(hint._attr1) == type(hint._attr2):
        return False
    
    # hint of (Floor, _)
    if isinstance(hint._attr1, Floor):
        floor: Floor = hint._attr1
        if floor > Floor.Fifth or floor < Floor.First:
            return False;
        
        # hint of (Floor, Animal)
        if isinstance(hint._attr2, Animal):
            animal: Animal = hint._attr2
            if assigment.is_valid_floor_animal_assigment(floor, animal):
                assigment.apply_animal(floor, animal)
                return True
            return assigment.is_animal_already_applied(floor, animal)

        # hint of (Floor, Color)
        color: Color = hint._attr2
        if assigment.is_valid_floor_color_assigment(floor, color):
            assigment.apply_color(floor, color)
            return True
        return assigment.is_color_already_applied(floor, color)
        
    # hint of (_, Floor)
    if isinstance(hint._attr2, Floor):
        floor: Floor = hint._attr2
        if floor > Floor.Fifth or floor < Floor.First:
            return False;
        
        # hint of (Animal, Floor)
        if isinstance(hint._attr1, Animal):
            animal: Animal = hint._attr1
            if assigment.is_valid_floor_animal_assigment(floor, animal):
                assigment.apply_animal(floor, animal)
                return True
            return assigment.is_animal_already_applied(floor, animal)

        # hint of (Color, Floor)
        color: Color = hint._attr1
        if assigment.is_valid_floor_color_assigment(floor, color):
            assigment.apply_color(floor, color)
            return True
        return assigment.is_color_already_applied(floor, color)
        
def helper(hints: List[Hint], assigment: Assigment) -> int:
    """
    Recursively applies hints to the assignment and explores valid solutions.

    Args:
        hints (List[Hint]): Remaining hints to apply.
        assigment (Assigment): Current assignment state.

    Returns:
        int: Number of valid configurations for this path.
    """
    if not hints:
        return assigment._possibilities
        
    hint: Hint = hints[0]
    if isinstance(hint, RelativeHint):
        return helper_relative_hint(hint, hints[1:], assigment)
    
    if isinstance(hint, NeighborHint):
        return helper_neighbor_hint(hint, hints[1:], assigment)
    
    if isinstance(hint, AbsoluteHint):
        if hint.contains_floor():
            if apply_absolute_hint_if_valid(hint, assigment):
                return helper(hints[1:], assigment)
            return 0
        return helper_absolue_no_floor_hint(hint, hints[1:], assigment)

def count_assignments(hints):
    """
    Given a list of Hint objects, return the number of
    valid assignments that satisfy these hints.
    TODO: Needs to be implemented
    """
    ass = Assigment()
    return helper(hints, ass)

HINTS_EX1 = [
    AbsoluteHint(Animal.Rabbit, Floor.First),
    AbsoluteHint(Animal.Chicken, Floor.Second),
    AbsoluteHint(Floor.Third, Color.Red),
    AbsoluteHint(Animal.Bird, Floor.Fifth),
    AbsoluteHint(Animal.Grasshopper, Color.Orange),
    NeighborHint(Color.Yellow, Color.Green),
]

HINTS_EX2 = [
    AbsoluteHint(Animal.Bird, Floor.Fifth),
    AbsoluteHint(Floor.First, Color.Green),
    AbsoluteHint(Animal.Frog, Color.Yellow),
    NeighborHint(Animal.Frog, Animal.Grasshopper),
    NeighborHint(Color.Red, Color.Orange),
    RelativeHint(Animal.Chicken, Color.Blue, -4)
]

HINTS_EX3 = [
    RelativeHint(Animal.Rabbit, Color.Green, -2)
]


def test():
    assert count_assignments(HINTS_EX1) == 2, 'Failed on example #1'
    assert count_assignments(HINTS_EX2) == 4, 'Failed on example #2'
    assert count_assignments(HINTS_EX3) == 1728, 'Failed on example #3'
    print('Success!')


if __name__ == '__main__':
    test()
