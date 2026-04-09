import os
import pymysql
import pandas as pd
from pandas import DataFrame
from pandas import Series
import numpy as np
# import sidetable
import math
from PIL import Image
import streamlit as st
import base64

# from google.colab import data_table
# from vega_datasets import data

import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import requests
from io import BytesIO

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

import plotly.offline as pyo
# import plotly.plotly as py

from stats import safe_divide, create_batter_stats, create_pitcher_stats, create_series_stats, BattingConfig, PitchConfig, DesConfig, EventsConfig, TeamConfig, DesConfigENG



pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)


os.environ["REQUESTS_CA_BUNDLE"] = r"D:\JEON\CA.crt"


# GitHub 정보
OWNER = "Henryjeon1"
REPO = "ktdata"
TAG_NAME = "KoreaBaseballOrganization"
RELEASE_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/releases/tags/{TAG_NAME}"


label_to_filename = {
    "1군": "KoreaBaseballOrganization.parquet",
    "2군": "Minor.parquet",
    "AAA": "AAA.parquet",
    "NPB": "NPB.parquet"
}
filename_to_label = {v: k for k, v in label_to_filename.items()}
labels = list(label_to_filename.keys())

st.set_page_config(
    layout="wide"  # 기본은 "centered", "wide"로 하면 폭 넓어짐
)


st.markdown("""
    <style>
    /* 1. 메인 컨테이너 및 헤더 설정 (기존 수치 유지) */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    [data-testid="stAppViewBlockContainer"] {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
    }
    [data-testid="stHeader"], header {
        background: transparent !important;
    }
    h2 {
        padding-top: 0rem !important;
        margin-top: -30px !important; 
        margin-bottom: 5px !important;
    }

    /* 2. 타이틀 바 공유 스타일 (규격 통일, 패딩 6px 10px 유지) */
    .pink-title-bar, .gray-title-bar, .darkgray-title-bar {
        padding: 6px 10px !important;
        border-radius: 10px 10px 0 0;
        font-weight: bold;
        line-height: 1.4;
        font-size: 11px;
        width: 100%;
        box-sizing: border-box;
        margin-bottom: 0px !important;
    }
    /* 타이틀 바 개별 색상 및 테두리 */
    .pink-title-bar { background-color: #FFF0F5; border: 1px solid #FFD1DC; border-bottom: none; }
    .gray-title-bar { background-color: #F8F9FA; border: 1px solid #E9ECEF; border-bottom: none; }
    .darkgray-title-bar { background-color: #E9ECEF; border: 1px solid #CED4DA; border-bottom: none; }

    /* 3. 타이틀과 그래프 사이 간격 (가장 최근 설정 수치인 -8px로 통합) */
    [data-testid="stVerticalBlock"] > div:has(.pink-title-bar) + div,
    [data-testid="stVerticalBlock"] > div:has(.gray-title-bar) + div,
    [data-testid="stVerticalBlock"] > div:has(.darkgray-title-bar) + div {
        margin-top: -8px !important; /* 더 바짝 밀착 */
    }
    
    /* 4. 기타 레이아웃 및 테이블 스타일 */
    [data-testid="column"] {
        padding-left: 2px !important;
        padding-right: 2px !important;
    }
    .darkgray-analysis-box {
        background-color: #E9ECEF;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #CED4DA;
        height: 100%;
        line-height: 1.5; /* 분석 텍스트용 여백 */
    }
    .dense-table {
        width: 100%;
        font-size: 11px;
        border-collapse: collapse;
        margin: 10px 0;
        font-family: sans-serif;
    }
    .dense-table th {
        background-color: #f8f9fa;
        color: #333;
        font-weight: bold;
        padding: 4px 2px !important;
        border: 1px solid #dee2e6;
        text-align: center;
    }
    .dense-table td {
        padding: 3px 2px !important;
        border: 1px solid #dee2e6;
        text-align: center;
        white-space: nowrap;
    }
    .dense-table tr:hover {
        background-color: #f1f3f5;
    }

    @media print {
        section[data-testid="stSidebar"] { display: none !important; }
        .main { margin-left: 0 !important; overflow: visible !important; }
        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important; /* 👈 기존 1cm에서 0으로 변경: 상하좌우 모든 여백 제거 */
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        [data-testid="stAppViewBlockContainer"] {
            padding-top: 0 !important;
            padding-bottom: 0 !important;
        }
        header, [data-testid="stHeader"], footer, [data-testid="stStatusWidget"], [data-testid="stDecoration"] {
            display: none !important;
        }
        html, body, .stApp { height: auto !important; margin: 0 !important; padding: 0 !important; }
        div[data-testid="stVerticalBlock"] > div:last-child {
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)


with st.sidebar:
    st.header("🔍 필터 조건")
    selected_labels = st.multiselect("📁 리그 선택", labels, default=[])
    run_button = st.button("실행")
    FILE_NAMES = [label_to_filename[label] for label in selected_labels]

    if run_button:
        if not FILE_NAMES:
            st.warning("⚠️ 하나 이상의 리그를 선택하세요.")
        else:
            response = requests.get(RELEASE_URL)
            dfs = []

            if response.status_code == 200:
                release_data = response.json()
                assets = release_data.get("assets", [])
                target_assets = [a for a in assets if a["name"] in FILE_NAMES]

                with requests.Session() as session:
                    session.headers.update({
                        "Accept": "application/octet-stream"
                    })

                    for asset in target_assets:
                        asset_url = asset["url"]
                        res = session.get(asset_url)

                        if res.status_code == 200:
                            try:
                                df = pd.read_parquet(BytesIO(res.content), engine="pyarrow")
                                dfs.append(df)
                            except Exception as e:
                                st.error(f"❌ {asset['name']} 파싱 실패: {e}")
                        else:
                            st.error(f"❌ 다운로드 실패: {res.status_code} {res.text}")

                if dfs:
                    df = pd.concat(dfs, ignore_index=True)
                    st.session_state["df"] = df
                    st.session_state["data_loaded"] = True

                    # 필터 상태 초기화
                    st.session_state["selected_game_year"] = []
                    st.session_state["selected_batterteam"] = []
                    st.session_state["selected_players"] = []
                    st.session_state["filter_applied"] = False

                    # 임시 입력 초기화
                    st.session_state["temp_game_year"] = []
                    st.session_state["temp_batterteam"] = []
                    st.session_state["temp_players"] = []
                else:
                    st.warning("⚠️ 불러온 데이터가 없습니다.")
            else:
                st.error(f"❌ 릴리스 조회 실패: {response.status_code}")

    if st.session_state.get("data_loaded", False) and "df" in st.session_state:
        df = st.session_state["df"]

        # 날짜 컬럼 datetime 변환
        if not pd.api.types.is_datetime64_any_dtype(df["game_date"]):
            df["game_date"] = pd.to_datetime(df["game_date"])

        # 연도 선택
        years = sorted(df["game_year"].unique())

        st.multiselect(
            "📅 연도 선택",
            options=["전체"] + years,
            default=[],
            key="temp_game_year"
        )

        if "전체" in st.session_state["temp_game_year"] or not st.session_state["temp_game_year"]:
            filtered_year_df = df
        else:
            filtered_year_df = df[df["game_year"].isin(st.session_state["temp_game_year"])]

        # ------------------------
        # 날짜 선택 (여기 추가)
        # ------------------------

        min_date = filtered_year_df["game_date"].min()
        max_date = filtered_year_df["game_date"].max()

        st.date_input(
            "📅 날짜 범위",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="temp_game_date"
        )

        date_range = st.session_state["temp_game_date"]

        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_year_df = filtered_year_df[
                (filtered_year_df["game_date"] >= pd.to_datetime(start_date)) &
                (filtered_year_df["game_date"] <= pd.to_datetime(end_date))
            ]

        # ------------------------
        # 팀 선택 (한글 매핑 적용)
        # ------------------------

        teams = sorted(filtered_year_df["batterteam"].dropna().unique())

        temp_batterteam = st.multiselect(
            "⚾ 소속 팀 선택",
            options=["전체"] + teams,
            default=[],
            format_func=lambda x: TeamConfig.TEAM_NAME_MAP.get(x, x),
            key="temp_batterteam"
        )

        if "전체" in temp_batterteam or not temp_batterteam:
            filtered_team_df = filtered_year_df
        else:
            filtered_team_df = filtered_year_df[
                filtered_year_df["batterteam"].isin(temp_batterteam)
            ]

        # ------------------------
        # 상대 팀 선택 (신규 추가)
        # ------------------------

        opp_teams = sorted(filtered_year_df["pitcherteam"].dropna().unique())

        temp_pitcherteam = st.multiselect(
            "🔥 상대 팀 선택",
            options=["전체"] + opp_teams,
            default=[],
            format_func=lambda x: TeamConfig.TEAM_NAME_MAP.get(x, x),
            key="temp_pitcherteam"
        )

        if "전체" in temp_pitcherteam or not temp_pitcherteam:
            filtered_team_df = filtered_team_df # 변화 없음
        else:
            filtered_team_df = filtered_team_df[
                filtered_team_df["pitcherteam"].isin(temp_pitcherteam)
            ]

        # ------------------------
        # 선수 선택
        # ------------------------

        players = sorted(filtered_team_df["NAME_batter"].dropna().unique())

        st.multiselect(
            "✅ 선수 선택",
            options=players,
            default=[],
            key="temp_players"
        )

        apply_filter = st.button("🔍 필터 적용")

        if apply_filter:
            selected_players = st.session_state.get("temp_players", [])
            if len(selected_players) == 0:
                st.warning("⚠️ 최소 1명의 선수를 선택하세요.")
            else:
                st.session_state["selected_game_year"] = st.session_state.get("temp_game_year")
                st.session_state["selected_batterteam"] = st.session_state.get("temp_batterteam")
                st.session_state["selected_pitcherteam"] = st.session_state.get("temp_pitcherteam")
                st.session_state["selected_players"] = selected_players
                st.session_state["selected_game_date"] = st.session_state.get("temp_game_date")
                st.session_state["filter_applied"] = True

    else:
        st.info("리그를 먼저 선택하세요.")
        st.multiselect("📅 연도 선택", options=[], disabled=True)
        st.multiselect("📅 날짜 선택", options=[], disabled=True)
        st.multiselect("⚾ 팀 선택", options=[], disabled=True)
        st.multiselect("✅ 선수 선택", [], disabled=True)
        

if st.session_state.get("data_loaded", False):
    if st.session_state.get("data_loaded", False) and st.session_state.get("filter_applied", False):
        if st.session_state.get("filter_applied", False):
            # --- [인쇄 버튼 배치] ---
            # 💡 리포트 제목 바로 위에 두어 접근성을 높입니다.
            # col_title, col_print = st.columns([4, 1])
            # with col_title:
            #     st.title("타자 분석 리포트")
            # with col_print:
            #     # JavaScript를 실행하는 버튼
            #     if st.button("🖨️ PDF 저장/인쇄"):
            #         st.components.v1.html(
            #             "<script>window.parent.focus(); window.parent.print();</script>",
            #             height=0
            #      )
        # ------------------------

            df = st.session_state["df"]
            filtered_df = df.copy()
            filtered_df_without_year = df.copy()  # 연도 필터 제외 버전

            # 1. 연도 필터 (filtered_df만 적용)
            sel_year = st.session_state.get("selected_game_year")
            if sel_year and "전체" not in sel_year:
                filtered_df = filtered_df[filtered_df["game_year"].isin(sel_year)]

            # 날짜 필터
            sel_date = st.session_state.get("selected_game_date")

            if sel_date and len(sel_date) == 2:
                start_date, end_date = sel_date
                filtered_df = filtered_df[
                    (filtered_df["game_date"] >= pd.to_datetime(start_date)) &
                    (filtered_df["game_date"] <= pd.to_datetime(end_date))
                ]

            # 2. 팀 필터 (두 데이터프레임 모두 적용)
            sel_team = st.session_state.get("selected_batterteam")
            if sel_team and "전체" not in sel_team:
                filtered_df = filtered_df[filtered_df["batterteam"].isin(sel_team)]
                

            # 2-1. 상대팀 필터 (신규 적용)
            sel_opp_team = st.session_state.get("selected_pitcherteam")
            if sel_opp_team and "전체" not in sel_opp_team:
                filtered_df = filtered_df[filtered_df["pitcherteam"].isin(sel_opp_team)]
                

            # 3. 선수 필터 (두 데이터프레임 모두 적용)
            sel_players = st.session_state.get("selected_players", [])
            if sel_players and "전체" not in sel_players:
                filtered_df = filtered_df[filtered_df["NAME_batter"].isin(sel_players)]
                filtered_df_without_year = filtered_df_without_year[filtered_df_without_year["NAME_batter"].isin(sel_players)]


            # ⚠️ 예외 처리: 필터 결과가 없을 경우
            if filtered_df.empty:
                st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
            else:
                # 그룹화
                grouped = filtered_df.groupby(["batter", "NAME_batter"])
                grouped_full = filtered_df_without_year.groupby(["batter", "NAME_batter"])  # 연도 제외 전체 기준

                # 2. [추가] 스윙을 시도한(swing == 1) 데이터만 따로 추출하여 그룹화
                swing_df = filtered_df[filtered_df["swing"] == 1].copy()
                
                grouped_swing = swing_df.groupby(["batter", "NAME_batter"])


                looking_df = filtered_df[filtered_df["swing"] != 1].copy()
                grouped_looking = looking_df.groupby(["batter", "NAME_batter"])
                # 선수명 기준 정렬
                sorted_keys = sorted(grouped.groups.keys(), key=lambda x: x[1])
                
                # 기존 for group_keys in sorted_keys: 부분을 아래처럼 변경
                for idx, group_keys in enumerate(sorted_keys):
                    batter, player_name = group_keys
                    group_df = grouped.get_group(group_keys)
                    group_df_full = grouped_full.get_group(group_keys)  # 시즌 전체 기준
                    
                    # 3. [추가] 해당 선수의 스윙 데이터만 가져오기 (예외처리 포함)
                    try:
                        group_df_swing = grouped_swing.get_group(group_keys)
                    except KeyError:
                        # 이 선수가 해당 기간에 스윙을 한 번도 안 했을 경우 빈 데이터프레임 생성
                        group_df_swing = pd.DataFrame(columns=filtered_df.columns)
                        
                    
                    # 4. [추가] 해당 선수의 루킹 데이터만 가져오기 (예외처리 포함)
                    try:
                        group_df_looking = grouped_looking.get_group(group_keys)
                    except KeyError:
                        # 이 선수가 해당 기간에 루킹을 한 번도 안 했을 경우 빈 데이터프레임 생성
                        group_df_looking = pd.DataFrame(columns=filtered_df.columns)


                    # ---------------------------------------------------------
                    # 1. 페이지 줄바꿈: 0번째(첫 선수)가 아닐 때만 실행
                    # ---------------------------------------------------------
                    if idx == 0:
                        # 첫 번째 선수는 페이지 넘김이 없으므로 상단 여백만 살짝 줍니다.
                        st.markdown('<div style="padding-top: 5px;"></div>', unsafe_allow_html=True)
                    else:
                        # 두 번째 선수부터는 페이지를 넘기고 여백을 줍니다.
                        st.markdown("""
                            <div style="page-break-before: always; height: 0px; margin: 0; padding: 0;"></div>
                            <div style="padding-top: 30px;"></div> 
                        """, unsafe_allow_html=True)

                    # ---------------------------------------------------------
                    # 2. 선수별 리포트 시작 (제목 및 정보)
                    # ---------------------------------------------------------
                    date_range_text = f"{start_date} ~ {end_date}"
                    # st.header(f"{player_name}")
                    # 상대팀 표시 문구 생성
                    sel_opp = st.session_state.get("selected_pitcherteam", [])
                    if not sel_opp or "전체" in sel_opp:
                        opp_display = "전체"
                    else:
                        opp_display = ", ".join([TeamConfig.TEAM_NAME_MAP.get(t, t) for t in sel_opp])

                    st.markdown(f"""
                        <div style='display: flex; align-items: baseline; margin-top: 10px; margin-bottom: 10px;'>
                            <h2 style='margin: 0; padding: 0;'>{player_name}</h2>
                            <span style='margin-left: 11px; color: gray; font-size: 0.9rem;'>{start_date} ~ {end_date}  VS {opp_display} </span>
                        </div>
                        """, unsafe_allow_html=True)

                    # 최근 3시즌만 선택 등 기존 로직 진행...
                    latest_year = group_df_full["game_year"].max()
                    season_df = group_df_full[
                        group_df_full["game_year"] >= latest_year - 2
                    ]
                    season = create_series_stats(season_df, {'game_year': '시즌'})

                    # 1. 최근 3개 시즌 데이터 준비
                    season = create_series_stats(season_df, {'game_year': '시즌'})
                    season_styled = season.reset_index().rename(columns={'game_year': '시즌', 'index': '시즌'})
                    season_styled = season_styled.sort_values('시즌', ascending=True)
                    
                    # 2. 이번 시리즈(3연전) 데이터 준비
                    pitch_name = create_series_stats(group_df, {'game_year': '시즌'})
                    pitch_name_styled = pitch_name.reset_index()
                    pitch_name_styled['game_year'] = '3연전'
                    pitch_name_styled = pitch_name_styled.rename(columns={'game_year': '시즌', 'index': '시즌'})

                    # 3. 두 데이터 표 합치기
                    combined_stats = pd.concat([season_styled, pitch_name_styled], ignore_index=True)

                    # 4. 컬럼명 최종 한글화
                    combined_stats = combined_stats.rename(columns={
                        'exit_velocity': '타구속도',
                        'launch_angleX': '발사각도',
                        'ev50': 'EV50',
                        'z%': '존%',
                        'z_swing%': '존스윙%',
                        'z_con%': '존컨택%',
                        'o%': '외부%',
                        'o_swing%': '외부스윙%',
                        'o_con%': '외부컨택%',
                        'f_swing%': '초구스윙%',
                        'swing%': '스윙%',
                        'whiff%': '헛스윙%',
                        'inplay_sw': '인플레이%',
                        'solid_contact' : 'solid'
                    })

                    # 고밀도 테이블로 출력 (3연전 행 상단에 굵은 구분선 추가)
                    table_html = combined_stats.to_html(classes='dense-table', index=False)
                    rows = table_html.split('<tr>')
                    new_rows = [rows[0]]  # 헤더 부분
                    for row in rows[1:]:
                        if '<td>3연전</td>' in row:
                            # 3연전 행 상단에 1.5px 실선 및 강조 배경색 추가
                            new_rows.append(f'<tr class="series-row" style="background-color: #F8F9FA !important; font-weight: bold;">{row}')
                        else:
                            new_rows.append(f'<tr>{row}')
                    table_html = "".join(new_rows)
                    
                    st.write(table_html, unsafe_allow_html=True)
                    # st.markdown("<hr style='border: 1px solid #ccc;'>", unsafe_allow_html=True)


                    # 시각화 시작 
                    current_threshold = BattingConfig.get_hard_hit_threshold(batter)

                    # season_df를 기반으로 adf 생성
                    adf = season_df[
                        (season_df["exit_velocity"] >= current_threshold) & 
                        (season_df["launch_angle"] >= 9) & 
                        (season_df["launch_angle"] <= 33)
                    ].copy()

                    # [데이터 전처리 공통]
                    if not adf.empty:
                        adf['game_year'] = adf['game_year'].astype(str)
                        adf = adf.reset_index(drop=True).reset_index()
                        adf['index'] = adf['index'] + 1

                    # 공통 설정값
                    colors = {'2020':'rgba(68,1,84,0.7)', '2021':'rgba(35,144,140,0.7)', '2022': 'rgba(253,231,37,0.9)', '2023': 'rgba(153,102,255,0.9)', '2024': 'rgba(160,98,86,0.8)', '2025': 'rgba(68,1,84,0.6)', '2026' : 'rgba(255,000,051,0.9)'}
                    symbols = {'4-Seam Fastball':'circle', '2-Seam Fastball':'triangle-down', 'Cutter': 'triangle-se', 'Slider': 'triangle-right', 'Curveball': 'triangle-up', 'Changeup': 'diamond', 'Split-Finger':'square', 'Sweeper' : 'cross'}
                    homex = [-0.27, 0, 0.27, 0.27, -0.27, -0.27]
                    homey = [0.215, 0, 0.215, 0.43, 0.43, 0.215]

                    colors_2 = {'Neutral':'rgba(148,103,189,0.7)', 'Pitcher':'rgba(255,105,97,1)', 'Hitter': 'rgba(108,122,137,1)'}
                    colors_swing = {'hit_into_play':'rgba(140,86,75,0.6)', 'ball':'rgba(108,122,137,0.7)', 'foul':'rgba(67,89,119,0.6)', 'swinging_strike':'rgba(244,247,143,0.8)', 'called_strike':'rgba(108,122,137,0.7)', 'hit_into_play_no_out':'rgba(241,106,227,1)', 'hit_into_play_score':'rgba(255,72,120,0.9)', 'hit_by_pitch':'rgba(108,122,137,0.7)'}
                    group_df = group_df.reset_index(drop=True).reset_index()
                    group_df['index'] = group_df['index'] + 1
                    
                    group_df_swing = group_df_swing.reset_index(drop=True).reset_index()
                    group_df_swing['index'] = group_df_swing['index'] + 1

                    group_df_looking = group_df_looking.reset_index(drop=True).reset_index()
                    group_df_looking['index'] = group_df_looking['index'] + 1
                    
                    # --- [그래프 1 생성: 강한타구 존] ---
                    if not adf.empty:
                        # 데이터가 있을 때는 정상적으로 산점도 생성
                        fig1 = px.scatter(adf, x='plate_x', y='plate_z', 
                                        color='game_year', symbol='pitch_name', 
                                        color_discrete_map=colors, symbol_map=symbols, 
                                        template="simple_white")
                        
                        # 실제 데이터를 기반으로 유동적인 존 높이 설정
                        s_h, s_l = adf['high'].mean(), adf['low'].mean()
                        fig1.add_hline(y=s_h, line_width=2, line_color='rgba(108,122,137,0.9)')
                        fig1.add_hline(y=s_l, line_width=2, line_color='rgba(108,122,137,0.9)')
                        
                        h_step = (s_h - s_l) / 3
                        fig1.add_hline(y=s_l + h_step, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')
                        fig1.add_hline(y=s_l + 2 * h_step, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')
                    else:
                        # [지적하신 부분 수정] 데이터가 없을 때는 좌표축만 있는 빈 그래프 생성
                        fig1 = go.Figure()
                        # 배경을 하얀색으로 세팅
                        fig1.update_layout(template="simple_white")
                        
                        # 표준 스트라이크 존 가이드라인 표시 (고정값)
                        fig1.add_hline(y=1.1, line_width=2, line_color='rgba(108,122,137,0.5)')
                        fig1.add_hline(y=0.4, line_width=2, line_color='rgba(108,122,137,0.5)')
                        fig1.add_hline(y=0.63, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.3)')
                        fig1.add_hline(y=0.86, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.3)')

                    # [공통 적용] 좌우 라인 및 레이아웃 설정 (항상 실행)
                    fig1.add_vline(x=-0.27, line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig1.add_vline(x=0.27, line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig1.add_vline(x=-0.0903, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.3)')
                    fig1.add_vline(x=0.0903, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.3)')
                    
                    fig1.update_layout(xaxis_range=[-0.60, 0.60], yaxis_range=[0.0, 1.40], showlegend=False)
                    fig1.update_xaxes(title_text=None, showticklabels=False)
                    fig1.update_yaxes(title_text=None, showticklabels=False)
                    fig1.update_traces(marker=dict(size=10))


                    # --- [그래프 2 생성: 강한타구 포인트] ---
                    if not adf.empty:
                        # 데이터가 있을 때만 px.scatter 실행
                        fig2 = px.scatter(adf, x='contactZ', y='contactX', color='game_year', symbol='pitch_name', 
                                        color_discrete_map=colors, symbol_map=symbols, 
                                        hover_name="pitname", 
                                        hover_data=["rel_speed(km)","pitch_name","events","exit_velocity","description","launch_speed_angle","launch_angle"], 
                                        template="simple_white")
                    else:
                        # 데이터가 없을 때는 빈 캔버스 생성
                        fig2 = go.Figure()
                        fig2.update_layout(template="simple_white")

                    # [공통 적용] 홈플레이트 모양 및 가이드라인 (데이터가 없어도 항상 표시)
                    fig2.add_trace(go.Scatter(x=homex, y=homey, mode='lines', 
                                            line=dict(color='rgba(108,122,137,0.7)'), 
                                            showlegend=False))
                    
                    fig2.add_hline(y=1, line_dash='dash', line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig2.add_hline(y=0.43, line_dash='dash', line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig2.add_hline(y=0, line_dash='dash', line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig2.add_vline(x=-0.37, line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig2.add_vline(x=0.37, line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig2.add_vline(x=-0.27, line_dash='dash', line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig2.add_vline(x=0.27, line_dash='dash', line_width=1, line_color='rgba(108,122,137,0.7)')
                    
                    fig2.update_layout(xaxis_range=[-0.65, 0.65], yaxis_range=[-0.35, 1.25], showlegend=False)
                    fig2.update_xaxes(title_text=None, showticklabels=False)
                    fig2.update_yaxes(title_text=None, showticklabels=False)
                    fig2.update_traces(marker=dict(size=10))

                    
                    # --- [그래프 3 생성]  ---

                    fig3 = px.scatter(group_df, x='plate_x', y='plate_z', color='count_value', symbol='pitch_name', text='pitch_number', color_discrete_map=colors_2, hover_name="pitname", hover_data=["rel_speed(km)","pitch_name","events","exit_velocity","description","launch_speed_angle","launch_angle"], template="simple_white")
                    
                    for i, d in enumerate(fig3.data):
                        fig3.data[i].marker.symbol = symbols[fig3.data[i].name.split(', ')[1]]
                    fig3.update_layout(xaxis_range=[-0.60, 0.60], yaxis_range=[0.0, 1.40], showlegend=False)
                    fig3.update_traces(marker=dict(size=10)) # 그리드에서는 크기를 15~20 정도로 조절 추천
                    fig3.update_traces(textfont_size=10)
                    fig3.update_xaxes(title_text=None, showticklabels=False) # x축 'plate_x' 텍스트 제거
                    fig3.update_yaxes(title_text=None, showticklabels=False) # y축 'plate_z' 텍스트 제거

                    
                    fig3.add_hline(y=group_df['high'].mean(), line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig3.add_hline(y=group_df['low'].mean(), line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig3.add_vline(x=-0.27,line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig3.add_vline(x=0.27, line_width=2, line_color='rgba(108,122,137,0.9)')


                    fig3.add_hline(y= group_df['1/3'].mean() , line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')
                    fig3.add_hline(y= group_df['2/3'].mean() , line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')

                    fig3.add_vline(x=-0.0903, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')
                    fig3.add_vline(x=0.0903, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')
                    

                    # --- [그래프 4 생성]  ---

                    fig4 = px.scatter(group_df_looking, x='plate_x', y='plate_z', color='count_value', symbol='pitch_name', text='pitch_number', color_discrete_map=colors_2, hover_name="pitname", hover_data=["rel_speed(km)","pitch_name","events","exit_velocity","description","launch_speed_angle","launch_angle"], template="simple_white")
                    
                    for i, d in enumerate(fig4.data):
                        fig4.data[i].marker.symbol = symbols[fig4.data[i].name.split(', ')[1]]
                    fig4.update_layout(xaxis_range=[-0.60, 0.60], yaxis_range=[0.0, 1.40], showlegend=False)
                    fig4.update_traces(marker=dict(size=10)) # 그리드에서는 크기를 15~20 정도로 조절 추천
                    fig4.update_traces(textfont_size=10)
                    fig4.update_xaxes(title_text=None, showticklabels=False) # x축 'plate_x' 텍스트 제거
                    fig4.update_yaxes(title_text=None, showticklabels=False) # y축 'plate_z' 텍스트 제거

                    
                    fig4.add_hline(y=group_df_looking['high'].mean(), line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig4.add_hline(y=group_df_looking['low'].mean(), line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig4.add_vline(x=-0.27,line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig4.add_vline(x=0.27, line_width=2, line_color='rgba(108,122,137,0.9)')


                    fig4.add_hline(y= group_df_looking['1/3'].mean() , line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)    ')
                    fig4.add_hline(y= group_df_looking['2/3'].mean() , line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')

                    fig4.add_vline(x=-0.0903, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')
                    fig4.add_vline(x=0.0903, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')
                        

                    # --- [그래프 5 생성]  ---

                    fig5 = px.scatter(group_df_swing, x='plate_x', y='plate_z', color='description', symbol='pitch_name', text='index', color_discrete_map=colors_swing , hover_name="pitname", hover_data=["rel_speed(km)","pitch_name","events","exit_velocity","description","launch_speed_angle","launch_angle"], template="simple_white")
                    
                    for i, d in enumerate(fig5.data):
                        fig5.data[i].marker.symbol = symbols[fig5.data[i].name.split(', ')[1]]
                    fig5.update_layout(xaxis_range=[-0.60, 0.60], yaxis_range=[0.0, 1.40], showlegend=False)
                    fig5.update_traces(marker=dict(size=10)) # 그리드에서는 크기를 15~20 정도로 조절 추천
                    fig5.update_traces(textfont_size=10)
                    fig5.update_xaxes(title_text=None, showticklabels=False) # x축 'plate_x' 텍스트 제거
                    fig5.update_yaxes(title_text=None, showticklabels=False) # y축 'plate_z' 텍스트 제거

                    
                    fig5.add_hline(y=group_df_swing['high'].mean(), line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig5.add_hline(y=group_df_swing['low'].mean(), line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig5.add_vline(x=-0.27,line_width=2, line_color='rgba(108,122,137,0.9)')
                    fig5.add_vline(x=0.27, line_width=2, line_color='rgba(108,122,137,0.9)')


                    fig5.add_hline(y= group_df_swing['1/3'].mean() , line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')
                    fig5.add_hline(y= group_df_swing['2/3'].mean() , line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')

                    fig5.add_vline(x=-0.0903, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')
                    fig5.add_vline(x=0.0903, line_width=1, line_dash='dash', line_color='rgba(108,122,137,0.9)')


                    # --- [그래프 6 생성]  ---
                    fig6 = px.scatter(group_df_swing, x='contactZ', y='contactX', color='description', symbol='pitch_name', text='index', color_discrete_map=colors_swing , hover_name="pitname", hover_data=["rel_speed(km)","pitch_name","events","exit_velocity","description","launch_speed_angle","launch_angle"], template="simple_white")
                    for i, d in enumerate(fig6.data):
                        fig6.data[i].marker.symbol = symbols[fig6.data[i].name.split(', ')[1]]
                    fig6.update_layout(xaxis_range=[-0.65,0.65],yaxis_range=[-0.35,1.25],showlegend=False)
                    
    
                    fig6.update_xaxes(title_text=None, showticklabels=False) # x축 'plate_x' 텍스트 제거
                    fig6.update_yaxes(title_text=None, showticklabels=False) # y축 'plate_z' 텍스트 제거
                    
                    fig6.update_traces(marker=dict(size=10))
                    fig6.update_traces(textfont_size=10)
                    # # v line

                    fig6.append_trace(go.Scatter(x=homex,y=homey, mode = 'lines', line=dict(color='rgba(108,122,137,0.7)') ), row = 1 , col = 1)


                    fig6.add_hline(y=1, line_dash='dash' ,line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig6.add_hline(y=0.43,  line_dash='dash' ,line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig6.add_hline(y=0,  line_dash='dash' ,line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig6.add_vline(x=-0.37,line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig6.add_vline(x=0.37, line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig6.add_vline(x=-0.27, line_dash='dash' ,line_width=1, line_color='rgba(108,122,137,0.7)')
                    fig6.add_vline(x=0.27, line_dash='dash', line_width=1, line_color='rgba(108,122,137,0.7)')
                    
                    # --- [그래프 7 생성] ---
                    fig7 = px.scatter(group_df_swing, x='groundX', y='groundY', color='description', text="index",symbol="pitch_name", color_discrete_map=colors_swing, hover_name="pitname", hover_data=["rel_speed(km)","pitch_name","events","exit_velocity","description","launch_speed_angle","launch_angle"], template="simple_white")
                    
                    for i, d in enumerate(fig7.data):
                        fig7.data[i].marker.symbol = symbols[fig7.data[i].name.split(', ')[1]]

                    fig7.update_layout(showlegend=False, xaxis_range=[-5,140], yaxis_range=[-5,140])
                    fig7.update_traces(marker=dict(size=12))
                    fig7.update_traces(textfont_size=10)
                    fig7.update_xaxes(title_text=None, showticklabels=False) # x축 'plate_x' 텍스트 제거
                    fig7.update_yaxes(title_text=None, showticklabels=False) # y축 'plate_z' 텍스트 제거
                    
                    # fig7.update_layout({'plot_bgcolor': 'rgba(255,255,255,1)', 'paper_bgcolor': 'rgba(255,255,255,1)',})

                    fig7.update_yaxes(gridcolor='rgba(255,255,255,1)')
                    fig7.update_xaxes(gridcolor='rgba(255,255,255,1)')
                    fig7.update_layout(
                        shapes=[
                            # Quadratic Bezier Curves
                            dict(
                                type="path",
                                path="M 0,100 Q 120,120 100,0",
                                line_color="rgba(108,122,137,0.7)",
                                line_width = 2,
                                fillcolor='rgba(0,0,0,0)' # 내부 투명화
                            )])

                    fig7.add_shape(type="rect",
                        x0=0, y0=0, x1=28, y1=28,
                        line=dict(color="rgba(108,122,137,0.7)"),
                        line_width=2,
                        fillcolor='rgba(0,0,0,0)', # 내부 투명화
                        row="all", col="all"
                    )

                    fig7.add_shape(type="rect",
                        x0=0, y0=0, x1=150, y1=150,
                        line=dict(color="rgba(108,122,137,0.7)"),
                        line_width=2,
                        fillcolor='rgba(0,0,0,0)', # 내부 투명화
                        row="all", col="all"
                    )

                    # 1. 그룹별 배경색 지정 및 너비 자동화 (use_container_width 대응)
                    color_pink = "#FFF0F5"
                    color_gray = "#F8F9FA"
                    color_darkgray = "#E9ECEF"

                    # 그래프 일반설정
                    common_style = dict(
                        height=210, 
                        width=175, 
                        margin=dict(l=15, r=15, t=10, b=15, autoexpand=False), # autoexpand 추가
                        autosize=False,
                        font=dict(color="black")
                    )
                    for f in [fig1, fig2, fig3, fig4, fig5, fig6]:
                        f.update_layout(**common_style)
                        f.update_coloraxes(showscale=False) 
                        f.update_traces(showlegend=False)
                        
                    
                    # fig7은 스프레이 차트라 너비만 별도 조정
                    fig7.update_layout(**common_style)
                    fig7.update_layout(width=220)

                    # fig1~7: 그룹별 배경색 지정 (plot_bgcolor 투명화)
                    for f in [fig1, fig2]: f.update_layout(paper_bgcolor=color_pink, plot_bgcolor='rgba(255,255,255,1)')
                    for f in [fig3, fig4]: f.update_layout(paper_bgcolor=color_gray, plot_bgcolor='rgba(255,255, 255,1)')
                    for f in [fig5, fig6, fig7]: f.update_layout(paper_bgcolor=color_darkgray, plot_bgcolor='rgba(255,255,255,1)')

                    # 2. 레이아웃 배치 (공백 최소화)
                    r1_col1, r1_col2, r1_col3, r1_col4 = st.columns(4, gap="small")

                    with r1_col1:
                        st.markdown('<div class="pink-title-bar" style="width: 175px;">\'24~26시즌 강한타구 존</div>', unsafe_allow_html=True)
                        st.plotly_chart(fig1, use_container_width=False, key=f"{player_name}_r1c1")

                    with r1_col2:
                        st.markdown('<div class="gray-title-bar" style="width: 175px;">투구지점(투구순서)</div>', unsafe_allow_html=True)
                        st.plotly_chart(fig3, use_container_width=False, key=f"{player_name}_{idx}_r1c2")

                    with r1_col3:
                        st.markdown('<div class="gray-title-bar" style="width: 175px;">Looking</div>', unsafe_allow_html=True)
                        st.plotly_chart(fig4, use_container_width=False, key=f"{player_name}_{idx}_r1c3")

                    with r1_col4:
                        st.markdown('<div class="darkgray-title-bar" style="width: 175px;">Swing Zone</div>', unsafe_allow_html=True)
                        st.plotly_chart(fig5, use_container_width=False, key=f"{player_name}_{idx}_r1c4")

                    # r3_1 정의 바로 위에 추가
                    r3_1, r3_2, r3_3 = st.columns([1, 2, 1], gap="small")
                    with r3_1:
                        try:
                            with open("D:/JEON/추적데이터/2026/Trackman/Series Report/season.jpg", "rb") as f:
                                img_data = f.read()
                                encoded_img = base64.b64encode(img_data).decode()
                            
                                # 이미지 div에 직접 음수 마진을 넣어 위아래 공백을 '흡수'합니다.
                                st.markdown(
                                    f'''
                                    <div style="
                                        display: flex; 
                                        justify-content: flex-start; 
                                        margin-top: 0px;    /* 위쪽 차트와 바짝 붙임 */
                                        margin-bottom: 0px; /* 아래쪽 차트와 바짝 붙임 */
                                        padding: 0;
                                    ">
                                        <img src="data:image/jpeg;base64,{encoded_img}" 
                                            style="height:20px; max-width:100%; object-fit:contain;">
                                    </div>
                                    ''', 
                                    unsafe_allow_html=True
                                )
                        except:
                            st.warning("D:/JEON/추적데이터/2026/Trackman/Series Report/season.jpg 파일을 찾을 수 없습니다.")
                    
                    with r3_2:
                        try:
                            with open("D:/JEON/추적데이터/2026/Trackman/Series Report/count.jpg", "rb") as f:
                                img_data = f.read()
                                encoded_img = base64.b64encode(img_data).decode()
                            
                                # 이미지 div에 직접 음수 마진을 넣어 위아래 공백을 '흡수'합니다.
                                st.markdown(
                                    f'''
                                    <div style="
                                        display: flex; 
                                        justify-content: center; 
                                        margin-top: -10px;    /* 위쪽 차트와 바짝 붙임 */
                                        margin-bottom: 0px; /* 아래쪽 차트와 바짝 붙임 */
                                        padding: 0;
                                    ">
                                        <img src="data:image/jpeg;base64,{encoded_img}" 
                                            style="height:30px; max-width:100%; object-fit:contain;">
                                    </div>
                                    ''', 
                                    unsafe_allow_html=True
                                )
                        except:
                            st.warning("D:/JEON/추적데이터/2026/Trackman/Series Report/count.jpg 파일을 찾을 수 없습니다.")

                    # [3행] 하단부 그룹 연결 (상단 공백 제거)
                    r2_1, r2_2, r2_3, r2_4 = st.columns([1, 1, 1.3, 0.7], gap="small")


                    with r2_1:
                        st.markdown('<div class="pink-title-bar" style="width: 175px;">\'24~26시즌 강한타구 포인트</div>', unsafe_allow_html=True)
                        # 여기 마진을 딱 3px만 넣어보면 1행의 그래프들과 느낌이 비슷해질 거예요.
                        st.plotly_chart(fig2, use_container_width=False, key=f"{player_name}_{idx}_r2c1")

                    with r2_2:
                        st.markdown('<div class="darkgray-title-bar" style="width: 175px;">Swing Contact</div>', unsafe_allow_html=True)
                        st.plotly_chart(fig6, use_container_width=False, key=f"{player_name}_{idx}_r1c5")

                    with r2_3:
                        st.markdown('<div class="darkgray-title-bar" style="width: 220px;">Spary Chart</div>', unsafe_allow_html=True)
                        st.plotly_chart(fig7, use_container_width=False, key=f"{player_name}_{idx}_r1c6")

                    with r2_4:
                        # 로컬 사진을 읽어서 데이터로 변환 (보안 문제 해결 및 높이 동기화)
                        try:
                            with open("D:/JEON/추적데이터/2026/Trackman/Series Report/symbol.jpg", "rb") as f:
                                img_data = f.read()
                                encoded_img = base64.b64encode(img_data).decode()
                            
                                st.markdown(
                                    f'<div style="display: flex; justify-content: flex-end;">'
                                    f'<img src="data:image/jpeg;base64,{encoded_img}" '
                                    f'style="height:175px; max-width:100%; object-fit:contain;">'
                                    f'</div>', 
                                    unsafe_allow_html=True
                                )
                        except:
                            st.warning("D:/JEON/추적데이터/2026/Trackman/Series Report/symbol.jpg 파일을 찾을 수 없습니다.")


                    
                    # [3행] 최하단 - 행 전체를 차지하는 표 (공백 제거)
                    # st.markdown("**📋 세부 분석 데이터**")
                    # season이나 pitch_name 같은 DataFrame을 넣으시면 됩니다.

                    # 데이터 준비 및 반올림
                    if player_name == "힐리어드":
                        sdf_table = group_df_swing[['index', 'game_date','inning','balls','strikes','pitname','catcher','pitch_name','rel_speed(km)', 'release_spin_rate','description','events','exit_velocity','launch_angle','hit_spin_rate','hit_distance', 'BatSpeed','VerticalAttackAngle']]
                    else:
                        sdf_table = group_df_swing[['index', 'game_date','inning','balls','strikes','NAME_pitcher','NAME_catcher','pitch_name','rel_speed(km)', 'release_spin_rate','description','events','exit_velocity','launch_angle','hit_spin_rate','hit_distance', 'BatSpeed','VerticalAttackAngle']]
                    # 0. 수치 데이터 포맷팅 (소수점 제어 및 문자열 변환으로 .0 방지)
                    format_map = {
                        'rel_speed(km)': 1, 'release_spin_rate': 0, 'exit_velocity': 1, 
                        'launch_angle': 0, 'hit_spin_rate': 0, 'hit_distance': 0, 
                        'BatSpeed': 1, 'VerticalAttackAngle': 1
                    }
                    for col, precision in format_map.items():
                        if col in sdf_table.columns:
                            # NaN이 아닌 경우에만 해당 소수점 자리수의 문자열로 변환
                            sdf_table[col] = sdf_table[col].apply(
                                lambda x: f"{x:.{precision}f}" if pd.notnull(x) else x
                            )
                    
                    # 만약 선수가 "힐리어드"이 아니면 한글 매핑을 진행하고, "힐리어드"이면 원래 영어 값을 유지합니다.
                    if player_name != "힐리어드":
                        sdf_table['pitch_name'] = sdf_table['pitch_name'].map(PitchConfig.PITCH_NAME_MAP).fillna(sdf_table['pitch_name'])
                        sdf_table['description'] = sdf_table['description'].map(DesConfig.DES_NAME_MAP).fillna(sdf_table['description'])
                        sdf_table['events'] = sdf_table['events'].map(EventsConfig.EVENT_NAME_MAP).fillna(sdf_table['events'])
                    else:
                        sdf_table['description'] = sdf_table['description'].map(DesConfigENG.DES_NAME_MAP).fillna(sdf_table['description'])

                    # NaN 값을 빈칸으로 처리 (유저 요청)
                    sdf_table = sdf_table.fillna("")

                    # 복사본 생성 및 컬럼명 변경
                    sdf_table_styled = sdf_table.rename(columns={
                        'index' : '구분',
                        'game_date' : '날짜',
                        'inning' : '이닝',
                        'balls' : 'B',
                        'strikes' : 'S',
                        'NAME_pitcher' : '투수',
                        'NAME_catcher' : '포수',
                        'pitname' : '투수',
                        'catcher' : '포수',
                        'pitch_name' : '구종',
                        'rel_speed(km)' : '구속',
                        'release_spin_rate' : '회전수',
                        'description' : '투구내용',
                        'events' : '결과',
                        'exit_velocity' : '타구속도',
                        'launch_angle' : '발사각도',
                        'hit_spin_rate' : '타구스핀',
                        'hit_distance' : '비거리',
                        'BatSpeed' : '배트스피드',
                        'VerticalAttackAngle' : '어택앵글'
                    })
                    
                    # 1. 기존처럼 완벽한 형식의 HTML 생성 (반올림/폰트 유지)
                    table_html = sdf_table_styled.to_html(classes='dense-table', index=False)
                    
                    # 2. 특정 결과(안타 등) 강조 및 날짜 변경선 클래스 부여
                    target_hits = ['안타', '2루타', '3루타', '홈런', 'single', 'double', 'triple', 'home_run']
                    table_rows = table_html.split('<tr>')
                    new_table_rows = [table_rows[0]] # 헤더 부분 보존
                    
                    prev_date = None
                    for i, row in enumerate(table_rows[1:]):
                        current_date = sdf_table_styled.iloc[i]['날짜']
                        classes = []
                        
                        # 날짜가 바뀌는 시점 클래스
                        if prev_date is not None and current_date != prev_date:
                            classes.append("date-sep")
                        
                        # 안타 등 결과 강조 클래스
                        if any(f'<td>{hit}</td>' in row for hit in target_hits):
                            classes.append("hit-row")
                        
                        if classes:
                            new_table_rows.append(f'<tr class="{" ".join(classes)}">{row}')
                        else:
                            new_table_rows.append(f'<tr>{row}')
                            
                        prev_date = current_date
                        
                    table_html = "".join(new_table_rows)

                    # 3. 행 수에 따라 글자 크기와 여백 동적 조절 (25줄 초과 시 더 축소)
                    num_rows = len(sdf_table_styled)
                    if num_rows > 30:
                        font_size = "8px"
                        padding_val = "0.5px 4px"
                    elif num_rows > 24:
                        font_size = "8px"
                        padding_val = "1px 4px"
                    else:
                        font_size = "8px"
                        padding_val = "2px 4px"

                    scrollable_table_html = f"""
                    <div style="overflow-x: auto; width: 100%; margin-top: -10px;">
                        <style>
                            /* 표 전체와 하위 셀들의 테두리 설정 */
                            .dense-table, .dense-table th, .dense-table td {{
                                border: 0.1px solid #ddd !important; /* 선 두께를 0.1px로 매우 가늘게 설정 */
                                border-collapse: collapse !important;
                            }}
                            .dense-table td, .dense-table th {{
                                font-size: {font_size} !important;
                                padding: {padding_val} !important;
                                white-space: nowrap !important;
                            }}
                            /* 날짜 구분선만 조금 더 명확하게 (기존 유지) */
                            .dense-table tr.date-sep td {{
                                border-top: 2px solid #999 !important;
                            }}
                            .dense-table tr.hit-row td {{
                                background-color: #FFF5E1 !important;
                                font-weight: bold !important;
                            }}
                            /* 인쇄 시 색상과 선 보존 강제 설정 */
                            * {{
                                -webkit-print-color-adjust: exact !important;
                                print-color-adjust: exact !important;
                            }}
                            /* 3연전 행(series-row)의 모든 자식 td에 상단 선 추가 */
                            .dense-table tr.series-row td {{
                                border-top: 2px solid #444 !important; /* 더 굵고 진한 선 */
                            }}
                        </style>
                        {table_html}
                    </div>
                    """

                    # 데이터 출력
                    st.write(scrollable_table_html, unsafe_allow_html=True)

            # --- 루프 종료 ---
                    

        else:
            st.info("좌측에서 필터 조건을 선택하고 ‘필터 적용’ 버튼을 눌러주세요.")
    else:
        st.info("데이터가 없습니다.")



