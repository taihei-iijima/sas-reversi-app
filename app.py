import os
import pandas as pd
import saspy
import streamlit as st


# --- クラウド環境（Linux）向け自動初期設定 ---
def prepare_cloud_environment():
    # 認証ファイル (.authinfo) の作成
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
    else:
        st.error(
            "⚠️ Streamlit Secrets に SAS_USER または SAS_PASSWORD が設定されていません。"
        )
        st.stop()


prepare_cloud_environment()

st.set_page_config(page_title="SAS Othello AI Cockpit", layout="wide")

# ==============================================================
# オセロ盤面のカスタムCSS（行・列番号完全同期 ＆ 黒背景 ＆ 正方形立体石）
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
    gap: 0px !important;
    margin: 0px !important;
    padding: 0px !important;
}
div[data-testid="column"] {
    padding: 0px !important;
    margin: 0px !important;
    min-width: 0px !important;
}
div.stButton {
    margin: 0px !important;
    padding: 0px !important;
    width: 100% !important;
    position: relative !important;
    overflow: visible !important;
}

/* =======================================================
   2. 盤面外枠の番号用マージン確保（上32px・左32px）
======================================================= */
/* 1行目（Y=1）のマス：上に列番号用の余白を作る */
div[class*="_sq_"][class*="_1_1"],
div[class*="_sq_"][class*="_2_1"],
div[class*="_sq_"][class*="_3_1"],
div[class*="_sq_"][class*="_4_1"],
div[class*="_sq_"][class*="_5_1"],
div[class*="_sq_"][class*="_6_1"],
div[class*="_sq_"][class*="_7_1"],
div[class*="_sq_"][class*="_8_1"] {
    margin-top: 32px !important;
}

/* 1列目（X=1）のマス：左に行番号用の余白を作る */
div[class*="_sq_"][class*="_1_1"],
div[class*="_sq_"][class*="_1_2"],
div[class*="_sq_"][class*="_1_3"],
div[class*="_sq_"][class*="_1_4"],
div[class*="_sq_"][class*="_1_5"],
div[class*="_sq_"][class*="_1_6"],
div[class*="_sq_"][class*="_1_7"],
div[class*="_sq_"][class*="_1_8"] {
    margin-left: 32px !important;
}

/* =======================================================
   3. 列番号（1〜8）：1行目マスの真上に中央配置（黒背景）
======================================================= */
/* 列番号の共通スタイル */
div[class*="_sq_"][class*="_1_1"] button::before,
div[class*="_sq_"][class*="_2_1"] button::before,
div[class*="_sq_"][class*="_3_1"] button::before,
div[class*="_sq_"][class*="_4_1"] button::before,
div[class*="_sq_"][class*="_5_1"] button::before,
div[class*="_sq_"][class*="_6_1"] button::before,
div[class*="_sq_"][class*="_7_1"] button::before,
div[class*="_sq_"][class*="_8_1"] button::before {
    position: absolute !important;
    top: -28px !important;
    left: 0px !important;
    width: 100% !important;
    text-align: center !important;
    font-size: 16px !important;
    font-weight: bold !important;
    color: #e0e0e0 !important;
    background: transparent !important;
    pointer-events: none !important;
    line-height: 1 !important;
}

/* 各列の番号割り当て */
div[class*="_sq_"][class*="_1_1"] button::before { content: "1" !important; }
div[class*="_sq_"][class*="_2_1"] button::before { content: "2" !important; }
div[class*="_sq_"][class*="_3_1"] button::before { content: "3" !important; }
div[class*="_sq_"][class*="_4_1"] button::before { content: "4" !important; }
div[class*="_sq_"][class*="_5_1"] button::before { content: "5" !important; }
div[class*="_sq_"][class*="_6_1"] button::before { content: "6" !important; }
div[class*="_sq_"][class*="_7_1"] button::before { content: "7" !important; }
div[class*="_sq_"][class*="_8_1"] button::before { content: "8" !important; }

/* =======================================================
   4. 行番号（1〜8）：左端マスの左外側に縦中央配置（黒背景）
======================================================= */
/* 行番号の共通スタイル */
div[class*="_sq_"][class*="_1_1"]::before,
div[class*="_sq_"][class*="_1_2"]::before,
div[class*="_sq_"][class*="_1_3"]::before,
div[class*="_sq_"][class*="_1_4"]::before,
div[class*="_sq_"][class*="_1_5"]::before,
div[class*="_sq_"][class*="_1_6"]::before,
div[class*="_sq_"][class*="_1_7"]::before,
div[class*="_sq_"][class*="_1_8"]::before {
    position: absolute !important;
    left: -26px !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    width: 20px !important;
    text-align: center !important;
    font-size: 16px !important;
    font-weight: bold !important;
    color: #e0e0e0 !important;
    background: transparent !important;
    pointer-events: none !important;
    line-height: 1 !important;
    z-index: 10 !important;
}

/* 各行の番号割り当て */
div[class*="_sq_"][class*="_1_1"]::before { content: "1" !important; }
div[class*="_sq_"][class*="_1_2"]::before { content: "2" !important; }
div[class*="_sq_"][class*="_1_3"]::before { content: "3" !important; }
div[class*="_sq_"][class*="_1_4"]::before { content: "4" !important; }
div[class*="_sq_"][class*="_1_5"]::before { content: "5" !important; }
div[class*="_sq_"][class*="_1_6"]::before { content: "6" !important; }
div[class*="_sq_"][class*="_1_7"]::before { content: "7" !important; }
div[class*="_sq_"][class*="_1_8"]::before { content: "8" !important; }

/* =======================================================
   5. オセロ盤マス目（完全正方形・深緑・黒枠線）
======================================================= */
div[class*="_sq_"] button {
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
    overflow: visible !important;
}

div[class*="_sq_"] button:disabled {
    background-color: #1b6d2b !important;
    opacity: 1.0 !important;
    cursor: default !important;
}

/* ボタン内の元の文字は非表示にしてCSSで石を描画 */
div[class*="_sq_"] button * {
    display: none !important;
}

/* =======================================================
   6. オセロ石のリアル描画（正方形マスに連動した美しい円）
======================================================= */
div[class*="_sq_b_"] button::after,
div[class*="_sq_w_"] button::after {
    content: "" !important;
    display: block !important;
    width: 76% !important;
    height: 76% !important;
    border-radius: 50% !important;
}

/* ★ 黒石：透け感ゼロの漆黒（ハイライト ＋ 強い影） ★ */
div[class*="_sq_b_"] button::after {
    background: radial-gradient(circle at 32% 32%, #444444 0%, #151515 45%, #000000 100%) !important;
    box-shadow: 2px 3px 5px rgba(0, 0, 0, 0.85) !important;
    border: 1px solid #000000 !important;
}

/* ★ 白石：透け感ゼロの純白（陶器のような立体光沢 ＋ 影） ★ */
div[class*="_sq_w_"] button::after {
    background: radial-gradient(circle at 32% 32%, #ffffff 0%, #f0f0f0 60%, #cfcfcf 100%) !important;
    box-shadow: 2px 3px 5px rgba(0, 0, 0, 0.65) !important;
    border: 1px solid #bfbfbf !important;
}

/* =======================================================
   7. 着手可能マス（×印）
======================================================= */
div[class*="_sq_x_"] button {
    background-color: #1e7a33 !important;
    cursor: pointer !important;
    border: 1px solid #0a2e12 !important;
}
div[class*="_sq_x_"] button::after {
    content: "✖" !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 26px !important;
    color: #4a1515 !important; /* 眩しくないダークワインレッド */
    font-weight: 900 !important;
    line-height: 1 !important;
}
div[class*="_sq_x_"] button:hover {
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
        # リポジトリ直下の暗号化JARファイルを直接クラスパスに渡す
        current_dir = os.path.dirname(os.path.abspath(__file__))
        jar_names = ["sas.rutil.jar", "sas.rutil.nls.jar", "sastpj.rutil.jar"]
        extra_jars = [
            os.path.join(current_dir, j)
            for j in jar_names
            if os.path.exists(os.path.join(current_dir, j))
        ]
        cp_arg = os.pathsep.join(extra_jars) if extra_jars else None

        if cp_arg:
            st.session_state.sas = saspy.SASsession(
                cfgname="oda", classpath=cp_arg
            )
        else:
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
