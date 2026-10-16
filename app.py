import os
import urllib.request
import pandas as pd
import saspy
import streamlit as st


# --- クラウド環境（Linux）向け自動初期設定 ---
def prepare_cloud_environment():
    # 1. 暗号化通信用JARファイルが存在しない場合、自動ダウンロード
    jar_dir = os.path.join(os.path.dirname(saspy.__file__), "java", "iomclient")
    jars = ["sas.rutil.jar", "sas.rutil.nls.jar", "sastpj.rutil.jar"]
    for j in jars:
        j_path = os.path.join(jar_dir, j)
        if not os.path.exists(j_path):
            try:
                url = f"http://ftp.sas.com/techsup/download/base/{j}"
                urllib.request.urlretrieve(url, j_path)
            except Exception as e:
                print(f"JAR download error for {j}: {e}")

    # 2. クラウドの秘密設定(Secrets)から認証ファイルを生成
    # ※ Linux環境用に .authinfo (ドット)、Windows用に _authinfo の両方を作成
    if "SAS_USER" in st.secrets and "SAS_PASSWORD" in st.secrets:
        sas_user = str(st.secrets["SAS_USER"]).strip()
        sas_pw = str(st.secrets["SAS_PASSWORD"]).strip()
        auth_content = f"oda user {sas_user} password {sas_pw}\n"

        for filename in [".authinfo", "_authinfo"]:
            path = os.path.expanduser(f"~/{filename}")
            with open(path, "w", encoding="utf-8") as f:
                f.write(auth_content)
            # Linux必須: 権限を「所有者のみ読み書き可(600)」に設定
            try:
                os.chmod(path, 0o600)
            except Exception:
                pass
    else:
        st.error(
            "⚠️ Streamlit Secrets に SAS_USER または SAS_PASSWORD が設定されていません！"
        )
        st.info("右下の Manage app → 3点リーダー → Settings → Secrets を確認してください。")
        st.stop()


prepare_cloud_environment()

st.set_page_config(page_title="SAS Othello AI Cockpit", layout="wide")
# （これ以降のコードはそのまま）
# ==============================================================
# オセロ盤面のカスタムCSS（列番号・行番号 完全中央同期 ＆ 正方形立体石）
# ==============================================================
st.markdown(
    """
<style>
/* 1. 縦横の隙間（余白・ギャップ）を完全にゼロにする */
div[data-testid="stVerticalBlock"] {
    gap: 0px !important;
}
div[data-testid="stVerticalBlock"] > div {
    margin: 0px !important;
    padding: 0px !important;
    gap: 0px !important;
}
div[data-testid="stHorizontalBlock"] {
    display: flex !important;
    align-items: stretch !important;
    gap: 0px !important;
    margin: 0px !important;
    padding: 0px !important;
}
div.stButton {
    margin: 0px !important;
    padding: 0px !important;
    width: 100% !important;
    height: 100% !important;
}

/* =======================================================
   2. ★ 盤面・列番号行の9カラム幅を完全固定（位置ズレ根本解消） ★
======================================================= */
/* 9つのカラムを持つ行（上段の列番号 ＋ 盤面8行）のみを特定して幅を完全同期 */
div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(9)) {
    width: 100% !important;
}

/* 左端カラム（角の空白セル ＆ 行番号1〜8）：幅 6.98% に完全固定 */
div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(9)) > div[data-testid="column"]:first-child {
    flex: 0 0 6.98% !important;
    width: 6.98% !important;
    max-width: 6.98% !important;
    min-width: 6.98% !important;
    padding: 0px !important;
    margin: 0px !important;
}

/* 2〜9列目カラム（列番号1〜8 ＆ オセロ盤マス）：幅 11.6275% に完全固定 */
div[data-testid="stHorizontalBlock"]:has(> div[data-testid="column"]:nth-child(9)) > div[data-testid="column"]:not(:first-child) {
    flex: 0 0 11.6275% !important;
    width: 11.6275% !important;
    max-width: 11.6275% !important;
    min-width: 11.6275% !important;
    padding: 0px !important;
    margin: 0px !important;
}

/* =======================================================
   3. 行番号・列番号（背景を完全な黒・透明にし、中央配置）
======================================================= */
div[class*="st-key-col_num_"] button,
div[class*="st-key-col_num_"] button:disabled,
div[class*="st-key-row_num_"] button,
div[class*="st-key-row_num_"] button:disabled,
div[class*="st-key-corner_cell"] button,
div[class*="st-key-corner_cell"] button:disabled {
    background: transparent !important;
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
    border-radius: 0px !important;
    opacity: 1.0 !important;
    cursor: default !important;
    width: 100% !important;
    padding: 0px !important;
    margin: 0px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    text-align: center !important;
}

/* 数字フォント（白く鮮明にし、余計なマージンを排除して完全中央揃え） */
div[class*="st-key-col_num_"] button *,
div[class*="st-key-row_num_"] button * {
    color: #e0e0e0 !important;
    font-size: 16px !important;
    font-weight: bold !important;
    background: transparent !important;
    opacity: 1.0 !important;
    line-height: 1 !important;
    margin: 0px auto !important;
    padding: 0px !important;
    text-align: center !important;
}

/* 上段：列番号（1〜8）上部マージンを確保 */
div[class*="st-key-col_num_"],
div[class*="st-key-corner_cell"] {
    height: 36px !important;
    margin-top: 14px !important;
    margin-bottom: 2px !important;
}
div[class*="st-key-col_num_"] button,
div[class*="st-key-corner_cell"] button {
    height: 36px !important;
    min-height: 36px !important;
}

/* 左端：行番号（1〜8）マスの高さに同期して中央配置 */
div[class*="st-key-row_num_"] {
    height: 100% !important;
}
div[class*="st-key-row_num_"] button {
    height: 100% !important;
    min-height: 100% !important;
}

/* =======================================================
   4. オセロ盤のマス目（盤面ボタンのみに緑色・黒枠線を適用）
======================================================= */
div[class*="st-key-b_"] button,
div[class*="st-key-w_"] button,
div[class*="st-key-x_"] button,
div[class*="st-key-e_"] button {
    background-color: #1b6d2b !important; /* オセロ盤の深緑 */
    border: 1px solid #0a2e12 !important; /* マスの境界線 */
    border-radius: 0px !important;
    width: 100% !important;
    aspect-ratio: 1 / 1 !important;        /* 縦横比 1:1 に完全固定 */
    height: auto !important;
    min-height: 0px !important;
    padding: 0px !important;
    margin: 0px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    position: relative !important;
}

div[class*="st-key-b_"] button:disabled,
div[class*="st-key-w_"] button:disabled,
div[class*="st-key-e_"] button:disabled {
    background-color: #1b6d2b !important;
    opacity: 1.0 !important;
    cursor: default !important;
}

/* 元の文字は非表示にしてCSSで石を描画 */
div[class*="st-key-b_"] button *,
div[class*="st-key-w_"] button *,
div[class*="st-key-e_"] button * {
    display: none !important;
}

/* =======================================================
   5. オセロ石のリアル描画（正方形マスに連動した美しい円）
======================================================= */
div[class*="st-key-b_"] button::after,
div[class*="st-key-w_"] button::after {
    content: "" !important;
    display: block !important;
    width: 76% !important;
    height: 76% !important;
    border-radius: 50% !important;
}

/* ★ 黒石：透け感ゼロの漆黒（ハイライト ＋ 強い影） ★ */
div[class*="st-key-b_"] button::after {
    background: radial-gradient(circle at 32% 32%, #444444 0%, #151515 45%, #000000 100%) !important;
    box-shadow: 2px 3px 5px rgba(0, 0, 0, 0.85) !important;
    border: 1px solid #000000 !important;
}

/* ★ 白石：透け感ゼロの純白（陶器のような立体光沢 ＋ 影） ★ */
div[class*="st-key-w_"] button::after {
    background: radial-gradient(circle at 32% 32%, #ffffff 0%, #f0f0f0 60%, #cfcfcf 100%) !important;
    box-shadow: 2px 3px 5px rgba(0, 0, 0, 0.65) !important;
    border: 1px solid #bfbfbf !important;
}

/* =======================================================
   6. 着手可能マス（×印）
======================================================= */
div[class*="st-key-x_"] button {
    background-color: #1e7a33 !important;
    cursor: pointer !important;
    border: 1px solid #0a2e12 !important;
}
div[class*="st-key-x_"] button * {
    font-size: 26px !important;
    color: #4a1515 !important; /* 眩しくないダークワインレッド */
    font-weight: 900 !important;
    line-height: 1 !important;
}
div[class*="st-key-x_"] button:hover {
    background-color: #249641 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


st.title("SAS Othello AI Cockpit (PvE)")
st.markdown(
    "SASのDATAステップとマクロによるミニマックス探索AIが裏で稼働しています。"
)

# --- 1. SASセッションの初期化・保持 ---
if "sas" not in st.session_state:
    with st.spinner("SASサーバーに接続中..."):
        st.session_state.sas = saspy.SASsession(cfgname="oda")
        st.session_state.log = "ここにSASの実行ログが表示されます。"
        st.session_state.df_info = None


# --- 2. 盤面データ取得関数 ---
def fetch_board():
    try:
        df = st.session_state.sas.sasdata2dataframe(table="_INFO", libref="WORK")
        if df is not None and not df.empty:
            df.columns = [str(c).upper() for c in df.columns]
            if "Y" in df.columns:
                st.session_state.df_info = df.sort_values(by="Y").reset_index(
                    drop=True
                )
            else:
                st.error(
                    f"WORK._INFO に 'Y' 列が見つかりません。現在の列: {list(df.columns)}"
                )
        else:
            st.warning("WORK._INFO データセットが空です。")
    except Exception as e:
        st.error(f"データセット取得エラー: {e}")


# --- 3. SAS実行関数 ---
def init_game():
    code = """
    %symdel init_done _xy _black _white / nowarn;
    %inc "/home/u63429059/sas_2026_Othello/macro_PvE.sas";
    %inc "/home/u63429059/sas_2026_Othello/IIJIMTA2.sas";
    %let _m1 = player;
    %let _m2 = IIJIMTA2;
    %make_first;
    %make_xy_com;
    """
    res = st.session_state.sas.submit(code)
    st.session_state.log = res["LOG"]
    fetch_board()


def make_move(x, y):
    code = f"""
    %let _xy = {x},{y};
    %make_next;
    %make_xy_com;
    """
    res = st.session_state.sas.submit(code)
    st.session_state.log = res["LOG"]
    fetch_board()


# --- 4. UIレイアウト ---
col1, col2 = st.columns([1.1, 1.2])

with col1:
    st.subheader("🎮 対戦ボード")

    if st.button("🔄 新規対局開始 (マクロ再読み込み)", type="primary"):
        with st.spinner("SASマクロ初期化・初手生成中..."):
            init_game()
            st.rerun()

    df = st.session_state.df_info
    if df is not None and not df.empty:
        turn = df.loc[0, "TURN"] if "TURN" in df.columns else None
        no_val = df.loc[0, "NO"] if "NO" in df.columns else ""
        turn_str = "● 黒の手番" if turn == -1 else "○ 白の手番"
        st.markdown(f"**手番:** {turn_str} ｜ **手数 (No):** {no_val}")

        # 左端ラベル列 (0.6) ＋ 盤面8列 (1.0 × 8)
        col_ratios = [0.6, 1, 1, 1, 1, 1, 1, 1, 1]

        # --- 上段：列番号 (X座標: 1〜8) ---
        h_cols = st.columns(col_ratios)
        h_cols[0].button(" ", key="corner_cell", disabled=True)
        for c in range(8):
            h_cols[c + 1].button(
                f"{c + 1}", key=f"col_num_{c + 1}", disabled=True
            )

        # --- 盤面行：左端に行番号 (Y座標: 1〜8) ＋ マス目 ---
        for r in range(8):
            cols = st.columns(col_ratios)
            y_coord = r + 1

            # 行番号ボタン
            cols[0].button(f"{y_coord}", key=f"row_num_{y_coord}", disabled=True)

            row_data = df.iloc[r]
            for c in range(8):
                val = row_data.get(f"X{c+1}", 0)
                x_coord = c + 1

                if val == -1:  # 黒石
                    cols[c + 1].button(
                        "●",
                        key=f"b_{x_coord}_{y_coord}",
                        disabled=True,
                        use_container_width=True,
                    )
                elif val == 1:  # 白石
                    cols[c + 1].button(
                        "○",
                        key=f"w_{x_coord}_{y_coord}",
                        disabled=True,
                        use_container_width=True,
                    )
                elif val == 99:  # 着手可能
                    cols[c + 1].button(
                        "✖",
                        key=f"x_{x_coord}_{y_coord}",
                        on_click=make_move,
                        args=(x_coord, y_coord),
                        use_container_width=True,
                    )
                else:  # 空きマス
                    cols[c + 1].button(
                        " ",
                        key=f"e_{x_coord}_{y_coord}",
                        disabled=True,
                        use_container_width=True,
                    )

        x_cols = [f"X{i}" for i in range(1, 9) if f"X{i}" in df.columns]
        if not (df[x_cols] == 99).any().any():
            st.info("着手可能マスがありません。パスまたはゲーム終了です。")
    else:
        st.info(
            "上の「🔄 新規対局開始」ボタンを押して対局を開始してください。"
        )

with col2:
    st.subheader("💻 SAS エンジンモニタ")
    tab1, tab2, tab3 = st.tabs(
        [
            "実行ログ (LOG)",
            "盤面データセット (WORK._INFO)",
            "評価値推移 (SCORED)",
        ]
    )

    with tab1:
        st.caption("AI思考時に出力されたSASログです。")
        st.text_area("SAS Log", st.session_state.log, height=450)

    with tab2:
        st.caption(
            "現在メモリ上に保持されている WORK._INFO データセットです。"
        )
        if df is not None:
            st.dataframe(df, use_container_width=True)

    with tab3:
        st.caption("AIのミニマックス探索結果（SCOREDデータセット）です。")
        try:
            df_scored = st.session_state.sas.sasdata2dataframe(
                table="SCORED1", libref="WORK"
            )
            if df_scored is not None and not df_scored.empty:
                st.dataframe(df_scored, use_container_width=True)
            else:
                st.text("評価値データはまだありません。")
        except:
            st.text("評価値データセットの取得をスキップしました。")
