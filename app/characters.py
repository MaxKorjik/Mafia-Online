

# class Surgeon:
#     name = "Surgeon"
#     age = 30
#     illness = "Broken arm"
#     hobby = "Playing guitar"
#     mentality = "Patient"
#     items = "Suture kit"
#     fear = "Claustrophobia"

# class Teacher:
#     name = "Teacher"
#     age = 35
#     illness = "Healthy"
#     hobby = "Drawing"
#     mentality = "Kind"
#     items = "Survival kit"
#     fear = "Darkness"

# class Programmer:
#     name = "Programmer"
#     age = 25
#     illness = "Hypertony"
#     hobby = "Playing video games"
#     mentality = "Practical"
#     items = "Solar panels"
#     fear = "Water"

# class Agronomist:
#     name = "Agronomist"
#     age = 55
#     illness = "Hypertension"
#     hobby = "Cooking"
#     mentality = "Practical"
#     items = "Seeds of 30 kinds of vegetables"
#     fear = "Birds"

# class ExSoldier:
#     name = "Ex-Soldier"
#     age = 48
#     illness = "PTSD"
#     hobby = "Psychology"
#     mentality = "Leader"
#     items = "Weapon and ammo"
#     fear = "Fire"

# class TheaterActor:
#     name = "Theater Actor"
#     age = 35
#     illness = "Congenital blindness"
#     hobby = "Music"
#     mentality = "Charismatic"
#     items = "Portable speaker"
#     fear = "Loneliness"

# class MechanicalEngineer:
#     name = "Mechanical Engineer"
#     age = 40
#     illness = "Arthritis"
#     hobby = "Robot modeling"
#     mentality = "Perfectionist"
#     items = "Spare parts for generator repair"
#     fear = "Loud noises"

# class Pharmacist:
#     name = "Pharmacist"
#     age = 33
#     illness = "Dust allergy"
#     hobby = "Herb collecting"
#     mentality = "Calm"
#     items = "Medical kit with medicines"
#     fear = "Close contact with people"

# class SciFiWriter:
#     name = "Science Fiction Writer"
#     age = 29
#     illness = "Depression"
#     hobby = "History of civilizations"
#     mentality = "Highly imaginative"
#     items = "Book '100 Ways to Build a New Society'"
#     fear = "Losing memory"

# class ChildPsychologist:
#     name = "Child Psychologist"
#     age = 38
#     illness = "Back pain"
#     hobby = "Dancing"
#     mentality = "Friendly"
#     items = "Teddy bear and children's books"
#     fear = "Crying children"

# class Event:
#     def __init__(self, description, related_to=None):
#         self.description = description
#         self.related_to = related_to  # Link to character name

#     def __str__(self):
#         return f"Event: {self.description}\nRelated to: {self.related_to if self.related_to else 'Unknown'}\n"


# events = [
#     Event("Near the body, a torn guitar string was found. The word 'TIGHT' was scratched into the wall.", "Surgeon"),
#     Event("At the shelter entrance, a drawing was left open. A blood drop stained one corner. Tracks led to a children's library.", "Teacher"),
#     Event("A pool of water covered the floor. A shattered solar panel lay inside. Someone left in a hurry.", "Programmer"),
#     Event("In the garden, torn vegetable seed packs were scattered. A crow feather lay on the soil.", "Agronomist"),
#     Event("By a burned-out campfire, a military jacket button was found. Someone had fired a weapon... at no one.", "Ex-Soldier"),
#     Event("A portable speaker was still playing music on the theater steps. No one was around to listen.", "Theater Actor"),
#     Event("In the workshop, generator parts were strewn everywhere. Crumpled earplugs lay in the corner.", "Mechanical Engineer"),
#     Event("A medical bag was neatly left on a rock. A dusty handprint stained its surface.", "Pharmacist"),
#     Event("Pages from '100 Ways to Build a New Society' were torn and scattered. Some were covered in confused handwriting.", "Science Fiction Writer"),
#     Event("A scorched teddy bear lay in the room's corner. Tear stains were visible nearby.", "Child Psychologist"),
# ]
# [Повар, Слесарь, Бармен, Проститутка, Полицейский, Военный]
#     улику выбрать только для присутствующих персов 
# class  Archetype:
#     name : str
#     surname : str
#     male : str
#     age : int
#     height : int
#     body : str
#     clothes : str
#     illness: str
#     pets : str
#     personal_items : str
#     sign : str
    
    
# class Worker:
#     name = "Марк" 
#     surname = "Фрамко" 
#     male = "man" 
#     age = 67 
#     height = 1.8 
#     body = "Кремезний чоловік"
#     clothes = "Носить старий жакет та сині джинси" #random
#     illness = "Має сильний кашель та нежить"   #random 
#     pets = "Має старого пса, німецька вівчарка"  #random
#     personal_items = "Носить в кишені стару запальничку та трубу для табаку" #random 
#     sign = "Має великий шрам на правій нозі, через це храмий" #random

#     def __init__(self):
#         pass
    

# 1) нельзя выбрать улику для персонажей которых нет в комнате :
#     """логика работы программы должна при переходе на дневную фазу, выбрать улику, значит при ее выборе будет 
#     происходить проверка доступных для этого персонажей, проверка персонажей в комнате"""
# 2) улика не должна наводить прямо на мирных жителей / должна быть из пулла мафии:
#     """подразумеваеться то что хотябы одна улика должна наводить на персонажа который является мафией,"""
# 3) можно давать 2-3 улики: 
#     """можно сделать что бы писало несколько улик что бы можно было получить достаточно инфы что бы вести расследование
#     и не подумать на мирного"""
# # при выпадении улики если это полный рандом, она может наводить на мирного игрока, тоесть вообще мафия может не подходить под найденые улики
# # это можно обыграть как подделку улик и подставу мирных игроков но покачто это МИМО, не рассматривать



# # для начала нужно придумать схему по которой будут распределяться приметы для персонажей

# # То как будет работать распределение улик
# """идет проверка на подходящие персонажи, после """