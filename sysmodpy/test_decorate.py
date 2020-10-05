from __future__ import annotations
from typing import List, Set
from unittest import TestCase

from sysmodpy import decorate


class University:
    name: str
    # associations
    student: Student = None
    # students: Set[Student]
    rooms: Set[University]


class Student:
    name: str
    student_id: str
    credits: int
    motivation: int
    # associations
    university: University = None
    room: Room

class Room:
    name: str
    room_number: str
    topic: str
    credits: int
    # associations
    university: University
    students: Set[Student]

# TODO: think about multiple associations

class Test(TestCase):
    def test_decorate(self):
        decorate(University, Student, Room)
        sru = University().with_name("Study Right University")
        karli = Student().with_name("Karli")
        print(sru.get_name())
        sru.set_student(karli)
        audimax = Room().with_name("Audimax")
        sru.add_rooms(audimax)
        print("get_student1:", sru.get_student())
        sru.remove_student(karli)
        print("get_student2:", sru.get_student())
        print("get_room_from_sru:", sru.get_rooms())
        #self.fail()
