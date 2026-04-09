import pandas as pd
import numpy as np

def safe_divide(numerator, denominator):
    numerator = numerator.astype(float)
    denominator = denominator.astype(float)
    result = pd.Series(np.zeros(len(numerator)), index=numerator.index)
    mask = denominator != 0
    result[mask] = numerator[mask] / denominator[mask]
    return result


def create_batter_stats(df, indexes={}):
    """
    df: 데이터프레임
    indexes: 사용할 인덱스 정의 딕셔너리
    """

    # reindex 설정을 딕셔너리로 정의
    reindex_options = {
        'game_year': [2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019],
        'level': ['MAJOR', 'AAA', 'KoreaBaseballOrganization', 'KBO Minors','NPB', 'NPM'],
        'pitch_name': ['4-Seam Fastball','2-Seam Fastball','Cutter','Slider','Curveball','Sweeper','Changeup','Split-Finger', 'ALL'],
        'p_kind': ['Fastball', 'Breaking', 'Off_Speed'],
        'stand': ['R','L'],
        'p_throws' : ['R', 'L', 'S'],
        'p_throw' : ['R','L']
    }

    
    # 조건 필터링
    season_df = df.copy()
    index_cols = []
    # 디버깅을 위한
  
    # 그 다음 indexes 설정
    for col, description in indexes.items():
        # if col != 'level':  # level은 마지막에 추가
        index_cols.append(col)
    
    
    # 전체 데이터가 없는 경우
    if len(season_df) == 0:
        return "조건에 맞는 데이터가 없습니다. 입력한 조건들을 확인해주세요."
    
    # 최소 데이터 수 확인 (예: 10개 미만인 경우 경고)
    if len(season_df) < 10:
        return f"데이터가 너무 적습니다 (현재 {len(season_df)}개). 더 많은 데이터가 필요할 수 있습니다."

    
    # level은 항상 마지막 인덱스로 추가
    # index_cols.append('level')
    
    # 기존 피벗 테이블 생성 코드를 함수로 정리
    stats = {
        'game': pd.pivot_table(season_df, index=index_cols, values='game_date', aggfunc='nunique', margins=False),
        'pitched': pd.pivot_table(season_df, index=index_cols, values='game_date', aggfunc='count', margins=False),
        'rel_speed': pd.pivot_table(season_df, index=index_cols, values='rel_speed(km)', aggfunc='mean', margins=False),

        'inplay' : pd.pivot_table(season_df, index=index_cols, values='inplay', aggfunc='sum', margins=False),
        'exit_velocity' : pd.pivot_table(season_df, index=index_cols, values='exit_velocity', aggfunc='mean', margins=False),
        'launch_angleX' : pd.pivot_table(season_df, index=index_cols, values='launch_angleX', aggfunc='mean', margins=False),
        'hit_spin' : pd.pivot_table(season_df, index=index_cols, values='hit_spin', aggfunc='mean', margins=False),
        # 🎯 EV50 계산 (groupby_key 사용)
        'ev50' : pd.pivot_table(
            season_df[season_df.groupby(index_cols)['exit_velocity'].transform('median') <= season_df['exit_velocity']], 
            index=index_cols, 
            values='exit_velocity', 
            aggfunc='mean', 
            margins=False
        ).rename(columns={'exit_velocity': 'ev50'}),
        'avg_bat_speed': pd.pivot_table(
            season_df[season_df.groupby(index_cols)['BatSpeed'].transform(lambda x: x.quantile(0.1)) <= season_df['BatSpeed']],
            index=index_cols,
            values='BatSpeed',
            aggfunc='mean',
            margins=False
        ).rename(columns={'BatSpeed': 'avg_bat_speed'}),
        'hit' : pd.pivot_table(season_df, index=index_cols, values='hit', aggfunc='sum', margins=False),
        'ab' : pd.pivot_table(season_df, index=index_cols, values='ab', aggfunc='sum', margins=False),
        'pa' : pd.pivot_table(season_df, index=index_cols, values='pa', aggfunc='sum', margins=False),
        'single' : pd.pivot_table(season_df, index=index_cols, values='single', aggfunc='sum', margins=False),
        'double' : pd.pivot_table(season_df, index=index_cols, values='double', aggfunc='sum', margins=False),
        'triple' : pd.pivot_table(season_df, index=index_cols, values='triple', aggfunc='sum', margins=False),
        'home_run' : pd.pivot_table(season_df, index=index_cols, values='home_run', aggfunc='sum', margins=False),
        'walk' : pd.pivot_table(season_df, index=index_cols, values='walk', aggfunc='sum', margins=False),
        'hit_by_pitch' : pd.pivot_table(season_df, index=index_cols, values='hit_by_pitch', aggfunc='sum', margins=False),
        'sac_fly' : pd.pivot_table(season_df, index=index_cols, values='sac_fly', aggfunc='sum', margins=False),

        'z_in' : pd.pivot_table(season_df, index=index_cols, values='z_in', aggfunc='sum', margins=False),
        'z_swing' : pd.pivot_table(season_df, index=index_cols, values='z_swing', aggfunc='sum', margins=False),
        'z_con' : pd.pivot_table(season_df, index=index_cols, values='z_con', aggfunc='sum', margins=False),
        'z_out' : pd.pivot_table(season_df, index=index_cols, values='z_out', aggfunc='sum', margins=False),
        'o_swing' : pd.pivot_table(season_df, index=index_cols, values='o_swing', aggfunc='sum', margins=False),
        'o_con' : pd.pivot_table(season_df, index=index_cols, values='o_con', aggfunc='sum', margins=False),

        'f_swing' : pd.pivot_table(season_df, index=index_cols, values='f_swing', aggfunc='sum', margins=False),
        # 'f_s' : pd.pivot_table(season_df, index=index_cols, values='f_s', aggfunc='sum', margins=False),
        'f_pitch' : pd.pivot_table(season_df, index=index_cols, values='f_pitch', aggfunc='sum', margins=False),
        'swing' : pd.pivot_table(season_df, index=index_cols, values='swing', aggfunc='sum', margins=False),
        'whiff' : pd.pivot_table(season_df, index=index_cols, values='whiff', aggfunc='sum', margins=False),

        'weak' : pd.pivot_table(season_df, index=index_cols, values='weak', aggfunc='sum', margins=False),
        'topped' : pd.pivot_table(season_df, index=index_cols, values='topped', aggfunc='sum', margins=False),
        'under' : pd.pivot_table(season_df, index=index_cols, values='under', aggfunc='sum', margins=False),
        'flare' : pd.pivot_table(season_df, index=index_cols, values='flare', aggfunc='sum', margins=False),
        'solid_contact' : pd.pivot_table(season_df, index=index_cols, values='solid_contact', aggfunc='sum', margins=False),
        'barrel' : pd.pivot_table(season_df, index=index_cols, values='barrel', aggfunc='sum', margins=False),

        
    }
    
    # 모든 통계를 하나의 데이터프레임으로 결합
    # 모든 통계를 하나의 데이터프레임으로 결합 (컬럼명 유실 방지를 위해 개별 지정)
    new_stats = {}
    for name, s_df in stats.items():
        if isinstance(s_df, pd.DataFrame):
            if len(s_df.columns) > 0:
                s_df.columns = [name]
                new_stats[name] = s_df
            else:
                # 데이터가 없어 컬럼이 생성되지 않은 경우 빈 시리즈 생성
                new_stats[name] = pd.Series(index=s_df.index, name=name, dtype='float64')
        elif isinstance(s_df, pd.Series):
            s_df.name = name
            new_stats[name] = s_df
        else:
            new_stats[name] = s_df

    review_df = pd.concat(new_stats.values(), axis=1)
    
    review_df['inplay_pit'] = safe_divide(review_df['inplay'], review_df['pitched']).round(3)

    review_df['avg'] = safe_divide(review_df['hit'], review_df['ab'])

    review_df['obp'] = safe_divide(
        review_df['hit'] + review_df['hit_by_pitch'] + review_df['walk'], 
        review_df['ab'] + review_df['hit_by_pitch'] + review_df['walk'] + review_df['sac_fly']
    )

    review_df['slg'] = safe_divide(
        review_df['single']*1 + review_df['double']*2 + review_df['triple']*3 + review_df['home_run']*4,
        review_df['ab']
    )

    review_df['ops'] = review_df['obp'] + review_df['slg']

    review_df['z%'] = safe_divide(review_df['z_in'], review_df['pitched'])
    review_df['z_swing%'] = safe_divide(review_df['z_swing'], review_df['z_in'])
    review_df['z_con%'] = safe_divide(review_df['z_con'], review_df['z_swing'])

    review_df['o%'] = safe_divide(review_df['z_out'], review_df['pitched'])
    review_df['o_swing%'] = safe_divide(review_df['o_swing'], review_df['z_out'])
    review_df['o_con%'] = safe_divide(review_df['o_con'], review_df['o_swing'])

    review_df['f_swing%'] = safe_divide(review_df['f_swing'], review_df['f_pitch'])
    review_df['swing%'] = safe_divide(review_df['swing'], review_df['pitched'])
    review_df['whiff%'] = safe_divide(review_df['whiff'], review_df['swing'])
    review_df['inplay_sw'] = safe_divide(review_df['inplay'], review_df['swing'])

    kbo_z_swing = 0.639
    kbo_o_swing = 0.262

    condition = [
                    (review_df['z_swing%'] >= kbo_z_swing) & (review_df['o_swing%'] >= kbo_o_swing),
                    (review_df['z_swing%'] >= kbo_z_swing) & (review_df['o_swing%'] <= kbo_o_swing),
                    (review_df['z_swing%'] <= kbo_z_swing) & (review_df['o_swing%'] >= kbo_o_swing),
                    (review_df['z_swing%'] <= kbo_z_swing) & (review_df['o_swing%'] <= kbo_o_swing)
                    ]

    choicelist = ['Aggressive','Selective','Non_Selective','Passive']

    review_df['approach'] = np.select(condition, choicelist, default='Not Specified')

    review_df['sum'] = review_df['weak'] + review_df['topped'] + review_df['under'] + review_df['flare'] + review_df['solid_contact'] + review_df['barrel']

    review_df['weak'] = safe_divide(review_df['weak'], review_df['sum'])
    review_df['topped'] = safe_divide(review_df['topped'], review_df['sum'])
    review_df['under'] = safe_divide(review_df['under'], review_df['sum'])
    review_df['flare'] = safe_divide(review_df['flare'], review_df['sum'])
    review_df['solid_contact'] = safe_divide(review_df['solid_contact'], review_df['sum'])
    review_df['barrel'] = safe_divide(review_df['barrel'], review_df['sum'])

    # review_df['S%'] = review_df['S'] / review_df['pitched']





    review_df = review_df[['game','pitched','pa','ab','hit','walk','rel_speed', 'inplay_pit','exit_velocity','launch_angleX', 'hit_spin', 'ev50', 'avg_bat_speed', 'obp','slg','avg','ops',
                        'z%','z_swing%','z_con%','o%','o_swing%', 'o_con%', 'f_swing%', 'swing%', 'whiff%','inplay_sw',
                        'weak','topped','under','flare','solid_contact','barrel','approach' ]]

    review_df = review_df.round({
        'rel_speed':1, 'exit_velocity':1, 'launch_angleX':1, 'hit_spin':0, 'ev50':1,
        'avg':3, 'obp':3, 'slg':3, 'ops':3,
        'z%':3, 'z_swing%':3, 'z_con%':3, 'o%':3, 'o_swing%':3, 'o_con%':3,
        'f_swing%':3, 'swing%':3, 'whiff%':3, 'inplay_sw':3,
        'weak':3, 'topped':3, 'under':3, 'flare':3, 'solid_contact':3, 'barrel':3,
        'approach':3
    })

    percent_cols = [
        'z%', 'z_swing%', 'z_con%', 'o%', 'o_swing%', 'o_con%', 'f_swing%',
        'swing%', 'whiff%', 'inplay_sw', 'weak','topped','under','flare','solid_contact','barrel'
    ]

    for col in percent_cols:
        if col in review_df.columns:
            review_df[col] = (review_df[col] * 100).round(1).astype(str) + '%'

    for col in index_cols:
        if col in reindex_options:
            valid_idx = [v for v in reindex_options[col] if v in review_df.index.get_level_values(col)]
            review_df = review_df.reindex(valid_idx, level=col)

    return review_df


def create_pitcher_stats(df, indexes={}):
    """
    df: 데이터프레임
    indexes: 사용할 인덱스 정의 딕셔너리
    """

    # reindex 설정을 딕셔너리로 정의
    reindex_options = {
        'game_year': [2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019],
        'level': ['MAJOR', 'AAA', 'KoreaBaseballOrganization', 'KBO Minors','NPB', 'NPM'],
        'pitch_name': ['4-Seam Fastball','2-Seam Fastball','Cutter','Slider','Curveball','Sweeper','Changeup','Split-Finger', 'ALL'],
        'p_kind': ['Fastball', 'Breaking', 'Off_Speed'],
        'stand': ['R','L'],
        'p_throws' : ['R', 'L', 'S'],
        'p_throw' : ['R','L']
    }

    # 조건 필터링
    season_df = df.copy()
    index_cols = []
    
    # 그 다음 indexes 설정
    for col, description in indexes.items():
        # if col != 'level':  # level은 마지막에 추가
        index_cols.append(col)
    
    # 전체 데이터가 없는 경우
    if len(season_df) == 0:
        return "조건에 맞는 데이터가 없습니다. 입력한 조건들을 확인해주세요."
    
    # 최소 데이터 수 확인 (예: 10개 미만인 경우 경고)
    if len(season_df) < 10:
        return f"데이터가 너무 적습니다 (현재 {len(season_df)}개). 더 많은 데이터가 필요할 수 있습니다."
    
    # level은 항상 마지막 인덱스로 추가
    # index_cols.append('level')
    
    # 기존 피벗 테이블 생성 코드를 함수로 정리
    stats = {
        'game': pd.pivot_table(season_df, index=index_cols, values='game_date', aggfunc='nunique', margins=False),
        'pitched': pd.pivot_table(season_df, index=index_cols, values='game_date', aggfunc='count', margins=False),
        'rel_speed': pd.pivot_table(season_df, index=index_cols, values='rel_speed(km)', aggfunc='mean', margins=False),
        # 'max_rel_speed': pd.pivot_table(season_df, index=index_cols, values='rel_speed(km)', aggfunc='max', margins=False),
        'spin_rate' : pd.pivot_table(season_df, index=index_cols, values='release_spin_rate', aggfunc='mean', margins=False),
        'ver_break' : pd.pivot_table(season_df, index=index_cols, values='ver_break', aggfunc='mean', margins=False),
        'hor_break' : pd.pivot_table(season_df, index=index_cols, values='hor_break', aggfunc='mean', margins=False),
        'rel_height' : pd.pivot_table(season_df, index=index_cols, values='rel_height', aggfunc='mean', margins=False),
        'rel_side' : pd.pivot_table(season_df, index=index_cols, values='rel_side', aggfunc='mean', margins=False),
        'extension' : pd.pivot_table(season_df, index=index_cols, values='extension', aggfunc='mean', margins=False),
        'spin_axis' : pd.pivot_table(season_df, index=index_cols, values='release_spin_axis', aggfunc='mean', margins=False),
        'inplay' : pd.pivot_table(season_df, index=index_cols, values='inplay', aggfunc='sum', margins=False),
        'exit_velocity' : pd.pivot_table(season_df, index=index_cols, values='exit_velocity', aggfunc='mean', margins=False),
        'launch_angleX' : pd.pivot_table(season_df, index=index_cols, values='launch_angleX', aggfunc='mean', margins=False),
        'hit_spin' : pd.pivot_table(season_df, index=index_cols, values='hit_spin', aggfunc='mean', margins=False),

        'hit' : pd.pivot_table(season_df, index=index_cols, values='hit', aggfunc='sum', margins=False),
        'ab' : pd.pivot_table(season_df, index=index_cols, values='ab', aggfunc='sum', margins=False),
        'pa' : pd.pivot_table(season_df, index=index_cols, values='pa', aggfunc='sum', margins=False),
        'single' : pd.pivot_table(season_df, index=index_cols, values='single', aggfunc='sum', margins=False),
        'double' : pd.pivot_table(season_df, index=index_cols, values='double', aggfunc='sum', margins=False),
        'triple' : pd.pivot_table(season_df, index=index_cols, values='triple', aggfunc='sum', margins=False),
        'home_run' : pd.pivot_table(season_df, index=index_cols, values='home_run', aggfunc='sum', margins=False),
        'walk' : pd.pivot_table(season_df, index=index_cols, values='walk', aggfunc='sum', margins=False),
        'hit_by_pitch' : pd.pivot_table(season_df, index=index_cols, values='hit_by_pitch', aggfunc='sum', margins=False),
        'sac_fly' : pd.pivot_table(season_df, index=index_cols, values='sac_fly', aggfunc='sum', margins=False),

        'z_in' : pd.pivot_table(season_df, index=index_cols, values='z_in', aggfunc='sum', margins=False),
        'z_swing' : pd.pivot_table(season_df, index=index_cols, values='z_swing', aggfunc='sum', margins=False),
        'z_con' : pd.pivot_table(season_df, index=index_cols, values='z_con', aggfunc='sum', margins=False),
        'z_out' : pd.pivot_table(season_df, index=index_cols, values='z_out', aggfunc='sum', margins=False),
        'o_swing' : pd.pivot_table(season_df, index=index_cols, values='o_swing', aggfunc='sum', margins=False),
        'o_con' : pd.pivot_table(season_df, index=index_cols, values='o_con', aggfunc='sum', margins=False),

        'f_swing' : pd.pivot_table(season_df, index=index_cols, values='f_swing', aggfunc='sum', margins=False),
        # 'f_s' : pd.pivot_table(season_df, index=index_cols, values='f_s', aggfunc='sum', margins=False),
        'f_pitch' : pd.pivot_table(season_df, index=index_cols, values='f_pitch', aggfunc='sum', margins=False),
        'swing' : pd.pivot_table(season_df, index=index_cols, values='swing', aggfunc='sum', margins=False),
        'whiff' : pd.pivot_table(season_df, index=index_cols, values='whiff', aggfunc='sum', margins=False),

        'weak' : pd.pivot_table(season_df, index=index_cols, values='weak', aggfunc='sum', margins=False),
        'topped' : pd.pivot_table(season_df, index=index_cols, values='topped', aggfunc='sum', margins=False),
        'under' : pd.pivot_table(season_df, index=index_cols, values='under', aggfunc='sum', margins=False),
        'flare' : pd.pivot_table(season_df, index=index_cols, values='flare', aggfunc='sum', margins=False),
        'solid_contact' : pd.pivot_table(season_df, index=index_cols, values='solid_contact', aggfunc='sum', margins=False),
        'barrel' : pd.pivot_table(season_df, index=index_cols, values='barrel', aggfunc='sum', margins=False),

        # 'Heart' : pd.pivot_table(season_df, index=index_cols, values='Heart', aggfunc='sum', margins=False),
        # 'Shadow' : pd.pivot_table(season_df, index=index_cols, values='Shadow', aggfunc='sum', margins=False),
        # 'Chase' : pd.pivot_table(season_df, index=index_cols, values='Chase', aggfunc='sum', margins=False),
        # 'Waste' : pd.pivot_table(season_df, index=index_cols, values='Waste', aggfunc='sum', margins=False),
        'S' : pd.pivot_table(season_df, index=index_cols, values='S', aggfunc='sum', margins=False),
    }
    
    # 모든 통계를 하나의 데이터프레임으로 결합
    # 모든 통계를 하나의 데이터프레임으로 결합 (컬럼명 유실 방지를 위해 개별 지정)
    new_stats = {}
    for name, s_df in stats.items():
        if isinstance(s_df, pd.DataFrame):
            if len(s_df.columns) > 0:
                s_df.columns = [name]
                new_stats[name] = s_df
            else:
                # 데이터가 없어 컬럼이 생성되지 않은 경우 빈 시리즈 생성
                new_stats[name] = pd.Series(index=s_df.index, name=name, dtype='float64')
        elif isinstance(s_df, pd.Series):
            s_df.name = name
            new_stats[name] = s_df
        else:
            new_stats[name] = s_df

    review_df = pd.concat(new_stats.values(), axis=1)
    
    review_df['inplay_pit'] = safe_divide(review_df['inplay'], review_df['pitched']).round(3)

    review_df['avg'] = safe_divide(review_df['hit'], review_df['ab'])

    review_df['obp'] = safe_divide(
        review_df['hit'] + review_df['hit_by_pitch'] + review_df['walk'], 
        review_df['ab'] + review_df['hit_by_pitch'] + review_df['walk'] + review_df['sac_fly']
    )

    review_df['slg'] = safe_divide(
        review_df['single']*1 + review_df['double']*2 + review_df['triple']*3 + review_df['home_run']*4,
        review_df['ab']
    )

    review_df['ops'] = review_df['obp'] + review_df['slg']

    review_df['z%'] = safe_divide(review_df['z_in'], review_df['pitched'])
    review_df['z_swing%'] = safe_divide(review_df['z_swing'], review_df['z_in'])
    review_df['z_con%'] = safe_divide(review_df['z_con'], review_df['z_swing'])

    review_df['o%'] = safe_divide(review_df['z_out'], review_df['pitched'])
    review_df['o_swing%'] = safe_divide(review_df['o_swing'], review_df['z_out'])
    review_df['o_con%'] = safe_divide(review_df['o_con'], review_df['o_swing'])

    review_df['f_swing%'] = safe_divide(review_df['f_swing'], review_df['f_pitch'])
    review_df['swing%'] = safe_divide(review_df['swing'], review_df['pitched'])
    review_df['whiff%'] = safe_divide(review_df['whiff'], review_df['swing'])
    review_df['inplay_sw'] = safe_divide(review_df['inplay'], review_df['swing'])

    kbo_z_swing = 0.639
    kbo_o_swing = 0.262

    condition = [
                    (review_df['z_swing%'] >= kbo_z_swing) & (review_df['o_swing%'] >= kbo_o_swing),
                    (review_df['z_swing%'] >= kbo_z_swing) & (review_df['o_swing%'] <= kbo_o_swing),
                    (review_df['z_swing%'] <= kbo_z_swing) & (review_df['o_swing%'] >= kbo_o_swing),
                    (review_df['z_swing%'] <= kbo_z_swing) & (review_df['o_swing%'] <= kbo_o_swing)
                    ]

    choicelist = ['Aggressive','Selective','Non_Selective','Passive']

    review_df['approach'] = np.select(condition, choicelist, default='Not Specified')

    review_df['sum'] = review_df['weak'] + review_df['topped'] + review_df['under'] + review_df['flare'] + review_df['solid_contact'] + review_df['barrel']

    review_df['weak'] = safe_divide(review_df['weak'], review_df['sum'])
    review_df['topped'] = safe_divide(review_df['topped'], review_df['sum'])
    review_df['under'] = safe_divide(review_df['under'], review_df['sum'])
    review_df['flare'] = safe_divide(review_df['flare'], review_df['sum'])
    review_df['solid_contact'] = safe_divide(review_df['solid_contact'], review_df['sum'])
    review_df['barrel'] = safe_divide(review_df['barrel'], review_df['sum'])


    # review_df['Heart%'] = review_df['Heart'] / review_df['pitched']
    # review_df['Shadow%'] = review_df['Shadow'] / review_df['pitched']
    # review_df['Chase%'] = review_df['Chase'] / review_df['pitched']
    # review_df['Waste%'] = review_df['Waste'] / review_df['pitched']
    # review_df['f_s%'] = review_df['f_s'] / review_df['f_pitch']
    review_df['S%'] = safe_divide(review_df['S'] ,review_df['pitched'])





    review_df = review_df[['game','pitched','pa','ab','hit','walk','rel_speed', 'spin_rate', 'ver_break', 'hor_break', 'rel_height', 'rel_side', 'extension', 'spin_axis','inplay_pit','exit_velocity','launch_angleX','hit_spin','obp','slg','avg','ops',
                        'z%','z_swing%','z_con%','o%','o_swing%', 'o_con%', 'f_swing%', 'swing%', 'whiff%','inplay_sw', "S%",
                        'weak','topped','under','flare','solid_contact','barrel','approach'
                        # , 'Heart%', 'Shadow%', 'Chase%', 'Waste%', 'f_s%', 'S%'
                        ]]
    review_df = review_df.round({
        'rel_speed':1, 'exit_velocity':1, 'launch_angleX':1, 'hit_spin':0, 'rel_speed':1,'spin_rate':0, 'ver_break':1, 'hor_break':1, 'rel_height':2, 'rel_side':2, 'extension':2,
        'avg':3, 'obp':3, 'slg':3, 'ops':3,
        'z%':3, 'z_swing%':3, 'z_con%':3, 'o%':3, 'o_swing%':3, 'o_con%':3,
        'f_swing%':3, 'swing%':3, 'whiff%':3, 'inplay_sw':3, 'S%' : 3,
        'weak':3, 'topped':3, 'under':3, 'flare':3, 'solid_contact':3, 'barrel':3,
        'approach':3
    })

    percent_cols = [
        'z%', 'z_swing%', 'z_con%', 'o%', 'o_swing%', 'o_con%', 'f_swing%', 
        'swing%', 'whiff%', 'inplay_sw','S%', 'weak','topped','under','flare','solid_contact','barrel'
    ]

    for col in percent_cols:
        if col in review_df.columns:
            review_df[col] = (review_df[col] * 100).round(1).astype(str) + '%'


    # reindex 부분 수정
    for col in index_cols:
        if col in reindex_options:
            valid_idx = [v for v in reindex_options[col] if v in review_df.index.get_level_values(col)]
            review_df = review_df.reindex(valid_idx, level=col)

    return review_df


    
def create_series_stats(df, indexes={}):
    """
    df: 데이터프레임
    indexes: 사용할 인덱스 정의 딕셔너리
    """

    # reindex 설정을 딕셔너리로 정의
    reindex_options = {
        'game_year': [2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019],
        'level': ['MAJOR', 'AAA', 'KoreaBaseballOrganization', 'KBO Minors','NPB', 'NPM'],
        'pitch_name': ['4-Seam Fastball','2-Seam Fastball','Cutter','Slider','Curveball','Sweeper','Changeup','Split-Finger', 'ALL'],
        'p_kind': ['Fastball', 'Breaking', 'Off_Speed'],
        'stand': ['R','L'],
        'p_throws' : ['R', 'L', 'S'],
        'p_throw' : ['R','L']
    }

    
    # 조건 필터링
    season_df = df.copy()
    index_cols = []
    # 디버깅을 위한
  
    # 그 다음 indexes 설정
    for col, description in indexes.items():
        # if col != 'level':  # level은 마지막에 추가
        index_cols.append(col)
    
    
    # 전체 데이터가 없는 경우
    if len(season_df) == 0:
        return "조건에 맞는 데이터가 없습니다. 입력한 조건들을 확인해주세요."
    
    # 최소 데이터 수 확인 (예: 10개 미만인 경우 경고)
    if len(season_df) < 10:
        return f"데이터가 너무 적습니다 (현재 {len(season_df)}개). 더 많은 데이터가 필요할 수 있습니다."

    
    # level은 항상 마지막 인덱스로 추가
    # index_cols.append('level')
    
    # 기존 피벗 테이블 생성 코드를 함수로 정리
    stats = {
        'game': pd.pivot_table(season_df, index=index_cols, values='game_date', aggfunc='nunique', margins=False),
        'pitched': pd.pivot_table(season_df, index=index_cols, values='game_date', aggfunc='count', margins=False),
        'rel_speed': pd.pivot_table(season_df, index=index_cols, values='rel_speed(km)', aggfunc='mean', margins=False),

        'inplay' : pd.pivot_table(season_df, index=index_cols, values='inplay', aggfunc='sum', margins=False),
        'exit_velocity' : pd.pivot_table(season_df, index=index_cols, values='exit_velocity', aggfunc='mean', margins=False),
        'launch_angleX' : pd.pivot_table(season_df, index=index_cols, values='launch_angleX', aggfunc='mean', margins=False),
        'hit_spin' : pd.pivot_table(season_df, index=index_cols, values='hit_spin', aggfunc='mean', margins=False),
        # 🎯 EV50 계산 (groupby_key 사용)
        'ev50' : pd.pivot_table(
            season_df[season_df.groupby(index_cols)['exit_velocity'].transform('median') <= season_df['exit_velocity']], 
            index=index_cols, 
            values='exit_velocity', 
            aggfunc='mean', 
            margins=False
        ).rename(columns={'exit_velocity': 'ev50'}),
        'avg_bat_speed': pd.pivot_table(
            season_df[season_df.groupby(index_cols)['BatSpeed'].transform(lambda x: x.quantile(0.1)) <= season_df['BatSpeed']],
            index=index_cols,
            values='BatSpeed',
            aggfunc='mean',
            margins=False
        ).rename(columns={'BatSpeed': 'avg_bat_speed'}),
        'hit' : pd.pivot_table(season_df, index=index_cols, values='hit', aggfunc='sum', margins=False),
        'ab' : pd.pivot_table(season_df, index=index_cols, values='ab', aggfunc='sum', margins=False),
        'pa' : pd.pivot_table(season_df, index=index_cols, values='pa', aggfunc='sum', margins=False),
        'single' : pd.pivot_table(season_df, index=index_cols, values='single', aggfunc='sum', margins=False),
        'double' : pd.pivot_table(season_df, index=index_cols, values='double', aggfunc='sum', margins=False),
        'triple' : pd.pivot_table(season_df, index=index_cols, values='triple', aggfunc='sum', margins=False),
        'home_run' : pd.pivot_table(season_df, index=index_cols, values='home_run', aggfunc='sum', margins=False),
        'walk' : pd.pivot_table(season_df, index=index_cols, values='walk', aggfunc='sum', margins=False),
        'hit_by_pitch' : pd.pivot_table(season_df, index=index_cols, values='hit_by_pitch', aggfunc='sum', margins=False),
        'sac_fly' : pd.pivot_table(season_df, index=index_cols, values='sac_fly', aggfunc='sum', margins=False),

        'z_in' : pd.pivot_table(season_df, index=index_cols, values='z_in', aggfunc='sum', margins=False),
        'z_swing' : pd.pivot_table(season_df, index=index_cols, values='z_swing', aggfunc='sum', margins=False),
        'z_con' : pd.pivot_table(season_df, index=index_cols, values='z_con', aggfunc='sum', margins=False),
        'z_out' : pd.pivot_table(season_df, index=index_cols, values='z_out', aggfunc='sum', margins=False),
        'o_swing' : pd.pivot_table(season_df, index=index_cols, values='o_swing', aggfunc='sum', margins=False),
        'o_con' : pd.pivot_table(season_df, index=index_cols, values='o_con', aggfunc='sum', margins=False),

        'f_swing' : pd.pivot_table(season_df, index=index_cols, values='f_swing', aggfunc='sum', margins=False),
        # 'f_s' : pd.pivot_table(season_df, index=index_cols, values='f_s', aggfunc='sum', margins=False),
        'f_pitch' : pd.pivot_table(season_df, index=index_cols, values='f_pitch', aggfunc='sum', margins=False),
        'swing' : pd.pivot_table(season_df, index=index_cols, values='swing', aggfunc='sum', margins=False),
        'whiff' : pd.pivot_table(season_df, index=index_cols, values='whiff', aggfunc='sum', margins=False),

        'weak' : pd.pivot_table(season_df, index=index_cols, values='weak', aggfunc='sum', margins=False),
        'topped' : pd.pivot_table(season_df, index=index_cols, values='topped', aggfunc='sum', margins=False),
        'under' : pd.pivot_table(season_df, index=index_cols, values='under', aggfunc='sum', margins=False),
        'flare' : pd.pivot_table(season_df, index=index_cols, values='flare', aggfunc='sum', margins=False),
        'solid_contact' : pd.pivot_table(season_df, index=index_cols, values='solid_contact', aggfunc='sum', margins=False),
        'barrel' : pd.pivot_table(season_df, index=index_cols, values='barrel', aggfunc='sum', margins=False),

        
    }
    
    # 모든 통계를 하나의 데이터프레임으로 결합
    # 모든 통계를 하나의 데이터프레임으로 결합 (컬럼명 유실 방지를 위해 개별 지정)
    new_stats = {}
    for name, s_df in stats.items():
        if isinstance(s_df, pd.DataFrame):
            if len(s_df.columns) > 0:
                s_df.columns = [name]
                new_stats[name] = s_df
            else:
                # 데이터가 없어 컬럼이 생성되지 않은 경우 빈 시리즈 생성
                new_stats[name] = pd.Series(index=s_df.index, name=name, dtype='float64')
        elif isinstance(s_df, pd.Series):
            s_df.name = name
            new_stats[name] = s_df
        else:
            new_stats[name] = s_df

    review_df = pd.concat(new_stats.values(), axis=1)
    
    review_df['inplay_pit'] = safe_divide(review_df['inplay'], review_df['pitched']).round(3)

    review_df['avg'] = safe_divide(review_df['hit'], review_df['ab'])

    review_df['obp'] = safe_divide(
        review_df['hit'] + review_df['hit_by_pitch'] + review_df['walk'], 
        review_df['ab'] + review_df['hit_by_pitch'] + review_df['walk'] + review_df['sac_fly']
    )

    review_df['slg'] = safe_divide(
        review_df['single']*1 + review_df['double']*2 + review_df['triple']*3 + review_df['home_run']*4,
        review_df['ab']
    )

    review_df['ops'] = review_df['obp'] + review_df['slg']

    review_df['z%'] = safe_divide(review_df['z_in'], review_df['pitched'])
    review_df['z_swing%'] = safe_divide(review_df['z_swing'], review_df['z_in'])
    review_df['z_con%'] = safe_divide(review_df['z_con'], review_df['z_swing'])

    review_df['o%'] = safe_divide(review_df['z_out'], review_df['pitched'])
    review_df['o_swing%'] = safe_divide(review_df['o_swing'], review_df['z_out'])
    review_df['o_con%'] = safe_divide(review_df['o_con'], review_df['o_swing'])

    review_df['f_swing%'] = safe_divide(review_df['f_swing'], review_df['f_pitch'])
    review_df['swing%'] = safe_divide(review_df['swing'], review_df['pitched'])
    review_df['whiff%'] = safe_divide(review_df['whiff'], review_df['swing'])
    review_df['inplay_sw'] = safe_divide(review_df['inplay'], review_df['swing'])

    kbo_z_swing = 0.639
    kbo_o_swing = 0.262

    condition = [
                    (review_df['z_swing%'] >= kbo_z_swing) & (review_df['o_swing%'] >= kbo_o_swing),
                    (review_df['z_swing%'] >= kbo_z_swing) & (review_df['o_swing%'] <= kbo_o_swing),
                    (review_df['z_swing%'] <= kbo_z_swing) & (review_df['o_swing%'] >= kbo_o_swing),
                    (review_df['z_swing%'] <= kbo_z_swing) & (review_df['o_swing%'] <= kbo_o_swing)
                    ]

    choicelist = ['Aggressive','Selective','Non_Selective','Passive']

    review_df['approach'] = np.select(condition, choicelist, default='Not Specified')

    review_df['sum'] = review_df['weak'] + review_df['topped'] + review_df['under'] + review_df['flare'] + review_df['solid_contact'] + review_df['barrel']

    review_df['weak'] = safe_divide(review_df['weak'], review_df['sum'])
    review_df['topped'] = safe_divide(review_df['topped'], review_df['sum'])
    review_df['under'] = safe_divide(review_df['under'], review_df['sum'])
    review_df['flare'] = safe_divide(review_df['flare'], review_df['sum'])
    review_df['solid_contact'] = safe_divide(review_df['solid_contact'], review_df['sum'])
    review_df['barrel'] = safe_divide(review_df['barrel'], review_df['sum'])

    # review_df['S%'] = review_df['S'] / review_df['pitched']





    review_df = review_df[['exit_velocity','launch_angleX', 'ev50',
                        'z%','z_swing%','z_con%','o%','o_swing%', 'o_con%', 'f_swing%', 'swing%', 'whiff%','inplay_sw',
                        'weak','topped','under','flare','solid_contact','barrel' ]]

    review_df = review_df.round({
        'rel_speed':1, 'exit_velocity':1, 'launch_angleX':1, 'hit_spin':0, 'ev50':1,
        'avg':3, 'obp':3, 'slg':3, 'ops':3,
        'z%':3, 'z_swing%':3, 'z_con%':3, 'o%':3, 'o_swing%':3, 'o_con%':3,
        'f_swing%':3, 'swing%':3, 'whiff%':3, 'inplay_sw':3,
        'weak':3, 'topped':3, 'under':3, 'flare':3, 'solid_contact':3, 'barrel':3,
        'approach':3
    })

    percent_cols = [
        'z%', 'z_swing%', 'z_con%', 'o%', 'o_swing%', 'o_con%', 'f_swing%',
        'swing%', 'whiff%', 'inplay_sw', 'weak','topped','under','flare','solid_contact','barrel'
    ]

    for col in percent_cols:
        if col in review_df.columns:
            review_df[col] = (review_df[col] * 100).round(1).astype(str) + '%'

    for col in index_cols:
        if col in reindex_options:
            valid_idx = [v for v in reindex_options[col] if v in review_df.index.get_level_values(col)]
            review_df = review_df.reindex(valid_idx, level=col)

    return review_df


class BattingConfig:
    # 기본 기준값 (공통)
    DEFAULT_HARD_HIT = 150
    
    # 선수별 특수 기준 (필요한 경우)
    # 예: {batter_id: threshold}
    PLAYER_SPECIFIC_THRESHOLD = {
        50066 : 148 , 69064 : 153 , 51003 : 153 , 64004 : 150 , 
        79402 : 145 , 53036 : 145 , 64007 : 158 , 76290 : 153 ,
        64166 : 158 , 53057 : 145 , 64504 : 158 , 63722 : 145 ,
        53058 : 142 , 51007 : 153 , 66606 : 148 , 656541 : 155 ,
        64115 : 153 , 78548 : 158 , 67006 : 140 , 56006 : 145 ,
        51013 : 145 , 79240 : 148 , 52001 : 153 , 67644 : 145
    }

    @classmethod
    def get_hard_hit_threshold(cls, batter_id=None):
        """
        batter_id를 넣으면 해당 선수의 기준값을, 
        없거나 등록되지 않았으면 기본값을 반환합니다.
        """
        return cls.PLAYER_SPECIFIC_THRESHOLD.get(batter_id, cls.DEFAULT_HARD_HIT)


class PitchConfig:
    """구종명 한글 매핑 클래스"""
    PITCH_NAME_MAP = {
        '4-Seam Fastball': '포심',
        '2-Seam Fastball': '투심',
        'Cutter': '커터',
        'Slider': '슬라이더',
        'Curveball': '커브',
        'Sweeper': '스위퍼',
        'Changeup': '체인지업',
        'Split-Finger': '스플리터',
        'Sinker': '싱커',
        'Slurve': '슬러브',
        'Knuckle Curve': '너클커브',
        'Forkball': '포크볼',
        'Eephus': '이퍼스',
        'Screwball': '스크루볼',
        'Knuckleball': '너클볼',
        'Other': '기타'
    }

class DesConfig:
    """투구내용 한글 매핑 클래스"""
    DES_NAME_MAP = {
        'ball' : '볼', 
        'foul' : '파울', 
        'called_strike' : '스트라이크', 
        'hit_into_play' : '인플레이',
        'swinging_strike' : '헛스윙',
        'hit_into_play_no_out' : '인플레이', 
        'hit_into_play_score' : '인플레이',
        'hit_by_pitch' : 'HP',
        'pitchout' : '피치아웃'
    }

class DesConfigENG:
    """투구내용 한글 매핑 클래스"""
    DES_NAME_MAP = {
        'ball' : 'ball', 
        'foul' : 'foul', 
        'called_strike' : 'strike', 
        'hit_into_play' : 'inplay',
        'swinging_strike' : 'whiff',
        'hit_into_play_no_out' : 'inplay', 
        'hit_into_play_score' : 'inplay',
        'hit_by_pitch' : 'HP',
        'pitchout' : 'pitchout'
    }

class EventsConfig:
    """타격결과 한글 매핑 클래스"""
    EVENT_NAME_MAP = {
        'field_out' : '필드아웃', 
        'single' : '안타', 
        'strikeout' : '삼진', 
        'double' : '2루타', 
        'walk' : '볼넷',
        'field_error' : '실책', 
        'hit_by_pitch' : 'HP', 
        'home_run' : '홈런', 
        'sac_fly' : '희생플라이', 
        'triple' : '3루타',
        'sac_bunt' : '희생번트', 
        'fielders_choice_out' : '야수선택'
    }


class TeamConfig:
    """팀명 한글 매핑 클래스"""
    TEAM_NAME_MAP = {
        'SAM_LIO' : '삼성',
        'KIW_HER' : '키움',
        'LOT_GIA' : '롯데',
        'SSG_LAN' : 'SSG',
        'KIA_TIG' : 'KIA',
        'DOO_BEA' : '두산',
        'LG_TWI' : 'LG',
        'NC_DIN' : 'NC',
        'HAN_EAG' : '한화',
        'KT_WIZ' : 'KT'
    }