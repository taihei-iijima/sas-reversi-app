import glob
import os
import saspy

# 1. saspy標準の iomclient 内にある全JARファイルを取得
_iom_dir = os.path.join(os.path.dirname(saspy.__file__), "java", "iomclient")
_default_jars = glob.glob(os.path.join(_iom_dir, "*.jar"))

# 2. リポジトリ直下に置いた3つの暗号化JARファイルを取得
_repo_dir = os.path.dirname(os.path.abspath(__file__))
_extra_jar_names = ["sas.rutil.jar", "sas.rutil.nls.jar", "sastpj.rutil.jar"]
_extra_jars = [
    os.path.join(_repo_dir, j)
    for j in _extra_jar_names
    if os.path.exists(os.path.join(_repo_dir, j))
]

# 3. すべてを合体させた完全なクラスパスを作成
_all_jars = _default_jars + _extra_jars
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
