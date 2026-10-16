import os

# リポジトリ直下にある暗号化JARファイルを自動検出
_dir = os.path.dirname(os.path.abspath(__file__))
_jars = [
    os.path.join(_dir, "sas.rutil.jar"),
    os.path.join(_dir, "sas.rutil.nls.jar"),
    os.path.join(_dir, "sastpj.rutil.jar"),
]
_cp = os.pathsep.join([j for j in _jars if os.path.exists(j)])

SAS_config_names = ["oda"]

oda = {
    "java": "java",
    "iomhost": "odaws01-usw2.oda.sas.com",
    "iomport": 8591,
    "authkey": "oda",
    "encoding": "utf-8",
    "classpath": _cp,
}
