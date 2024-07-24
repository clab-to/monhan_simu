import json
import os
from abc import ABCMeta
from abc import abstractmethod

import pandas as pd


class CsvLoader:
    def load(self, filepath, options) -> pd.DataFrame:
        return pd.read_csv(filepath, encoding="utf-8", **options)


class CsvDataTable(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.loader = CsvLoader()
        self.dataframe = self.loader.load(
            filepath=self.define_filepath(),
            options=self.define_read_option(),
        )
        self.is_head = 0
        self.is_torso = 0
        self.is_arm = 0
        self.is_wst = 0
        self.is_leg = 0
        self.is_talisman = 0
        self.define_optimize_parameter()

    @abstractmethod
    def define_filepath(self):
        return ""

    @abstractmethod
    def define_read_option(self):
        return {}

    @abstractmethod
    def define_optimize_parameter(self):
        return None

    @abstractmethod
    def to_optimize_format(self):
        pass

    def convert_slot_level(self, slot1, slot2, slot3):
        converted_slot_level = {
            "key": ["over-slot1", "over-slot2", "over-slot3", "over-slot4"],
            "value": [0, 0, 0, 0],
        }
        for slot_level in [slot1, slot2, slot3]:
            for index in range(slot_level):
                converted_slot_level["value"][index] += 1
        return {
            key: value
            for key, value in zip(
                converted_slot_level["key"], converted_slot_level["value"]
            )
        }

    def skillname_ja2en(self, skillname_ja):
        with open("skills.json", encoding="utf-8") as f:
            skills = {skill["ja"]: skill["en"] for skill in json.load(f)}
        skillname_en = skills[skillname_ja]
        return skillname_en


class ArmorDataTable(CsvDataTable):
    def define_read_option(self):
        param = {
            "dtype": {
                "name": "object",
                "sex": "object",
                "slot1": "Int64",
                "slot2": "Int64",
                "slot3": "Int64",
                "defense_finally": "Int64",
                "resistance_fire": "Int64",
                "resistance_water": "Int64",
                "resistance_thunder": "Int64",
                "resistance_ice": "Int64",
                "resistance_dragon": "Int64",
                "skill_name1": "object",
                "skill_point1": "Int64",
                "skill_name2": "object",
                "skill_point2": "Int64",
                "skill_name3": "object",
                "skill_point3": "Int64",
                "skill_name4": "object",
                "skill_point4": "Int64",
                "skill_name5": "object",
                "skill_point5": "Int64",
                "oneset": "object",
                "qurious_table": "object",
            }
        }
        return {**param, "usecols": param["dtype"].keys()}

    def to_optimize_format(self):
        rows = []
        for (
            name,
            sex,
            slot1,
            slot2,
            slot3,
            defense_finally,
            resistance_fire,
            resistance_water,
            resistance_thunder,
            resistance_ice,
            resistance_dragon,
            skill_name1,
            skill_point1,
            skill_name2,
            skill_point2,
            skill_name3,
            skill_point3,
            skill_name4,
            skill_point4,
            skill_name5,
            skill_point5,
        ) in zip(
            self.dataframe["name"].values.tolist(),
            self.dataframe["sex"].values.tolist(),
            self.dataframe["slot1"].values.tolist(),
            self.dataframe["slot2"].values.tolist(),
            self.dataframe["slot3"].values.tolist(),
            self.dataframe["defense_finally"].values.tolist(),
            self.dataframe["resistance_fire"].values.tolist(),
            self.dataframe["resistance_water"].values.tolist(),
            self.dataframe["resistance_thunder"].values.tolist(),
            self.dataframe["resistance_ice"].values.tolist(),
            self.dataframe["resistance_dragon"].values.tolist(),
            self.dataframe["skill_name1"].values.tolist(),
            self.dataframe["skill_point1"].values.tolist(),
            self.dataframe["skill_name2"].values.tolist(),
            self.dataframe["skill_point2"].values.tolist(),
            self.dataframe["skill_name3"].values.tolist(),
            self.dataframe["skill_point3"].values.tolist(),
            self.dataframe["skill_name4"].values.tolist(),
            self.dataframe["skill_point4"].values.tolist(),
            self.dataframe["skill_name5"].values.tolist(),
            self.dataframe["skill_point5"].values.tolist(),
        ):
            row = {
                "name": name,
                "sex": sex,
                "head": self.is_head,
                "torso": self.is_torso,
                "arm": self.is_arm,
                "wst": self.is_wst,
                "leg": self.is_leg,
                "talisman": self.is_talisman,
                "def": defense_finally,
                "r_fire": resistance_fire,
                "r_water": resistance_water,
                "r_thunder": resistance_thunder,
                "r_ice": resistance_ice,
                "r_dragon": resistance_dragon,
            }
            row.update(self.convert_slot_level(slot1, slot2, slot3))
            for s_name, s_point in zip(
                [skill_name1, skill_name2, skill_name3, skill_name4, skill_name5],
                [skill_point1, skill_point2, skill_point3, skill_point4, skill_point5],
            ):
                if isinstance(s_name, str) and isinstance(s_point, int):
                    s_name_en = self.skillname_ja2en(s_name)
                    row.update({s_name_en: s_point})
            rows.append(row)

        return rows


class HeadDataTable(ArmorDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_EQUIP_HEAD.csv"

    def define_optimize_parameter(self):
        self.is_head = 1


class TorsoDataTable(ArmorDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_EQUIP_TORSO.csv"

    def define_optimize_parameter(self):
        self.is_torso = 1


class ArmDataTable(ArmorDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_EQUIP_ARM.csv"

    def define_optimize_parameter(self):
        self.is_arm = 1


class WaistDataTable(ArmorDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_EQUIP_WST.csv"

    def define_optimize_parameter(self):
        self.is_wst = 1


class LegDataTable(ArmorDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_EQUIP_LEG.csv"

    def define_optimize_parameter(self):
        self.is_leg = 1


class DecoDataTable(CsvDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_DECO.csv"

    def define_read_option(self):
        param = {
            "dtype": {
                "name": "object",
                "rarity": "object",
                "slot": "object",
                "skill_name1": "object",
                "skill_point1": "object",
                "skill_name2": "object",
                "skill_point2": "object",
                "temp_number": "object",
            }
        }
        return {**param, "usecols": param["dtype"].keys()}

    def define_optimize_parameter(self):
        pass

    def to_optimize_format(self):
        pass


class SkillDataTable(CsvDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_SKILL.csv"

    def define_read_option(self):
        param = {
            "dtype": {
                "skill_name": "object",
                "activated_skill_name": "object",
                "requied_point": "object",
                "category": "object",
                "effect": "object",
                "skill_number": "object",
                "temp_number": "object",
                "cost": "object",
            }
        }
        return {**param, "usecols": param["dtype"].keys()}

    def define_optimize_parameter(self):
        pass

    def to_optimize_format(self):
        pass
