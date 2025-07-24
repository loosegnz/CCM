import streamlit as st
import sys
import io
from copy import deepcopy
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# 加载 ttf 字体
my_font = fm.FontProperties(fname='SimHei.ttf')

# 获取字体名，并设置到 rcParams 中
plt.rcParams['font.sans-serif'] = [my_font.get_name()]
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['axes.edgecolor'] = 'grey'
plt.rcParams['axes.linewidth'] = 1.0

print("当前字体名：", my_font.get_name())
# --- PLOTTING FUNCTIONS ---
# Each function now takes the matplotlib axes object `ax` and `params` dictionary as arguments.

def plot_sharkfin_call(ax, params):
    strike = params['strike']
    knock_out = params['knock_out']
    participation_rate = params['participation_rate']
    min_ret = params['min_ret']
    max_ret = params['max_ret']
    knock_ret = params['knock_ret']
    month = params['month']
    asset = params['asset']
    cost = params['cost']
    type0 = params['type']
    
    ax.set_ylim(-1, max_ret + 2)
    
    ax.plot([strike * 0.9, strike, knock_out], [min_ret, min_ret, max_ret],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)
    
    ax.plot([knock_out, knock_out * 1.05], [knock_ret, knock_ret],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)
    
    for x, y in zip([strike * 0.9, strike, knock_out], [min_ret, min_ret, max_ret]):
        ax.text(x, y + 0.1, f'{y:.2f}%', ha='center', va='bottom', color='black', fontsize=12)
    
    ax.text((strike + knock_out) / 2 - 0.5, max_ret / 2 + 0.2, f'参与率{participation_rate:,.1f}%',
            ha='left', va='center', color='black', fontsize=12)
    if type0 == '单鲨':
        ax.text(knock_out * 1.01, knock_ret + 0.3, f'敲出{knock_ret:,.2f}%',
                ha='left', va='center', color='black', fontsize=12)
    
    ax.set_xlabel('标的期末价格/期初价格', ha='right', fontsize=10, labelpad=15)
    ax.set_xticks([strike, knock_out])
    ax.set_xticklabels([f'{strike:g}%', f'{knock_out:g}%'], fontsize=11)
    ax.set_yticks([min_ret, max_ret])
    ax.set_yticklabels([f'{min_ret}%', f'{max_ret}%'], fontsize=11)
    
    title_text = f'{month}美式看涨单鲨（每日观察）-{asset}' if type0 == '单鲨' else f'{month}欧式看涨价差（期末观察一次）-{asset}'
    ax.set_title(f'{title_text}\n业绩报酬计提基准（年化)-费率{cost}%',
                 fontsize=14, pad=20, color='#2C3E50')
    
    ax.grid(linestyle=':', alpha=0.5, axis='both')
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(100, color='black', linewidth=0.8)
    ax.legend(['收益结构曲线'], loc='upper left', fontsize=10, frameon=False)

def plot_sharkfin_put(ax, params):
    strike = params['strike']
    knock_out = params['knock_out']
    participation_rate = params['participation_rate']
    min_ret = params['min_ret']
    max_ret = params['max_ret']
    knock_ret = params['knock_ret']
    month = params['month']
    asset = params['asset']
    cost = params['cost']
    type0 = params['type']

    ax.set_ylim(-1, max_ret + 2)

    ax.plot([knock_out * 0.9, knock_out], [knock_ret, knock_ret],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)
    ax.plot([knock_out, strike], [max_ret, min_ret],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)
    ax.plot([strike, strike * 1.1], [min_ret, min_ret],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)

    for x, y in zip([knock_out, strike, strike*1.1], [max_ret, min_ret, min_ret]):
        ax.text(x, y + 0.1, f'{y:.2f}%', ha='center', va='bottom', color='black', fontsize=12)

    ax.text((strike + knock_out) / 2, max_ret * 2 / 3, f'参与率{participation_rate:.1f}%',
            ha='left', va='center', color='black', fontsize=12)
    if type0 == '单鲨':
        ax.text(knock_out * 0.95, knock_ret * 1.1, f'敲出{knock_ret:,.2f}%',
                ha='left', va='center', color='black', fontsize=12)

    ax.set_xlabel('标的期末价格/期初价格', ha='right', fontsize=10, labelpad=10)
    ax.set_xticks([strike, knock_out])
    ax.set_xticklabels([f'{strike:g}%', f'{knock_out:g}%'], fontsize=11)
    ax.set_yticks([min_ret, max_ret])
    ax.set_yticklabels([f'{min_ret:g}%', f'{max_ret:g}%'], fontsize=11)

    opt_title = '美式看跌单鲨（每日观察）' if type0 == '单鲨' else '欧式看跌价差（期末观察一次）'
    ax.set_title(f'{month} {opt_title}-{asset}\n业绩报酬计提基准（年化)-费率{cost}%',
                 fontsize=14, pad=20, color='#2C3E50')

    ax.grid(linestyle=':', alpha=0.5, axis='both')
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(100, color='black', linewidth=0.8)
    ax.legend(['收益结构曲线'], loc='upper left', fontsize=10, frameon=False)

def plot_snowball(ax, params):
    knock_in = params['knock_in']
    knock_out = params['knock_out']
    ret1 = params['ret1']
    ret2 = params['ret2']
    ret3 = params['ret3']
    month = params['month']
    asset = params['asset']
    cost = params['cost']
    
    ax.set_ylim(-1, ret3 + 2)
    
    ax.plot([knock_in * 0.8, knock_in], [ret1, ret1],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)
    ax.plot([knock_in, knock_out], [ret2, ret2],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)
    ax.plot([knock_out, knock_out * 1.2], [ret3, ret3],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)

    ax.text(knock_in * 0.8, ret1 + 0.5, f'保底收益{ret1:,.2f}%',
            ha='left', va='center', color='black', fontsize=12)
    ax.text(knock_in + 3, ret2 + 0.5, f'未敲入未敲出收益{ret2:,.2f}%',
            ha='left', va='center', color='black', fontsize=12)
    ax.text(knock_out * 1.05, ret3 + 0.5, f'敲出收益{ret3:,.2f}%',
            ha='left', va='center', color='black', fontsize=12)
    
    ax.set_xlabel('敲出观察日价格/期初价格', ha='left', fontsize=10, labelpad=15)
    ax.set_xticks([knock_in, knock_out])
    ax.set_xticklabels([f'{knock_in}%', f'{knock_out}%'], fontsize=11)
    ax.set_yticks([ret1, ret2, ret3])
    ax.set_yticklabels([f'{ret1}%', f'{ret2}%', f'{ret3}%'], fontsize=11)

    ax.set_title(f'{month}三元小雪球（每月观察敲出）-{asset}\n业绩报酬计提基准（年化)-费率{cost}%',
                 fontsize=14, pad=20, color='#2C3E50')

    ax.grid(linestyle=':', alpha=0.5, axis='both')
    ax.axhline(0, color='black', linewidth=0.8)
    ax.legend(['收益结构曲线'], loc='upper left', fontsize=10, frameon=False)

def plot_snowball2(ax, params):
    knock_in = params['knock_in']
    knock_out = params['knock_out']
    ret1 = params['ret1']
    ret3 = params['ret3']
    month = params['month']
    asset = params['asset']
    cost = params['cost']

    ax.set_ylim(-1, ret3 + 2)

    ax.plot([knock_in * 0.9, knock_out], [ret1, ret1],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)
    ax.plot([knock_out, knock_out * 1.2], [ret3, ret3],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)

    ax.text(knock_in * 0.95, ret1 + 0.5, f'未敲出收益{ret1:,.2f}%',
            ha='left', va='center', color='black', fontsize=12)
    ax.text(knock_out * 1.05, ret3 + 0.5, f'敲出收益{ret3:,.2f}%',
            ha='left', va='center', color='black', fontsize=12)
    
    ax.set_xlabel('敲出观察日价格/期初价格', ha='left', fontsize=10, labelpad=15)
    ax.set_xticks([knock_out])
    ax.set_xticklabels([f'{knock_out}%'], fontsize=12)
    ax.set_yticks([ret1, ret3])
    ax.set_yticklabels([f'{ret1}%', f'{ret3}%'], fontsize=11)

    ax.set_title(f'{month}看涨敲出（期末观察一次）-{asset}\n业绩报酬计提基准（年化)-费率{cost}%',
                 fontsize=14, pad=20, color='#2C3E50')
    ax.grid(linestyle=':', alpha=0.5, axis='both')
    ax.axhline(0, color='black', linewidth=0.8)
    ax.legend(['收益结构曲线'], loc='upper left', fontsize=10, frameon=False)

def plot_call(ax, params):
    strike = params['strike']
    participation_rate = params['participation_rate']
    min_ret = params['min_ret']
    month = params['month']
    asset = params['asset']
    cost = params['cost']

    rise1 = 1.1
    ret1 = min_ret + participation_rate * (rise1 - 1)
    rise2 = 1.15
    ret2 = min_ret + participation_rate * (rise2 - 1)
    
    ax.set_ylim(-1, ret2 + 2)

    ax.plot([strike * 0.9, strike], [min_ret, min_ret],
            marker='o', linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)
    ax.plot([strike, strike * rise1, strike * rise2], [min_ret, ret1, ret2],
            linestyle='-', color='#FF6B6B',
            linewidth=2, markersize=5)

    for x, y in zip([strike * 0.9, strike], [min_ret, min_ret]):
        ax.text(x, y + 0.1, f'{y:.2f}%', ha='center', va='bottom', color='black', fontsize=12)

    ax.text((strike + rise2 * 100) / 2, ret2 / 2, f'参与率{participation_rate:.2f}%',
            ha='left', va='center', color='black', fontsize=12)
    
    ax.set_xlabel('标的期末价格/期初价格', ha='right', fontsize=10, labelpad=15)
    ax.set_xticks([strike])
    ax.set_xticklabels([f'{strike}%'], fontsize=11)
    ax.set_yticks([min_ret])
    ax.set_yticklabels([f'{min_ret}%'], fontsize=11)

    ax.set_title(f'{month}看涨香草-{asset}\n业绩报酬计提基准（年化)-费率{cost}%',
                 fontsize=14, pad=20, color='#2C3E50')

    ax.grid(linestyle=':', alpha=0.5, axis='both')
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(100, color='black', linewidth=0.8)
    ax.legend(['收益结构曲线'], loc='upper left', fontsize=10, frameon=False)

# --- PARSING LOGIC ---
def parse_parameters(text):
    """Parses tab-separated text and updates the session state."""
    if not text:
        return
    
    try:
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if len(lines) < 2 or '\t' not in lines[1]:
            st.error("解析失败：请粘贴包含表头和数据的两行以上表格文本。")
            return

        headers = lines[0].split('\t')
        values = lines[1].split('\t')
        
        parsed_params = {}
        structure_type_str = None

        for header, value in zip(headers, values):
            header = header.strip().lower()
            value = value.strip()
            
            if not value or value == '-': continue

            if '结构' in header:
                structure_type_str = value
            elif '标的' in header:
                parsed_params['asset'] = value
            elif '期限' in header:
                parsed_params['month'] = value.replace('天', 'D').replace('月', 'M')
            elif '行权价' in header:
                parsed_params['strike'] = float(value.replace('%', ''))
            elif '障碍价' in header or '敲出价' in header:
                parsed_params['knock_out'] = float(value.replace('%', ''))
            elif '敲入价' in header:
                parsed_params['knock_in'] = float(value.replace('%', ''))
            elif '保底年化收益' in header and not '期权' in header:
                parsed_params['min_ret'] = float(value.replace('%', ''))
            elif '敲出年化收益' in header and not '期权' in header:
                parsed_params['knock_ret'] = float(value.replace('%', ''))
            elif '未敲入未敲出收益' in header:
                parsed_params['ret2'] = float(value.replace('%', ''))
            elif '敲入未敲出收益' in header:
                parsed_params['ret1'] = float(value.replace('%', ''))
            elif '敲出收益' in header and not '敲入' in header:
                parsed_params['ret3'] = float(value.replace('%', ''))
            elif '参与率' in header:
                parsed_params['participation_rate'] = float(value.replace('%', ''))
            elif '最高收益' in header:
                parsed_params['max_ret'] = float(value.replace('%', ''))
            elif '管理费' in header or '期权费' in header:
                parsed_params['cost'] = float(value.replace('%', '').split('/')[0])
        
        # Determine and switch option type
        if structure_type_str:
            structure_mapping = {
                '三元': '三元小雪球', '看涨敲出': '看涨敲出', '看涨香草': '看涨香草',
                '单鲨': '看涨单鲨/价差' if '看涨' in structure_type_str else '看跌单鲨/价差',
                '价差': '看涨单鲨/价差' if '看涨' in structure_type_str else '看跌单鲨/价差'
            }
            matched_type = None
            for key, type_name in structure_mapping.items():
                if key in structure_type_str:
                    matched_type = type_name
                    break
            
            if matched_type and matched_type in st.session_state.option_types:
                st.session_state.current_option = matched_type

        # Update params for the current (possibly new) option type
        current_params_dict = st.session_state.option_types[st.session_state.current_option]['params']
        for key, value in parsed_params.items():
            if key in current_params_dict:
                current_params_dict[key] = value
        
        st.toast("参数解析成功！")

    except Exception as e:
        st.error(f"解析参数时出错: {e}")


# --- INITIAL DATA & SESSION STATE ---

def get_initial_data():
    """Returns the initial dictionary of option types and their parameters."""
    return {
        '看涨单鲨/价差': {
            'params': {'strike': 102.0, 'knock_out': 108.0, 'participation_rate': 49.2, 'min_ret': 1.8, 'max_ret': 4.38, 'knock_ret': 1.8, 'month': '2025-07', 'asset': '沪深300指数', 'cost': 0.42, 'type': '单鲨'},
            'plot_func': plot_sharkfin_call
        },
        '看跌单鲨/价差': {
            'params': {'strike': 100.0, 'knock_out': 90.0, 'participation_rate': 42.0, 'min_ret': 1.0, 'max_ret': 5.2, 'knock_ret': 2.25, 'month': '3M', 'asset': '黄金现货9999', 'cost': 0.42, 'type': '单鲨'},
            'plot_func': plot_sharkfin_put
        },
        '三元小雪球': {
            'params': {'knock_in': 80.0, 'knock_out': 100.0, 'ret1': 0.2, 'ret2': 4.0, 'ret3': 4.2, 'month': '24M', 'asset': '中证1000', 'cost': 0.42},
            'plot_func': plot_snowball
        },
        '看涨敲出': {
            'params': {'knock_in': 100.0, 'knock_out': 101.0, 'ret1': 0.2, 'ret3': 4.15, 'month': '6M', 'asset': '黄金9999', 'cost': 0.22},
            'plot_func': plot_snowball2
        },
        '看涨香草': {
            'params': {'strike': 100.0, 'participation_rate': 37.0, 'min_ret': 0.05, 'month': '10M', 'asset': '中证1000', 'cost': 0.42},
            'plot_func': plot_call
        }
    }

def initialize_state():
    """Initializes session state on the first run."""
    if 'initialized' not in st.session_state:
        initial_data = get_initial_data()
        st.session_state.option_types = deepcopy(initial_data)
        st.session_state.current_option = '看涨单鲨/价差'
        st.session_state.initialized = True
        st.session_state.parse_text = ""

# --- MAIN APP ---

def main():
    st.set_page_config(page_title="期权结构图", layout="wide")
    initialize_state()
    
    st.title("期权结构图生成器")

    # --- Sidebar for Parameter Controls ---
    with st.sidebar:
        st.header("参数设置")
        
        # Get the dictionary of parameters for the currently selected option
        params = st.session_state.option_types[st.session_state.current_option]['params']
        
        # Dynamically create widgets for each parameter
        # The value from the widget directly updates the session state dictionary
        if 'strike' in params:
            params['strike'] = st.number_input("行权价(%)", value=params['strike'])
        if 'knock_in' in params:
            params['knock_in'] = st.number_input("敲入价(%)", value=params['knock_in'])
        if 'knock_out' in params:
            params['knock_out'] = st.number_input("敲出价(%)", value=params['knock_out'])
        if 'participation_rate' in params:
            params['participation_rate'] = st.number_input("参与率(%)", value=params['participation_rate'])
        if 'min_ret' in params:
            params['min_ret'] = st.number_input("最低收益(%)", value=params['min_ret'])
        if 'max_ret' in params:
            params['max_ret'] = st.number_input("最高收益(%)", value=params['max_ret'])
        if 'knock_ret' in params:
            params['knock_ret'] = st.number_input("敲出收益(%)", value=params['knock_ret'])
        if 'ret1' in params:
            params['ret1'] = st.number_input("保底/敲入未敲出收益(%)", value=params['ret1'])
        if 'ret2' in params:
            params['ret2'] = st.number_input("中间/未敲入未敲出收益(%)", value=params['ret2'])
        if 'ret3' in params:
            params['ret3'] = st.number_input("敲出收益(%)", value=params['ret3'])
        
        params['month'] = st.text_input("期限", value=params['month'])
        params['asset'] = st.text_input("标的资产", value=params['asset'])
        params['cost'] = st.number_input("费率(%)", value=params['cost'])
        
        if 'type' in params:
            type_options = ['单鲨', '价差']
            params['type'] = st.selectbox("单鲨/价差", options=type_options, index=type_options.index(params['type']))

    # --- Main Panel for Selection, Parsing, and Plot ---
    
    # Let user select the option type
    st.selectbox(
        "选择期权类型",
        options=list(st.session_state.option_types.keys()),
        key='current_option', # This key binds the widget's state to the session state key
        label_visibility="collapsed"
    )

    # Area for parsing parameters from pasted text
    with st.expander("📝 从文本解析参数", expanded=True):
        st.text_area("在此粘贴参数表格 (通常是Excel中的两行，包含表头和数据)", height=100, key="parse_text")
        if st.button("一键解析"):
            parse_parameters(st.session_state.parse_text)
            # After parsing, we rerun the script to ensure all widgets are updated
            st.rerun()

    # --- Plotting Area ---
    col1, col2 = st.columns([5, 1]) # Create columns to align plot and download button
    
    with col1:
        # Create the plot
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Get the current plotting function and parameters from session state
        plot_func = st.session_state.option_types[st.session_state.current_option]['plot_func']
        current_params = st.session_state.option_types[st.session_state.current_option]['params']
        
        # Execute the plotting function
        plot_func(ax, current_params)
        fig.tight_layout()
        st.pyplot(fig)

if __name__ == "__main__":
    main()