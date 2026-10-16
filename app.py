import io
import logging
import os
import subprocess
import sascfg_personal
import saspy
import streamlit as st

st.set_page_config(page_title="SAS 接続診断 (詳細版)", layout="wide")
st.title("🔍 SAS Cloud 接続診断 (詳細ログ)")

# --- 1. SASPy の詳細デバッグログを画面に出力する設定 ---
log_stream = io.StringIO()
handler = logging.StreamHandler(log_stream)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)

sas_logger = logging.getLogger("saspy")
sas_logger.setLevel(logging.DEBUG)
sas_logger.addHandler(handler)

# --- 2. Java プロセス直接起動テスト (pyiom.saspy2j) ---
st.subheader("1. Java メインクラス直接実行テスト (`pyiom.saspy2j`)")
cp = sascfg_personal.oda.get("classpath", "")
cmd = ["java", "-classpath", cp, "pyiom.saspy2j", "-help"]
run_res = subprocess.run(
    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
)

st.write(f"終了コード: `{run_res.returncode}`")
if run_res.stderr:
    st.code(f"[STDERR]\n{run_res.stderr}", language="text")
if run_res.stdout:
    st.code(f"[STDOUT]\n{run_res.stdout}", language="text")

# --- 3. SASsession 接続テスト ---
st.subheader("2. SASsession 接続テスト")
with st.spinner("SASサーバーに接続テスト中..."):
    try:
        sas = saspy.SASsession(cfgname="oda")
        st.success("🎉 SASサーバーへの接続に完全に成功しました！")
        # テスト実行
        res = sas.submit("data _null_; put 'HELLO SAS CLOUD'; run;")
        st.code(res["LOG"], language="sas")
    except Exception as e:
        st.error(f"SAS接続例外: {e}")
    finally:
        # 捕捉したすべてのデバッグログを表示
        st.subheader("📋 SASPy 内部通信デバッグログ")
        debug_output = log_stream.getvalue()
        if debug_output:
            st.code(debug_output, language="text")
        else:
            st.info("デバッグログは空でした。")
