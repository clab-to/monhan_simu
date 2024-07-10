import os
from abc import ABCMeta, abstractmethod

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

    @abstractmethod
    def define_filepath(self):
        return ""

    @abstractmethod
    def define_read_option(self):
        return {}


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
                "fire_resistance": "Int64",
                "water_resistance": "Int64",
                "thunder_resistance": "Int64",
                "ice_resistance": "Int64",
                "dragon_resistance": "Int64",
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


class HeadDataTable(ArmorDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_EQUIP_HEAD.csv"


class TorsoDataTable(ArmorDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_EQUIP_TORSO.csv"


class ArmDataTable(ArmorDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_EQUIP_ARM.csv"


class WaistDataTable(ArmorDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_EQUIP_WST.csv"


class LegDataTable(ArmorDataTable):
    def define_filepath(self):
        sep = os.path.sep
        return f"csv{sep}MHR_EQUIP_LEG.csv"


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
