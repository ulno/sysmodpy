from __future__ import annotations
from typing import List, Set
from unittest import TestCase

from sysmodpy import decorate


class University:
    name: str
    # associations
    students: Set[Student]
    rooms: Set[Room]


class Student:
    name: str
    student_id: str
    credits: int = 0
    motivation: int = 0
    # associations
    university: University
    room: Room

class Room:
    name: str
    room_number: str
    topic: str = "N/A"
    credits: int = 0
    # associations
    university: University
    students: Set[Student]

# TODO: think about multiple associations

class Test(TestCase):
    def test_decorate(self):
        decorate(University, Student, Room)
        sru = University().with_name("Study Right University")
        karli = Student().with_name("Karli")
        alice = Student().with_name("Karli")
        print(sru.get_name())
        sru.add_students(karli, alice)
        audimax = Room().with_name("Audimax")
        sru.add_rooms(audimax)
        karli.set_room(audimax)
        print("get_student1:", sru.get_students())
        sru.remove_students(karli)
        print("get_student2:", sru.get_students())
        print("get_room_from_sru:", sru.get_rooms())
        #self.fail()
