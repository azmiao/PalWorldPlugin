import json
from typing import List


class PalChar:
    def __init__(self, pal_id: str, number: int, en_name: str, cn_name: str, power: int, alias: List[str]):
        self.pal_id = pal_id
        self.number = number
        self.en_name = en_name
        self.cn_name = cn_name
        self.power = power
        self.alias = alias

    def to_json(self):
        return json.dumps({
            "pal_id": self.pal_id,
            "number": self.number,
            "en_name": self.en_name,
            "cn_name": self.cn_name,
            "power": self.power,
            "alias": self.alias
        })
