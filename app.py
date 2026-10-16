import os
import socket
import subprocess
import sascfg_personal
import streamlit as st

st.set_page_config(page_title="SAS 接続診断", layout="wide")
st.title("🔍 SAS Cloud 接続診断")

# 1. 認証情報 (.authinfo) のチェック
# まず Secrets から生成を試みる
if "SAS_USER" in st.secrets and "SAS_PASSWORD" in st.secrets:
    u = str(st.secrets["SAS_USER"]).strip()
    p = str(st.secrets["SAS_PASSWORD"]).strip()
    content = f"oda user {u} password {p}\n"
    for fname in [".authinfo", "_authinfo"]:
        p_path = os.path.expanduser(f"~/{fname}")
        try:
            with open(p_path, "w", encoding="utf-8") as f:
                f.write(content)
            os.chmod(p_path, 0o600)
        except Exception:
            pass

auth_path = os.path.expanduser("~/.authinfo")
st.subheader("1. 認証ファイル (`~/.authinfo`)")
if os.path.exists(auth_path):
    st.success("✅ `~/.authinfo` は正常に作成・配置されています。")
else:
    st.error("❌ `~/.authinfo` が存在しません。Streamlit Secrets を確認してください。")

# 2. ネットワーク疎通テスト (ポート 8591)
host = sascfg_personal.oda.get("iomhost", "odaws01-usw2.oda.sas.com")
port = sascfg_personal.oda.get("iomport", 8591)
st.subheader(f"2. ネットワーク疎通テスト ({host}:{port})")
try:
    sock = socket.create_connection((host, port), timeout=5)
    sock.close()
    st.success(
        f"✅ {host}:{port} に接続できました（ファイアウォールは通過しています）。"
    )
except Exception as net_err:
    st.error(
        f"❌ {host}:{port} への通信が遮断されています: {net_err}\n"
        "※ ODAサーバー側でクラウド事業者のIPアドレスがブロックされている可能性があります。"
    )

# 3. クラスパス・JARファイルの検証
cp = sascfg_personal.oda.get("classpath", "")
jar_list = cp.split(os.pathsep) if cp else []
st.subheader(f"3. JARファイルの検出 (合計 {len(jar_list)} 個)")
missing = [j for j in jar_list if not os.path.exists(j)]
if not cp:
    st.error("❌ クラスパスが空です。`sascfg_personal.py` を確認してください。")
elif missing:
    st.error(f"❌ 以下のJARファイルが見つかりません:\n{missing}")
else:
    st.success("✅ クラスパスに指定された全JARファイルが正常に存在します。")

# 4. Java プロセス直接起動テスト (pyiom.saspyiom)
st.subheader("4. Java プロセス直接起動テスト")
cmd = ["java", "-classpath", cp, "pyiom.saspyiom"]
run_res = subprocess.run(
    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)

st.write(f"終了コード (Return Code): `{run_res.returncode}`")
if run_res.stderr:
    st.error("⚠️ Java が以下のエラーを出力しました:")
    st.code(run_res.stderr, language="text")
if run_res.stdout:
    st.info("ℹ️ Java の標準出力:")
    st.code(run_res.stdout, language="text")
if not run_res.stderr and not run_res.stdout:
    st.warning("Javaからの出力はありませんでした。")
