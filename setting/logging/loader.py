# -*- coding: utf-8 -*-
import io
import os
import yaml
import json


class YamlLoader(object):
    """
    YAML 로더
    """

    @classmethod
    def load(cls, path):
        with open(path, 'r') as f:
            return yaml.safe_load(f.read())


class JsonLoader(object):
    """
    Json 로더
    """

    @classmethod
    def load(cls, path):
        # io.open 에서 encoding 지원
        with io.open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
