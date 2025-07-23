import sys
import io
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QGroupBox, QFormLayout, QComboBox,
                             QScrollArea)
from PyQt5.QtGui import QPixmap, QImage, QDoubleValidator, QFont
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt


class OptionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("期权结构图")
        self.setGeometry(100, 100, 300, 300)

        self.font = QFont()
        self.font.setPointSize(10)
        
        # 初始化参数
        self.option_types = {
            '看涨单鲨/价差': {
                'params': {
                    'strike': 102,
                    'knock_out': 108,
                    'participation_rate': 49.2,
                    'min_ret': 1.8,
                    'max_ret': 4.38,
                    'knock_ret': 1.8,
                    'month': '2025-07',
                    'asset': '沪深300指数',
                    'cost': 0.42,
                    'type': '单鲨'
                },
                'plot_func': self.plot_sharkfin_call
            },
            '看跌单鲨/价差': {
                'params': {
                    'strike': 100,
                    'knock_out': 90,
                    'participation_rate': 42,
                    'min_ret': 1,
                    'max_ret': 5.2,
                    'knock_ret': 2.25,
                    'month': '3M',
                    'asset': '黄金现货9999',
                    'cost': 0.42,
                    'type': '单鲨'
                },
                'plot_func': self.plot_sharkfin_put
            },
            '三元小雪球': {
                'params': {
                    'knock_in': 80,
                    'knock_out': 100,
                    'ret1': 0.2,
                    'ret2': 4,
                    'ret3': 4.2,
                    'month': '24M',
                    'asset': '中证1000',
                    'cost': 0.42
                },
                'plot_func': self.plot_snowball
            },
            '看涨敲出': {
                'params': {
                    'knock_in': 100,
                    'knock_out': 101,
                    'ret1': 0.2,
                    'ret3': 4.15,
                    'month': '6M',
                    'asset': '黄金9999',
                    'cost': 0.22
                },
                'plot_func': self.plot_snowball2
            },
            '看涨香草': {
                'params': {
                    'strike': 100,
                    'participation_rate': 37,
                    'min_ret': 0.05,
                    'month': '10M',
                    'asset': '中证1000',
                    'cost': 0.42,
                },
                'plot_func': self.plot_call
            }
        }
        
        self.current_option = '看涨单鲨/价差'
        self.params = self.option_types[self.current_option]['params'].copy()
        
        # 创建UI
        self.init_ui()
        
        # 初始绘图
        self.update_plot()
    
    def init_ui(self):
        # 主布局
        main_widget = QWidget()
        main_layout = QHBoxLayout()  # 改为水平布局
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 左侧区域 - 图表和控制按钮
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        # 期权类型选择
        type_group = QGroupBox("期权类型")
        type_group.setFont(self.font)
        type_layout = QHBoxLayout()
        type_group.setLayout(type_layout)
        
        self.type_combo = QComboBox()
        self.type_combo.setFont(self.font)
        self.type_combo.setMinimumHeight(32)
        self.type_combo.addItems(self.option_types.keys())
        self.type_combo.currentTextChanged.connect(self.change_option_type)
            
        type_layout.addWidget(self.type_combo)
        
        left_layout.addWidget(type_group)

        # 添加文本解析区域
        parse_group = QGroupBox("参数解析")
        parse_group.setFont(self.font)
        parse_layout = QHBoxLayout()
        parse_group.setLayout(parse_layout)
        
        self.parse_text = QLineEdit()
        self.parse_text.setFont(self.font)
        self.parse_text.setPlaceholderText("在此粘贴参数表格...")
        self.parse_text.setMinimumHeight(32)  # 设置最小高度
        parse_layout.addWidget(self.parse_text, stretch=1)
        
        parse_btn = QPushButton("一键解析")
        parse_btn.setFont(self.font)
        parse_btn.clicked.connect(self.parse_parameters)
        parse_layout.addWidget(parse_btn)
        
        left_layout.addWidget(parse_group)
        
        # 图表区域
        self.figure = Figure(figsize=(6.8, 5.3))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setFixedSize(680, 530)
        self.ax = self.figure.add_subplot(111)
        left_layout.addWidget(self.canvas, stretch=1)
        
        # 右侧区域 - 参数设置
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(280)
        
        # 控件区域
        self.control_group = QGroupBox("参数设置")
        self.control_group.setFont(self.font)
        self.control_layout = QVBoxLayout()  # 改为垂直布局
        self.control_group.setLayout(self.control_layout)
        
        # 初始化参数控件
        self.create_parameter_controls()
        
        scroll.setWidget(self.control_group)
        right_layout.addWidget(scroll)
        
        # 添加到主布局
        main_layout.addWidget(left_widget, stretch=1)
        main_layout.addWidget(right_widget)
    
    def update_and_copy(self):
        """更新图表并复制到剪贴板"""
        self.update_plot()
        self.copy_to_clipboard()
    
    def parse_parameters(self):
        """从粘贴的表格文本中解析参数并更新界面"""
        text = self.parse_text.text().strip()
        if not text:
            return
        
        try:
            # 初始化参数字典
            params = {}
            structure_type = None  # 用于存储识别出的结构类型
            
            # 处理表格格式的文本
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            
            # 示例文本格式处理
            if len(lines) >= 2 and '\t' in lines[1]:
                # 假设第一行是表头，第二行是数据
                headers = lines[0].split('\t')
                values = lines[1].split('\t')
                
                # 创建键值对映射
                for header, value in zip(headers, values):
                    header = header.strip().lower()
                    value = value.strip()
                    
                    if not value or value == '-':
                        continue
                    
                    # 根据表头识别参数
                    if '结构' in header:
                        structure_type = value
                    elif '标的' in header:
                        params['asset'] = value
                    elif '期限' in header:
                        params['month'] = value.replace('天', 'D').replace('月', 'M')
                    elif '行权价' in header:
                        params['strike'] = float(value.replace('%', ''))
                    elif '障碍价' in header or '敲出价' in header:
                        params['knock_out'] = float(value.replace('%', ''))
                    elif '敲入价' in header:
                        params['knock_in'] = float(value.replace('%', ''))
                    elif '保底年化收益' in header and not '期权' in header:
                        params['min_ret'] = float(value.replace('%', ''))
                    elif '敲出年化收益' in header and not '期权' in header:
                        params['knock_ret'] = float(value.replace('%', ''))
                    elif '未敲入未敲出收益' in header:
                        params['ret2'] = float(value.replace('%', ''))
                    elif '敲入未敲出收益' in header:
                        params['ret1'] = float(value.replace('%', ''))
                    elif '敲出收益' in header and not '敲入' in header:
                        params['ret3'] = float(value.replace('%', ''))
                    elif '参与率' in header:
                        params['participation_rate'] = float(value.replace('%', ''))
                    elif '最高收益' in header:
                        params['max_ret'] = float(value.replace('%', ''))
                    elif '管理费' in header or '期权费' in header:
                        params['cost'] = float(value.replace('%', '').split('/')[0])
            
            # 根据结构类型自动切换期权类型
            if structure_type:
                # 定义结构类型到选项类型的映射
                structure_mapping = {
                    '三元': '三元小雪球',
                    '看涨敲出': '看涨敲出',
                    '看涨香草': '看涨香草',
                    '单鲨': lambda: '看涨单鲨/价差' if '看涨' in structure_type else '看跌单鲨/价差',
                    '价差': lambda: '看涨单鲨/价差' if '看涨' in structure_type else '看跌单鲨/价差'
                }
                
                # 查找匹配的结构类型
                matched_type = None
                for key in structure_mapping:
                    if key in structure_type:
                        if callable(structure_mapping[key]):
                            matched_type = structure_mapping[key]()
                        else:
                            matched_type = structure_mapping[key]
                        break
                
                if matched_type and matched_type in self.option_types:
                    self.type_combo.setCurrentText(matched_type)
                    self.current_option = matched_type
                    # 更新控件
                    self.create_parameter_controls()
            
            # 更新当前选项的参数
            if params:
                current_params = self.option_types[self.current_option]['params']
                for key, value in params.items():
                    if key in current_params:
                        current_params[key] = value
                        # 更新对应的控件
                        edit = getattr(self, f"{key}_edit", None)
                        if edit is not None:
                            if isinstance(value, (float, int)):
                                edit.setText(f"{value}")
                            else:
                                edit.setText(value)
                
                # 更新图表
                self.update_plot()
                self.copy_to_clipboard()
                
        except Exception as e:
            print(f"解析参数时出错: {e}")

    def create_parameter_controls(self):
        # 1. 清除所有控件
        while self.control_layout.count():
            item = self.control_layout.takeAt(0)  # 取出第一个 item
            if item.widget():
                item.widget().deleteLater()  # 删除 widget
            elif item.layout():
                # 递归删除子布局中的控件
                sub_layout = item.layout()
                while sub_layout.count():
                    sub_item = sub_layout.takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()
                sub_layout.deleteLater()
        
        # 根据当前期权类型创建控件
        params = self.option_types[self.current_option]['params']
        
        # 创建参数输入控件
        if 'strike' in params:
            self.strike_edit = self.create_parameter_input(self.control_layout, "行权价(%)", params['strike'])
        if 'knock_in' in params:
            self.knock_in_edit = self.create_parameter_input(self.control_layout, "敲入价(%)", params['knock_in'])
        if 'knock_out' in params:
            self.knock_out_edit = self.create_parameter_input(self.control_layout, "敲出价(%)", params['knock_out'])
        if 'participation_rate' in params:
            self.participation_rate_edit = self.create_parameter_input(self.control_layout, "参与率(%)", params['participation_rate'])
        if 'min_ret' in params:
            self.min_ret_edit = self.create_parameter_input(self.control_layout, "最低收益(%)", params['min_ret'])
        if 'max_ret' in params:
            self.max_ret_edit = self.create_parameter_input(self.control_layout, "最高收益(%)", params['max_ret'])
        if 'knock_ret' in params:
            self.knock_ret_edit = self.create_parameter_input(self.control_layout, "敲出收益(%)", params['knock_ret'])
        if 'ret1' in params:
            self.ret1_edit = self.create_parameter_input(self.control_layout, "保底收益(%)", params['ret1'])
        if 'ret2' in params:
            self.ret2_edit = self.create_parameter_input(self.control_layout, "中间收益(%)", params['ret2'])
        if 'ret3' in params:
            self.ret3_edit = self.create_parameter_input(self.control_layout, "敲出收益(%)", params['ret3'])
        
        self.month_edit = self.create_parameter_input(self.control_layout, "期限", params['month'], is_str=True)
        self.asset_edit = self.create_parameter_input(self.control_layout, "标的资产", params['asset'], is_str=True)
        self.cost_edit = self.create_parameter_input(self.control_layout, "费率(%)", params['cost'])
        
        if 'type' in params:
            self.type_edit = QComboBox()
            self.type_edit.addItems(['单鲨', '价差'])
            self.type_edit.setCurrentText(params['type'])
            form_layout = QFormLayout()
            form_layout.addRow(QLabel("单鲨/价差"), self.type_edit)
            self.control_layout.addLayout(form_layout)

        # 在最后添加一个拉伸因子，使所有控件靠上排列
        self.control_layout.addStretch()

        
        # 在最后添加"更新并复制"按钮
        self.update_copy_btn = QPushButton("更新并复制")
        self.update_copy_btn.setFont(self.font)
        self.update_copy_btn.clicked.connect(self.update_and_copy)
        button_style = """
            QPushButton {
                min-height: 30px;
                padding: 5px 10px;
            }
        """
        self.update_copy_btn.setStyleSheet(button_style)
        self.control_layout.addWidget(self.update_copy_btn)

        self.copy_hint = QLabel("结构图已复制到剪贴板！")
        self.copy_hint.setAlignment(Qt.AlignCenter)
        self.copy_hint.setVisible(False)  # 初始隐藏
        # 在布局中添加（但不显示）
        self.control_layout.insertWidget(self.control_layout.count()-1, self.copy_hint)

    def create_parameter_input(self, layout, label, default_value, is_str=False):
        form_layout = QFormLayout()
        label_widget = QLabel(label)
        edit = QLineEdit(str(default_value))
        if not is_str:
            validator = QDoubleValidator()
            validator.setNotation(QDoubleValidator.StandardNotation)
            edit.setValidator(validator)
        form_layout.addRow(label_widget, edit)
        layout.addLayout(form_layout)
        return edit
    
    def change_option_type(self, option_type):
        self.current_option = option_type
        # 更新控件
        self.create_parameter_controls()
        # 更新图表
        self.update_plot()
    
    def update_params(self):
        try:
            params = self.option_types[self.current_option]['params']
            for key in params.keys():
                # 获取对应的编辑控件
                edit = getattr(self, f"{key}_edit", None)
                if edit is not None:
                    if key in ['strike', 'knock_out', 'knock_in', 'participation_rate', 'min_ret', 'max_ret', 'knock_ret', 'ret1', 'ret2', 'ret3', 'cost']:
                        # 确保参与率等数值参数正确转换为浮点数
                        text = edit.text().replace('%', '')  # 移除可能存在的百分号
                        params[key] = float(text)
                    elif key in ['type']:
                        params['type'] = self.type_edit.currentText()
                    else:
                        # 处理字符串参数
                        params[key] = edit.text()
            
            return True
        except ValueError as e:
            print(f"参数更新错误: {e}")
            return False
    
    def update_plot(self):
        if not self.update_params():
            return
        
        # 清除当前图形
        self.ax.clear()
        
        # 调用对应的绘图函数
        plot_func = self.option_types[self.current_option]['plot_func']
        plot_func()
        
        # 重绘图形
        self.canvas.draw()
    
    def plot_sharkfin_call(self):
        # 获取当前参数
        params = self.option_types[self.current_option]['params']
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
        
        # 设置图形样式
        self.ax.set_ylim(-1, max_ret + 2)
        
        # 绘制收益曲线
        self.ax.plot([strike * 0.9, strike, knock_out], [min_ret, min_ret, max_ret],
                     marker='o', linestyle='-', color='#FF6B6B',
                     linewidth=2, markersize=5)
        
        self.ax.plot([knock_out, knock_out * 1.05], [knock_ret, knock_ret],
                     marker='o', linestyle='-', color='#FF6B6B',
                     linewidth=2, markersize=5)
        
        # 添加核心数据标签
        for x, y in zip([strike * 0.9, strike, knock_out], [min_ret, min_ret, max_ret]):
            self.ax.text(x, y + 0.1, f'{y:.2f}%',
                         ha='center', va='bottom', color='black', fontsize=12)
        
        # 添加特殊条款标注
        self.ax.text((strike + knock_out) / 2 - 0.5, max_ret / 2 + 0.2, f'参与率{participation_rate:,.1f}%',
                     ha='left', va='center', color='black', fontsize=12)
        if type0 == '单鲨':
            self.ax.text(knock_out * 1.01, knock_ret + 0.3, f'敲出{knock_ret:,.2f}%',
                         ha='left', va='center', color='black', fontsize=12)
        
        # 设置坐标轴
        self.ax.set_xlabel('标的期末价格/期初价格', ha='right', fontsize=10, labelpad=15)
        self.ax.set_xticks([strike, knock_out])
        self.ax.set_xticklabels([f'{strike:g}%', f'{knock_out:g}%'], fontsize=11)
        self.ax.set_yticks([min_ret, max_ret])
        self.ax.set_yticklabels([f'{min_ret}%', f'{max_ret}%'], fontsize=11)
        
        # 添加图表标题
        if type0 == '单鲨':
            self.ax.set_title(f'{month}美式看涨单鲨（每日观察）-{asset}\n业绩报酬计提基准（年化)-费率{cost}%',
                              fontsize=14, pad=20, color='#2C3E50')
        else:
            self.ax.set_title(f'{month}欧式看涨价差（期末观察一次）-{asset}\n业绩报酬计提基准（年化)-费率{cost}%',
                              fontsize=14, pad=20, color='#2C3E50')
            
        
        # 网格线优化
        self.ax.grid(linestyle=':', alpha=0.5, axis='both')
        self.ax.axhline(0, color='black', linewidth=0.8)
        self.ax.axvline(100, color='black', linewidth=0.8)
        
        # 图例说明
        self.ax.legend(['收益结构曲线'], loc='upper left', fontsize=10, frameon=False)
        
        # 调整布局确保图形大小固定
        self.figure.tight_layout()

    def plot_sharkfin_put(self):
        # 获取当前参数
        params = self.option_types[self.current_option]['params']
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

        self.ax.set_ylim(-1, max_ret + 2)

        # 绘制收益曲线
        self.ax.plot([knock_out*0.9,knock_out], [knock_ret,knock_ret], #保底 行权 敲出
                 marker='o', linestyle='-', color='#FF6B6B',
                 linewidth=2, markersize=5)

        self.ax.plot([knock_out,strike], [max_ret,min_ret], #保底 行权 敲出
                 marker='o', linestyle='-', color='#FF6B6B',
                 linewidth=2, markersize=5)

        self.ax.plot([strike,strike*1.1], [min_ret,min_ret],
                 marker='o', linestyle='-', color='#FF6B6B',
                 linewidth=2, markersize=5)

        # 添加核心数据标签
        for x, y in zip([knock_out,strike,strike*1.1],[max_ret,min_ret,min_ret]):
            self.ax.text(x, y +0.1, f'{y:.2f}%',
                    ha='center', va='bottom', color='black', fontsize=12)

        # 添加特殊条款标注
        self.ax.text((strike+knock_out)/2, max_ret*2/3, f'参与率{participation_rate:.2f}%',
                 ha='left', va='center', color='black', fontsize=12)

        if type0=='单鲨':
            self.ax.text(knock_out*0.95, knock_ret*1.1, f'敲出{knock_ret:,.2f}%',
                     ha='left', va='center', color='black', fontsize=12)

        # 设置坐标轴
        self.ax.set_xlabel('标的期末价格/期初价格', ha='right', fontsize=10, labelpad=10)
        self.ax.set_xticks([strike, knock_out], [str(strike)+'%', str(knock_out)+'%'], fontsize=11)
        self.ax.set_yticks([min_ret, max_ret], [str(min_ret)+'%', str(max_ret)+'%'], fontsize=11)

        # 添加图表标题
        if type0=='单鲨':opt_title ='美式看跌单鲨（每日观察）'
        else:opt_title ='欧式看跌价差（期末观察一次）'

        self.ax.set_title(f'{month}{opt_title}-{asset}\n业绩报酬计提基准（年化)-费率{cost}%',
                  fontsize=14, pad=20, color='#2C3E50')


        # 网格线优化
        self.ax.grid(linestyle=':', alpha=0.5, axis='both')
        self.ax.axhline(0, color='black', linewidth=0.8)
        self.ax.axvline(100, color='black', linewidth=0.8)

        # 图例说明
        self.ax.legend(['收益结构曲线'], loc='upper left', fontsize=10, frameon=False)
        
        # 调整布局确保图形大小固定
        self.figure.tight_layout()
    
    def plot_snowball(self):
        # 获取当前参数
        params = self.option_types[self.current_option]['params']
        knock_in = params['knock_in']
        knock_out = params['knock_out']
        ret1 = params['ret1']
        ret2 = params['ret2']
        ret3 = params['ret3']
        month = params['month']
        asset = params['asset']
        cost = params['cost']
        
        # 设置图形样式
        self.ax.set_ylim(-1, ret3 + 2)
        
        # 绘制收益曲线
        self.ax.plot([knock_in * 0.8, knock_in], [ret1, ret1],
                     marker='o', linestyle='-', color='#FF6B6B',
                     linewidth=2, markersize=5)
        
        self.ax.plot([knock_in, knock_out], [ret2, ret2],
                     marker='o', linestyle='-', color='#FF6B6B',
                     linewidth=2, markersize=5)

        self.ax.plot([knock_out, knock_out * 1.2], [ret3, ret3],
                     marker='o', linestyle='-', color='#FF6B6B',
                     linewidth=2, markersize=5)

        # 添加特殊条款标注
        self.ax.text(knock_in * 0.8, ret1 + 0.5, f'保底收益{ret1:,.2f}%',
                    ha='left', va='center', color='black', fontsize=12)
        
        self.ax.text(knock_in + 3, ret2 + 0.5, f'未敲入未敲出收益{ret2:,.2f}%',
                   ha='left', va='center', color='black', fontsize=12)

        self.ax.text(knock_out * 1.05, ret3 + 0.5, f'敲出收益{ret3:,.2f}%',
                   ha='left', va='center', color='black', fontsize=12)
        
        # 设置坐标轴
        self.ax.set_xlabel('敲出观察日价格/期初价格', ha='left', fontsize=10, labelpad=15)
        self.ax.set_xticks([knock_in, knock_out])
        self.ax.set_xticklabels([f'{knock_in}%', f'{knock_out}%'], fontsize=11)
        self.ax.set_yticks([ret1, ret2, ret3])
        self.ax.set_yticklabels([f'{ret1}%', f'{ret2}%', f'{ret3}%'], fontsize=11)

        # 添加图表标题
        self.ax.set_title(f'{month}三元小雪球（每月观察敲出）-{asset}\n业绩报酬计提基准（年化)-费率{cost}%',
                        fontsize=14, pad=20, color='#2C3E50')

        # 网格线优化
        self.ax.grid(linestyle=':', alpha=0.5, axis='both')
        self.ax.axhline(0, color='black', linewidth=0.8)

        # 图例说明
        self.ax.legend(['收益结构曲线'], loc='upper left', fontsize=10, frameon=False)
        
        # 调整布局确保图形大小固定
        self.figure.tight_layout()

    def plot_snowball2(self):
        # 获取当前参数
        params = self.option_types[self.current_option]['params']
        knock_in = params['knock_in']
        knock_out = params['knock_out']
        ret1 = params['ret1']
        ret3 = params['ret3']
        month = params['month']
        asset = params['asset']
        cost = params['cost']

        # 设置图形样式
        self.ax.set_ylim(-1, ret3 + 2)

        # 绘制收益曲线
        self.ax.plot([knock_in*0.9,knock_out], [ret1,ret1], #保底 行权 敲出
             marker='o', linestyle='-', color='#FF6B6B',
             linewidth=2, markersize=5)

        self.ax.plot([knock_out,knock_out*1.2], [ret3,ret3],
             marker='o', linestyle='-', color='#FF6B6B',
             linewidth=2, markersize=5)

        self.ax.text(knock_in*0.95 ,ret1+0.5, f'未敲出收益{ret1:,.2f}%',
        ha='left', va='center', color='black', fontsize=12)

        self.ax.text(knock_out*1.05,ret3+0.5, f'敲出收益{ret3:,.2f}%',
         ha='left', va='center', color='black', fontsize=12)
        # 设置坐标轴
        self.ax.set_xlabel('敲出观察日价格/期初价格', ha='left', fontsize=10, labelpad=15)
        self.ax.set_xticks([ knock_out], [ str(knock_out)+'%'], fontsize=12)
        self.ax.set_yticks([ret1,ret3], [str(ret1)+'%',str(ret3)+'%'], fontsize=11)

        # 添加图表标题
        self.ax.set_title(f'{month}看涨敲出（期末观察一次）-{asset}\n业绩报酬计提基准（年化)-费率{cost}%',
              fontsize=14, pad=20, color='#2C3E50')

        # 网格线优化
        self.ax.grid(linestyle=':', alpha=0.5, axis='both')
        self.ax.axhline(0, color='black', linewidth=0.8)

        # 图例说明
        self.ax.legend(['收益结构曲线'], loc='upper left', fontsize=10, frameon=False)

        # 调整布局确保图形大小固定
        self.figure.tight_layout()

    def plot_call(self):
        # 获取当前参数
        params = self.option_types[self.current_option]['params']
        strike = params['strike']
        participation_rate = params['participation_rate']
        min_ret = params['min_ret']
        month = params['month']
        asset = params['asset']
        cost = params['cost']

        rise1 = 1.1
        ret1 = min_ret+participation_rate*(rise1-1)

        rise2 = 1.15
        ret2 = min_ret+participation_rate*(rise2-1)

        self.ax.set_ylim(-1, ret2 + 2)

        # 绘制收益曲线
        self.ax.plot([strike*0.9,strike], [min_ret,min_ret], #保底 行权 敲出
                 marker='o', linestyle='-', color='#FF6B6B',
                 linewidth=2, markersize=5)

        self.ax.plot([strike,strike*rise1,strike*rise2], [min_ret,ret1,ret2], #保底 行权 敲出
             linestyle='-', color='#FF6B6B',
             linewidth=2, markersize=5)

        # 添加核心数据标签
        for x, y in zip([strike*0.9,strike],[min_ret,min_ret]):
            self.ax.text(x, y +0.1, f'{y:.2f}%',
                    ha='center', va='bottom', color='black', fontsize=12)

        # 添加特殊条款标注
        self.ax.text((strike+rise2 * 100)/2, ret2/2, f'参与率{participation_rate:.2f}%',
                 ha='left', va='center', color='black', fontsize=12)
        # 设置坐标轴
        self.ax.set_xlabel('标的期末价格/期初价格', ha='right', fontsize=10, labelpad=15)
        self.ax.set_xticks([strike], [str(strike)+'%'], fontsize=11)
        self.ax.set_yticks([min_ret], [str(min_ret)+'%'], fontsize=11)

        # 添加图表标题
        self.ax.set_title(f'{month}看涨香草-{asset}\n业绩报酬计提基准（年化)-费率{cost}%',
                  fontsize=14, pad=20, color='#2C3E50')


        # 网格线优化
        self.ax.grid(linestyle=':', alpha=0.5, axis='both')
        self.ax.axhline(0, color='black', linewidth=0.8)
        self.ax.axvline(100, color='black', linewidth=0.8)

        # 图例说明
        self.ax.legend(['收益结构曲线'], loc='upper left', fontsize=10, frameon=False)

        # 调整布局确保图形大小固定
        self.figure.tight_layout()

    def copy_to_clipboard(self):
        # 将图表保存为图像
        buf = io.BytesIO()
        self.figure.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        
        # 创建QPixmap并复制到剪贴板
        image = QImage()
        image.loadFromData(buf.getvalue())
        pixmap = QPixmap.fromImage(image)
        
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(pixmap)
        
        buf.close()

        self.copy_hint.setVisible(True)  # 显示提示
        QTimer.singleShot(800, lambda: self.copy_hint.setVisible(False))  # 1秒后隐藏


if __name__ == "__main__":
    # 设置matplotlib中文字体
    plt.rcParams['font.family'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['axes.edgecolor'] = 'grey'  # 坐标轴边框颜色设为灰色
    plt.rcParams['axes.linewidth'] = 1.0     # 坐标轴边框线宽设为 1.0
    
    app = QApplication(sys.argv)
    window = OptionApp()
    window.show()
    sys.exit(app.exec_())
