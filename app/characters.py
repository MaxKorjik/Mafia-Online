from dataclasses import dataclass

@dataclass
class Surgeon:
    name: str = "Surgeon"
    age: int = 30
    illness: str = "Broken arm"
    hobby: str = "Playing guitar"
    mentality: str = "Patient"
    items: str = "Suture kit"
    fear: str = "Claustrophobia"

@dataclass
class Teacher:
    name: str = "Teacher"
    age: int = 35
    illness: str = "Healthy"
    hobby: str = "Drawing"
    mentality: str = "Kind"
    items: str = "Survival kit"
    fear: str = "Darkness"

@dataclass
class Programmer:
    name: str = "Programmer"
    age: int = 25
    illness: str = "Hypertony"
    hobby: str = "Playing video games"
    mentality: str = "Practical"
    items: str = "Solar panels"
    fear: str = "Water"

@dataclass
class Agronomist:
    name: str = "Agronomist"
    age: int = 55
    illness: str = "Hypertension"
    hobby: str = "Cooking"
    mentality: str = "Practical"
    items: str = "Seeds of 30 kinds of vegetables"
    fear: str = "Birds"

@dataclass
class ExSoldier:
    name: str = "Ex-Soldier"
    age: int = 48
    illness: str = "PTSD"
    hobby: str = "Psychology"
    mentality: str = "Leader"
    items: str = "Weapon and ammo"
    fear: str = "Fire"

@dataclass
class TheaterActor:
    name: str = "Theater Actor"
    age: int = 35
    illness: str = "Congenital blindness"
    hobby: str = "Music"
    mentality: str = "Charismatic"
    items: str = "Portable speaker"
    fear: str = "Loneliness"

@dataclass
class MechanicalEngineer:
    name: str = "Mechanical Engineer"
    age: int = 40
    illness: str = "Arthritis"
    hobby: str = "Robot modeling"
    mentality: str = "Perfectionist"
    items: str = "Spare parts for generator repair"
    fear: str = "Loud noises"

@dataclass
class Pharmacist:
    name: str = "Pharmacist"
    age: int = 33
    illness: str = "Dust allergy"
    hobby: str = "Herb collecting"
    mentality: str = "Calm"
    items: str = "Medical kit with medicines"
    fear: str = "Close contact with people"

@dataclass
class SciFiWriter:
    name: str = "Science Fiction Writer"
    age: int = 29
    illness: str = "Depression"
    hobby: str = "History of civilizations"
    mentality: str = "Highly imaginative"
    items: str = "Book '100 Ways to Build a New Society'"
    fear: str = "Losing memory"

@dataclass
class ChildPsychologist:
    name: str = "Child Psychologist"
    age: int = 38
    illness: str = "Back pain"
    hobby: str = "Dancing"
    mentality: str = "Friendly"
    items: str = "Teddy bear and children's books"
    fear: str = "Crying children"

@dataclass
class Event:
    def __init__(self, description, related_to=None):
        self.description = description
        self.related_to = related_to  # Link to character name

    def __str__(self):
        return f"Event: {self.description}\nRelated to: {self.related_to if self.related_to else 'Unknown'}\n"


super_events = [
    Event("Near the body, a torn guitar string was found. The word 'TIGHT' was scratched into the wall.", "Surgeon"),
    Event("At the shelter entrance, a drawing was left open. A blood drop stained one corner. Tracks led to a children's library.", "Teacher"),
    Event("A pool of water covered the floor. A shattered solar panel lay inside. Someone left in a hurry.", "Programmer"),
    Event("In the garden, torn vegetable seed packs were scattered. A crow feather lay on the soil.", "Agronomist"),
    Event("By a burned-out campfire, a military jacket button was found. Someone had fired a weapon... at no one.", "Ex-Soldier"),
    Event("A portable speaker was still playing music on the theater steps. No one was around to listen.", "Theater Actor"),
    Event("In the workshop, generator parts were strewn everywhere. Crumpled earplugs lay in the corner.", "Mechanical Engineer"),
    Event("A medical bag was neatly left on a rock. A dusty handprint stained its surface.", "Pharmacist"),
    Event("Pages from '100 Ways to Build a New Society' were torn and scattered. Some were covered in confused handwriting.", "Science Fiction Writer"),
    Event("A scorched teddy bear lay in the room's corner. Tear stains were visible nearby.", "Child Psychologist"),
]


mini_events = [
    "Ви чуєте жіночий голос, що шепоче в темряві.",
    "Ви чуєте чоловічий крик посеред глибокої ночі.",
    "Ви чуєте звук кроків, які зникають у тиші.",
    "Ви чуєте два постріли.",
    "Ви чуєте глухий сміх, який швидко обривається.",
    "Ви бачите силует чоловіка у вікні навпроти.",
    "Ви бачите жіночу постать у вікні.",
    "Ви бачите тінь руки на стіні, яка відбивається від ліхтарика.",
    "Ви бачите ліхтарик, що блимає серед темних вулиць.",
    "Ви чуєте жіночий крик посеред глибокої ночі."
]