import io
import logging
import os
import saspy
import streamlit as st

st.set_page_config(page_title="SAS 接続テスト", layout="wide")
st.title("SAS Cloud 接続テスト")

# SASPy のデバッグログをキャプチャする設定
log_stream = io.StringIO()
handler = logging.StreamHandler(log_stream)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(levelname)s: %(message)s")
handler.setFormatter(formatter)

sas_logger = logging.getLogger("saspy")
sas_logger.setLevel(logging.DEBUG)
sas_logger.addHandler(handler)

with st.spinner("SASサーバーに直接認証で接続テスト中..."):
    try:
        cfg_file_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "sascfg_personal.py"
        )
        sas_u = str(st.secrets["SAS_USER"]).strip()
        sas_p = str(st.secrets["SAS_PASSWORD"]).strip()

        # Streamlit Secrets の認証情報を使って直接ログイン
        sas = saspy.SASsession(
            cfgfile=cfg_file_path,
            cfgname="oda",
            omruser=sas_u,
            omrpw=sas_p,
            results="TEXT",
        )

        st.success("🎉 SASサーバーへの接続に完全に成功しました！")

        # 疎通確認のためのテストクエリ実行
        res = sas.submit("data _null_; put 'HELLO SAS CLOUD SUCCESS!'; run;")
        st.subheader("SAS 実行ログ (LOG)")
        st.code(res["LOG"], language="sas")

    except Exception as e:
        st.error(f"SAS接続例外: {e}")
        st.subheader("📋 内部デバッグログ")
        st.code(log_stream.getvalue(), language="text")
