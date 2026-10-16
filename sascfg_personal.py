import glob
import os
import saspy

# 1. saspy/java フォルダ配下にある全JAR（saspyiom.jar、CORBA、通信用等）を再帰的に全取得
_saspy_dir = os.path.dirname(saspy.__file__)
_java_dir = os.path.join(_saspy_dir, "java")
_default_jars = glob.glob(
    os.path.join(_java_dir, "**", "*.jar"), recursive=True
)

# 2. リポジトリ直下の暗号化JAR（3つ）を取得
_repo_dir = os.path.dirname(os.path.abspath(__file__))
_extra_jar_names = ["sas.rutil.jar", "sas.rutil.nls.jar", "sastpj.rutil.jar"]
_extra_jars = [
    os.path.join(_repo_dir, j)
    for j in _extra_jar_names
    if os.path.exists(os.path.join(_repo_dir, j))
]

# 3. すべてを重複なく連結して完全なクラスパスを生成
_all_jars = list(set(_default_jars + _extra_jars))
_full_classpath = os.pathsep.join(_all_jars)

SAS_config_names = ["oda"]

oda = {
    "java": "java",
    "iomhost": "odaws01-usw2.oda.sas.com",
    "iomport": 8591,
    "authkey": "oda",
    "encoding": "utf-8",
    "classpath": _full_classpath,
}
