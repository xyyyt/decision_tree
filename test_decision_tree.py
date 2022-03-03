#!/usr/bin/env python3

from queue import Queue
import unittest
from decision_tree import tree_node, recursive_decision_tree, \
    iterative_decision_tree

class recursive_decision_tree_Test(unittest.TestCase):
    def test_case_1(self):
        main_tree = recursive_decision_tree()

        self.assertEqual(main_tree.size(), 0)

        class citizen_status:
            __slots__ = ("refund", "marital_status", "taxable_income")

            def __init__(self,
                         refund=None,
                         marital_status=None,
                         taxable_income=None):
                self.refund = refund
                self.marital_status = marital_status
                self.taxable_income = taxable_income

        citizen_1 = citizen_status(False, "Single,Divorced", 120000)

        self.assertIsNone(main_tree.get(0, citizen_1))
        self.assertIsNone(main_tree.get(1, citizen_1))
        self.assertIsNone(main_tree.get(2, citizen_1))
        self.assertIsNone(main_tree.get(42, citizen_1))

        self.assertEqual(
            main_tree.add(42, citizen_1, None, None), (None, False))
        self.assertEqual(
            main_tree.add(3, citizen_1, None, None), (None, False))
        self.assertEqual(
            main_tree.add(2, citizen_1, None, None), (None, False))
        self.assertEqual(
            main_tree.add(1, citizen_1, None, None), (None, False))

        tracker = Queue()
        leaf_decision = main_tree.traversal(citizen_1)

        self.assertTrue(tracker.empty())
        self.assertIsNone(leaf_decision)

        def refund_decision(citizen):
            child_key = "Yes" if citizen.refund is True else "No"

            tracker.put_nowait(("Refund", citizen.refund))

            return child_key

        def refund_yes_leaf():
            return "Have nothing to pay"

        def marital_status_decision(citizen):
            if citizen.marital_status == "Single,Divorced":
                child_key = "Single,Divorced"
            elif citizen.marital_status == "Married":
                child_key = "Married"
            elif citizen.marital_status == "Widower":
                child_key = "Widower"
            else:
                child_key = None

            tracker.put_nowait(("Marital Status", citizen.marital_status))

            return child_key

        def marital_status_married_leaf():
            return "Have to pay, they are 2"

        def marital_status_widower_leaf():
            return "Unknown action, situation not stable enough"

        def taxable_income_decision(citizen):
            child_key = "< 80k" if citizen.taxable_income < 80000 else ">= 80k"

            tracker.put_nowait(("Taxable Income", citizen.taxable_income))

            return child_key

        def taxable_income_higher_or_equal_80k_leaf():
            return "Have to pay, high income"

        def taxable_income_smaller_80k_leaf():
            return "Have nothing to pay, low income"

        citizen_2 = citizen_status(True)
        node, inserted = main_tree.add(0, citizen_2, None, refund_decision)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        node, inserted = main_tree.add(0, citizen_2, None, refund_decision)

        self.assertIsNotNone(node)
        self.assertFalse(inserted)

        node, inserted = main_tree.add(1, citizen_2, "Yes", refund_yes_leaf)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        node, inserted = main_tree.add(42, citizen_2, "Yes", refund_yes_leaf)

        self.assertIsNone(node)
        self.assertFalse(inserted)
        self.assertEqual(main_tree.size(), 2)
        self.assertIsNotNone(main_tree.get(0, citizen_2))
        self.assertIsNotNone(main_tree.get(1, citizen_2))

        node, inserted = main_tree.add(
            1, citizen_2, "No", marital_status_decision)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        node.child_nodes["Single,Divorced"] = \
            tree_node(taxable_income_decision)

        node.child_nodes["Single,Divorced"].child_nodes = {
            "< 80k" : tree_node(taxable_income_smaller_80k_leaf),
            ">= 80k" : tree_node(taxable_income_higher_or_equal_80k_leaf)
        }

        self.assertEqual(recursive_decision_tree(
            node.child_nodes["Single,Divorced"]).size(),
                         3)
        self.assertEqual(main_tree.size(), 6)

        citizen_3 = citizen_status(False, "Married")
        node, inserted = main_tree.add(
            2, citizen_3, "Married", marital_status_married_leaf)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        citizen_4 = citizen_status(False, "Widower")
        node, inserted = main_tree.add(
            2, citizen_4, "Widower", marital_status_widower_leaf)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)
        self.assertEqual(recursive_decision_tree(node).size(), 1)
        self.assertEqual(main_tree.size(), 8)

        citizen_5 = citizen_status(False, "Single,Divorced", 40000)

        self.assertIsNotNone(main_tree.get(1, citizen_5))
        self.assertIsNotNone(main_tree.get(2, citizen_5))
        self.assertIsNotNone(main_tree.get(2, citizen_3))
        self.assertIsNotNone(main_tree.get(2, citizen_4))
        self.assertIsNotNone(main_tree.get(3, citizen_5))
        self.assertIsNotNone(main_tree.get(3, citizen_1))

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(citizen_1)

        self.assertEqual(
            tracker.qsize(), 3)
        self.assertEqual(
            tracker.get_nowait(), ("Refund", False))
        self.assertEqual(
            tracker.get_nowait(), ("Marital Status", "Single,Divorced"))
        self.assertEqual(
            tracker.get_nowait(), ("Taxable Income", 120000))
        self.assertEqual(
            leaf_decision(), "Have to pay, high income")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(citizen_2)

        self.assertEqual(tracker.qsize(), 1)
        self.assertEqual(tracker.get_nowait(), ("Refund", True))
        self.assertEqual(leaf_decision(), "Have nothing to pay")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(citizen_3)

        self.assertEqual(tracker.qsize(), 2)
        self.assertEqual(tracker.get_nowait(), ("Refund", False))
        self.assertEqual(tracker.get_nowait(), ("Marital Status", "Married"))
        self.assertEqual(leaf_decision(), "Have to pay, they are 2")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(citizen_4)

        self.assertEqual(
            tracker.qsize(), 2)
        self.assertEqual(
            tracker.get_nowait(), ("Refund", False))
        self.assertEqual(
            tracker.get_nowait(), ("Marital Status", "Widower"))
        self.assertEqual(
            leaf_decision(), "Unknown action, situation not stable enough")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(citizen_5)

        self.assertEqual(
            tracker.qsize(), 3)
        self.assertEqual(
            tracker.get_nowait(), ("Refund", False))
        self.assertEqual(
            tracker.get_nowait(), ("Marital Status", "Single,Divorced"))
        self.assertEqual(
            tracker.get_nowait(), ("Taxable Income", 40000))
        self.assertEqual(
            leaf_decision(), "Have nothing to pay, low income")

    def test_case_2(self):
        from enum import Enum

        class weather(Enum):
            SUNNY = 1
            RAINY = 2
            GLOOMY = 3
            SNOWY = 4

        tracker = Queue()

        def what_weather_is_it_decision(weather_report):
            if weather_report == weather.SUNNY:
                child_key = "Sunny"
            elif weather_report == weather.RAINY:
                child_key = "Rainy"
            elif weather_report == weather.GLOOMY:
                child_key = "Gloomy"
            elif weather_report == weather.SNOWY:
                child_key = "Snowy"
            else:
                child_key = None

            tracker.put_nowait(("what_weather_is_it", weather_report))

            return child_key

        def what_weather_is_it_sunny_leaf():
            return "go make a barbecue !"

        def what_weather_is_it_rainy_leaf():
            return "stay at home and go sleep !"

        def what_weather_is_it_gloomy_leaf():
            return "stay at home and go play video games !"

        def what_weather_is_it_snowy_leaf():
            return "go make a snowball fight !"

        root = tree_node(what_weather_is_it_decision)
        leaf_1 = tree_node(what_weather_is_it_sunny_leaf)
        leaf_2 = tree_node(what_weather_is_it_rainy_leaf)

        root.child_nodes = {"Sunny" : leaf_1, "Rainy" : leaf_2}

        main_tree = recursive_decision_tree(root)
        subtree_1 = recursive_decision_tree(leaf_1)
        subtree_2 = recursive_decision_tree(leaf_2)
        weather_report_1 = weather.SUNNY
        weather_report_2 = weather.RAINY
        weather_report_3 = weather.GLOOMY
        weather_report_4 = weather.SNOWY

        self.assertEqual(main_tree.size(), 3)
        self.assertEqual(subtree_1.size(), 1)
        self.assertEqual(subtree_2.size(), 1)
        self.assertIsNotNone(main_tree.get(0, weather_report_1))
        self.assertIsNotNone(main_tree.get(1, weather_report_1))
        self.assertIsNotNone(main_tree.get(1, weather_report_2))
        self.assertIsNone(main_tree.get(1, weather_report_3))
        self.assertIsNone(main_tree.get(1, weather_report_4))
        self.assertIsNotNone(subtree_1.get(0, weather_report_1))
        self.assertIsNone(subtree_1.get(1, weather_report_1))
        self.assertIsNotNone(subtree_2.get(0, weather_report_2))
        self.assertIsNone(subtree_2.get(1, weather_report_2))

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_3)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.GLOOMY))
        self.assertIsNone(
            leaf_decision)

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_4)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.SNOWY))
        self.assertIsNone(
            leaf_decision)

        self.assertEqual(main_tree.add(
            42, weather_report_3, "Gloomy", what_weather_is_it_gloomy_leaf),
            (None, False))
        self.assertEqual(main_tree.add(
            42, weather_report_4, "Snowy", what_weather_is_it_snowy_leaf),
            (None, False))

        node, inserted = main_tree.add(
            0, weather_report_3, "Gloomy", what_weather_is_it_gloomy_leaf)

        self.assertTrue(node is root)
        self.assertFalse(inserted)

        node, inserted = main_tree.add(
            0, weather_report_4, "Snowy", what_weather_is_it_snowy_leaf)

        self.assertTrue(node is root)
        self.assertFalse(inserted)

        node, inserted = main_tree.add(
            1, weather_report_3, "Gloomy", what_weather_is_it_gloomy_leaf)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        node, inserted = main_tree.add(
            1, weather_report_3, "Gloomy", what_weather_is_it_gloomy_leaf)

        self.assertIsNotNone(node)
        self.assertFalse(inserted)

        node, inserted = main_tree.add(
            1, weather_report_4, "Snowy", what_weather_is_it_snowy_leaf)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        node, inserted = main_tree.add(
            1, weather_report_4, "Snowy", what_weather_is_it_snowy_leaf)

        self.assertIsNotNone(node)
        self.assertFalse(inserted)

        leaf_3 = main_tree.get(1, weather_report_3)
        leaf_4 = main_tree.get(1, weather_report_4)

        self.assertIsNotNone(leaf_3)
        self.assertIsNotNone(leaf_4)
        self.assertEqual(recursive_decision_tree(leaf_3).size(), 1)
        self.assertEqual(recursive_decision_tree(leaf_4).size(), 1)
        self.assertEqual(main_tree.size(), 5)

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_1)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.SUNNY))
        self.assertEqual(
            leaf_decision(), "go make a barbecue !")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_2)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.RAINY))
        self.assertEqual(
            leaf_decision(), "stay at home and go sleep !")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_3)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.GLOOMY))
        self.assertEqual(
            leaf_decision(), "stay at home and go play video games !")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_4)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.SNOWY))
        self.assertEqual(
            leaf_decision(), "go make a snowball fight !")


class iterative_decision_tree_Test(unittest.TestCase):
    def test_case_1(self):
        main_tree = iterative_decision_tree()

        self.assertEqual(main_tree.size(), 0)

        class citizen_status:
            __slots__ = ("refund", "marital_status", "taxable_income")

            def __init__(self,
                         refund=None,
                         marital_status=None,
                         taxable_income=None):
                self.refund = refund
                self.marital_status = marital_status
                self.taxable_income = taxable_income

        citizen_1 = citizen_status(False, "Single,Divorced", 120000)

        self.assertIsNone(main_tree.get(0, citizen_1))
        self.assertIsNone(main_tree.get(1, citizen_1))
        self.assertIsNone(main_tree.get(2, citizen_1))
        self.assertIsNone(main_tree.get(42, citizen_1))

        self.assertEqual(
            main_tree.add(42, citizen_1, None, None), (None, False))
        self.assertEqual(
            main_tree.add(3, citizen_1, None, None), (None, False))
        self.assertEqual(
            main_tree.add(2, citizen_1, None, None), (None, False))
        self.assertEqual(
            main_tree.add(1, citizen_1, None, None), (None, False))

        tracker = Queue()
        leaf_decision = main_tree.traversal(citizen_1)

        self.assertTrue(tracker.empty())
        self.assertIsNone(leaf_decision)

        def refund_decision(citizen):
            child_key = "Yes" if citizen.refund is True else "No"

            tracker.put_nowait(("Refund", citizen.refund))

            return child_key

        def refund_yes_leaf():
            return "Have nothing to pay"

        def marital_status_decision(citizen):
            if citizen.marital_status == "Single,Divorced":
                child_key = "Single,Divorced"
            elif citizen.marital_status == "Married":
                child_key = "Married"
            elif citizen.marital_status == "Widower":
                child_key = "Widower"
            else:
                child_key = None

            tracker.put_nowait(("Marital Status", citizen.marital_status))

            return child_key

        def marital_status_married_leaf():
            return "Have to pay, they are 2"

        def marital_status_widower_leaf():
            return "Unknown action, situation not stable enough"

        def taxable_income_decision(citizen):
            child_key = "< 80k" if citizen.taxable_income < 80000 else ">= 80k"

            tracker.put_nowait(("Taxable Income", citizen.taxable_income))

            return child_key

        def taxable_income_higher_or_equal_80k_leaf():
            return "Have to pay, high income"

        def taxable_income_smaller_80k_leaf():
            return "Have nothing to pay, low income"

        citizen_2 = citizen_status(True)
        node, inserted = main_tree.add(0, citizen_2, None, refund_decision)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        node, inserted = main_tree.add(0, citizen_2, None, refund_decision)

        self.assertIsNotNone(node)
        self.assertFalse(inserted)

        node, inserted = main_tree.add(1, citizen_2, "Yes", refund_yes_leaf)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        node, inserted = main_tree.add(42, citizen_2, "Yes", refund_yes_leaf)

        self.assertIsNone(node)
        self.assertFalse(inserted)
        self.assertEqual(main_tree.size(), 2)
        self.assertIsNotNone(main_tree.get(0, citizen_2))
        self.assertIsNotNone(main_tree.get(1, citizen_2))

        node, inserted = main_tree.add(
            1, citizen_2, "No", marital_status_decision)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        node.child_nodes["Single,Divorced"] = \
            tree_node(taxable_income_decision)

        node.child_nodes["Single,Divorced"].child_nodes = {
            "< 80k" : tree_node(taxable_income_smaller_80k_leaf),
            ">= 80k" : tree_node(taxable_income_higher_or_equal_80k_leaf)
        }

        self.assertEqual(iterative_decision_tree(
            node.child_nodes["Single,Divorced"]).size(),
                         3)
        self.assertEqual(main_tree.size(), 6)

        citizen_3 = citizen_status(False, "Married")
        node, inserted = main_tree.add(
            2, citizen_3, "Married", marital_status_married_leaf)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        citizen_4 = citizen_status(False, "Widower")
        node, inserted = main_tree.add(
            2, citizen_4, "Widower", marital_status_widower_leaf)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)
        self.assertEqual(iterative_decision_tree(node).size(), 1)
        self.assertEqual(main_tree.size(), 8)

        citizen_5 = citizen_status(False, "Single,Divorced", 40000)

        self.assertIsNotNone(main_tree.get(1, citizen_5))
        self.assertIsNotNone(main_tree.get(2, citizen_5))
        self.assertIsNotNone(main_tree.get(2, citizen_3))
        self.assertIsNotNone(main_tree.get(2, citizen_4))
        self.assertIsNotNone(main_tree.get(3, citizen_5))
        self.assertIsNotNone(main_tree.get(3, citizen_1))

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(citizen_1)

        self.assertEqual(
            tracker.qsize(), 3)
        self.assertEqual(
            tracker.get_nowait(), ("Refund", False))
        self.assertEqual(
            tracker.get_nowait(), ("Marital Status", "Single,Divorced"))
        self.assertEqual(
            tracker.get_nowait(), ("Taxable Income", 120000))
        self.assertEqual(
            leaf_decision(), "Have to pay, high income")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(citizen_2)

        self.assertEqual(tracker.qsize(), 1)
        self.assertEqual(tracker.get_nowait(), ("Refund", True))
        self.assertEqual(leaf_decision(), "Have nothing to pay")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(citizen_3)

        self.assertEqual(tracker.qsize(), 2)
        self.assertEqual(tracker.get_nowait(), ("Refund", False))
        self.assertEqual(tracker.get_nowait(), ("Marital Status", "Married"))
        self.assertEqual(leaf_decision(), "Have to pay, they are 2")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(citizen_4)

        self.assertEqual(
            tracker.qsize(), 2)
        self.assertEqual(
            tracker.get_nowait(), ("Refund", False))
        self.assertEqual(
            tracker.get_nowait(), ("Marital Status", "Widower"))
        self.assertEqual(
            leaf_decision(), "Unknown action, situation not stable enough")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(citizen_5)

        self.assertEqual(
            tracker.qsize(), 3)
        self.assertEqual(
            tracker.get_nowait(), ("Refund", False))
        self.assertEqual(
            tracker.get_nowait(), ("Marital Status", "Single,Divorced"))
        self.assertEqual(
            tracker.get_nowait(), ("Taxable Income", 40000))
        self.assertEqual(
            leaf_decision(), "Have nothing to pay, low income")

    def test_case_2(self):
        from enum import Enum

        class weather(Enum):
            SUNNY = 1
            RAINY = 2
            GLOOMY = 3
            SNOWY = 4

        tracker = Queue()

        def what_weather_is_it_decision(weather_report):
            if weather_report == weather.SUNNY:
                child_key = "Sunny"
            elif weather_report == weather.RAINY:
                child_key = "Rainy"
            elif weather_report == weather.GLOOMY:
                child_key = "Gloomy"
            elif weather_report == weather.SNOWY:
                child_key = "Snowy"
            else:
                child_key = None

            tracker.put_nowait(("what_weather_is_it", weather_report))

            return child_key

        def what_weather_is_it_sunny_leaf():
            return "go make a barbecue !"

        def what_weather_is_it_rainy_leaf():
            return "stay at home and go sleep !"

        def what_weather_is_it_gloomy_leaf():
            return "stay at home and go play video games !"

        def what_weather_is_it_snowy_leaf():
            return "go make a snowball fight !"

        root = tree_node(what_weather_is_it_decision)
        leaf_1 = tree_node(what_weather_is_it_sunny_leaf)
        leaf_2 = tree_node(what_weather_is_it_rainy_leaf)

        root.child_nodes = {"Sunny" : leaf_1, "Rainy" : leaf_2}

        main_tree = iterative_decision_tree(root)
        subtree_1 = iterative_decision_tree(leaf_1)
        subtree_2 = iterative_decision_tree(leaf_2)
        weather_report_1 = weather.SUNNY
        weather_report_2 = weather.RAINY
        weather_report_3 = weather.GLOOMY
        weather_report_4 = weather.SNOWY

        self.assertEqual(main_tree.size(), 3)
        self.assertEqual(subtree_1.size(), 1)
        self.assertEqual(subtree_2.size(), 1)
        self.assertIsNotNone(main_tree.get(0, weather_report_1))
        self.assertIsNotNone(main_tree.get(1, weather_report_1))
        self.assertIsNotNone(main_tree.get(1, weather_report_2))
        self.assertIsNone(main_tree.get(1, weather_report_3))
        self.assertIsNone(main_tree.get(1, weather_report_4))
        self.assertIsNotNone(subtree_1.get(0, weather_report_1))
        self.assertIsNone(subtree_1.get(1, weather_report_1))
        self.assertIsNotNone(subtree_2.get(0, weather_report_2))
        self.assertIsNone(subtree_2.get(1, weather_report_2))

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_3)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.GLOOMY))
        self.assertIsNone(
            leaf_decision)

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_4)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.SNOWY))
        self.assertIsNone(
            leaf_decision)

        self.assertEqual(main_tree.add(
            42, weather_report_3, "Gloomy", what_weather_is_it_gloomy_leaf),
            (None, False))
        self.assertEqual(main_tree.add(
            42, weather_report_4, "Snowy", what_weather_is_it_snowy_leaf),
            (None, False))

        node, inserted = main_tree.add(
            0, weather_report_3, "Gloomy", what_weather_is_it_gloomy_leaf)

        self.assertTrue(node is root)
        self.assertFalse(inserted)

        node, inserted = main_tree.add(
            0, weather_report_4, "Snowy", what_weather_is_it_snowy_leaf)

        self.assertTrue(node is root)
        self.assertFalse(inserted)

        node, inserted = main_tree.add(
            1, weather_report_3, "Gloomy", what_weather_is_it_gloomy_leaf)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        node, inserted = main_tree.add(
            1, weather_report_3, "Gloomy", what_weather_is_it_gloomy_leaf)

        self.assertIsNotNone(node)
        self.assertFalse(inserted)

        node, inserted = main_tree.add(
            1, weather_report_4, "Snowy", what_weather_is_it_snowy_leaf)

        self.assertIsNotNone(node)
        self.assertTrue(inserted)

        node, inserted = main_tree.add(
            1, weather_report_4, "Snowy", what_weather_is_it_snowy_leaf)

        self.assertIsNotNone(node)
        self.assertFalse(inserted)

        leaf_3 = main_tree.get(1, weather_report_3)
        leaf_4 = main_tree.get(1, weather_report_4)

        self.assertIsNotNone(leaf_3)
        self.assertIsNotNone(leaf_4)
        self.assertEqual(iterative_decision_tree(leaf_3).size(), 1)
        self.assertEqual(iterative_decision_tree(leaf_4).size(), 1)
        self.assertEqual(main_tree.size(), 5)

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_1)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.SUNNY))
        self.assertEqual(
            leaf_decision(), "go make a barbecue !")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_2)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.RAINY))
        self.assertEqual(
            leaf_decision(), "stay at home and go sleep !")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_3)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.GLOOMY))
        self.assertEqual(
            leaf_decision(), "stay at home and go play video games !")

        tracker.queue.clear()

        leaf_decision = main_tree.traversal(weather_report_4)

        self.assertEqual(
            tracker.qsize(), 1)
        self.assertEqual(
            tracker.get_nowait(), ("what_weather_is_it", weather.SNOWY))
        self.assertEqual(
            leaf_decision(), "go make a snowball fight !")


if __name__ == "__main__":
    import random

    unittest.TestLoader.sortTestMethodsUsing = \
        lambda _1, _2, _3: random.choice([1, 0, -1])

    unittest.main()
