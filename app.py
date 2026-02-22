import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 替换为系统中存在的中文字体，如微软雅黑、宋体等
plt.rcParams['axes.unicode_minus'] = False    # 解决负号显示为方块的问题

# ==========================================
# 1. 页面配置与空天教学情境导入
# ==========================================
# 将布局改为 centered，在手机竖屏下显示更集中、更美观
st.set_page_config(page_title="数智力学交互学案", layout="centered") 

st.title("🚀 空天构件复杂应力状态分析系统")
st.markdown("""
**长空创新班《材料力学A》专属数字伴学资源** > **教学情境**：假设您正在对某型飞行器机翼蒙皮进行受力分析。请在下方调整测点提取的初始应力状态，并滑动角度滑块，观察应力莫尔圆的实时映射及主应力演化过程，寻找最危险截面。
---
""")

# ==========================================
# 2. 交互控制区 (优化为全平台直观显示，完美适配手机扫码)
# ==========================================
st.header("⚙️ 动态参数调节区")
st.caption("单位：MPa (兆帕)")

# 摒弃隐藏的侧边栏，使用主页面的列布局，让滑动条在手机上直接可见
col_input1, col_input2 = st.columns(2)

with col_input1:
    val_sx = st.slider("x方向正应力 (σx)", min_value=-200.0, max_value=200.0, value=80.0, step=1.0)
    val_txy = st.slider("切应力 (τxy)", min_value=-100.0, max_value=100.0, value=40.0, step=1.0)

with col_input2:
    val_sy = st.slider("y方向正应力 (σy)", min_value=-200.0, max_value=200.0, value=-20.0, step=1.0)
    alpha_deg = st.slider("截面倾角 α (度) 🔄", min_value=0.0, max_value=180.0, value=0.0, step=1.0)

alpha_rad = np.radians(alpha_deg)
st.divider()

# ==========================================
# 3. 后端引擎：基于 SymPy 的数理推导 (强推导体现)
# ==========================================
# 预先进行符号推导，保证底层逻辑的严密性
sx, sy, txy, alpha = sp.symbols('sigma_x sigma_y tau_xy alpha')
eq_sigma = (sx + sy)/2 + (sx - sy)/2 * sp.cos(2*alpha) - txy * sp.sin(2*alpha)
eq_tau = (sx - sy)/2 * sp.sin(2*alpha) + txy * sp.cos(2*alpha)

calc_sigma = sp.lambdify((sx, sy, txy, alpha), eq_sigma, 'numpy')
calc_tau = sp.lambdify((sx, sy, txy, alpha), eq_tau, 'numpy')

# 计算当前截面应力
current_sigma = calc_sigma(val_sx, val_sy, val_txy, alpha_rad)
current_tau = calc_tau(val_sx, val_sy, val_txy, alpha_rad)

# 计算主应力与莫尔圆参数
center_c = (val_sx + val_sy) / 2
radius_r = np.sqrt(((val_sx - val_sy)/2)**2 + val_txy**2)
sigma_1 = center_c + radius_r
sigma_2 = center_c - radius_r
tau_max = radius_r

# ==========================================
# 4. 主体布局：可视化与核心数据面板 (弱验证破局)
# ==========================================
st.subheader("⭕ 数学空间：应力莫尔圆动态映射")

# 为了手机端更好的视觉连贯性，将图表放在数据上方
fig, ax = plt.subplots(figsize=(8, 6))

# 绘制莫尔圆
circle = plt.Circle((center_c, 0), radius_r, color='#1f77b4', fill=False, linestyle='-', linewidth=2)
ax.add_patch(circle)

# 绘制坐标轴
ax.axhline(0, color='black', linewidth=1.2)
ax.axvline(0, color='black', linewidth=1.2)

# 绘制动态映射点和半径线
ax.plot(current_sigma, current_tau, 'ro', markersize=8, label=f'当前截面状态 (α={alpha_deg}°)')
ax.plot([center_c, current_sigma], [0, current_tau], 'r-', linewidth=2)

# 绘制主应力点
ax.plot(sigma_1, 0, 'go', markersize=8, label='第一主应力 (σ1)')
ax.plot(sigma_2, 0, 'go', markersize=8, label='第三主应力 (σ3)')

# 图表格式化
ax.set_aspect('equal', 'box')
ax.set_xlabel('正应力, σ (MPa)', fontsize=12)
ax.set_ylabel('切应力, τ (MPa)', fontsize=12)
ax.set_title("材料力学应力莫尔圆 (Mohr's Circle)", fontsize=14, fontweight='bold')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, linestyle=':', alpha=0.7)

# 自适应坐标轴范围，稍微留白避免图形贴边
max_val = max(abs(sigma_1), abs(sigma_2), radius_r) * 1.5
if max_val == 0:
    max_val = 100
ax.set_xlim(center_c - max_val, center_c + max_val)
ax.set_ylim(-max_val, max_val)

st.pyplot(fig)
st.divider()

# 核心数据展示区
col_data1, col_data2 = st.columns(2)

with col_data1:
    st.subheader("📊 实时计算结果")
    st.info(f"**当前倾角**: {alpha_deg}°\n\n**正应力 (σα)**: {current_sigma:.2f} MPa\n\n**切应力 (τα)**: {current_tau:.2f} MPa")

with col_data2:
    st.subheader("⚠️ 结构安全边界")
    st.error(f"**第一主应力 (σ1)**: {sigma_1:.2f} MPa\n\n**第三主应力 (σ3)**: {sigma_2:.2f} MPa\n\n**最大切应力 (τmax)**: {tau_max:.2f} MPa")

