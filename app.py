import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

# ==========================================
# 1. 页面配置与空天教学情境导入
# ==========================================
st.set_page_config(page_title="数智力学交互学案", layout="wide")
st.title("🚀 空天构件复杂应力状态分析系统")
st.markdown("""
**长空创新班《材料力学A》专属数字伴学资源** > **教学情境**：假设您正在对某型飞行器机翼蒙皮进行受力分析。请在左侧调整测点提取的初始应力状态，并滑动角度滑块，观察应力莫尔圆的实时映射及主应力演化过程，寻找最危险截面。
---
""")

# ==========================================
# 2. 侧边栏：参数输入与交互控制
# ==========================================
with st.sidebar:
    st.header("⚙️ 工程参数输入区")
    st.caption("单位：MPa (兆帕)")
    
    # 设定默认值为典型的航空铝合金壁板受力状态
    val_sx = st.slider("x方向正应力 (σx)", min_value=-200.0, max_value=200.0, value=80.0, step=1.0)
    val_sy = st.slider("y方向正应力 (σy)", min_value=-200.0, max_value=200.0, value=-20.0, step=1.0)
    val_txy = st.slider("切应力 (τxy)", min_value=-100.0, max_value=100.0, value=40.0, step=1.0)
    
    st.divider()
    st.header("🔄 截面旋转探究")
    alpha_deg = st.slider("截面倾角 α (度)", min_value=0.0, max_value=180.0, value=0.0, step=1.0)
    alpha_rad = np.radians(alpha_deg)

# ==========================================
# 3. 后端引擎：基于 SymPy 的数理推导 (强推导)
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
# 4. 主体布局：数据面板与可视化 (弱验证破局)
# ==========================================
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📊 实时计算结果")
    st.metric(label=f"倾角 {alpha_deg}° 时的正应力 (σα)", value=f"{current_sigma:.2f} MPa")
    st.metric(label=f"倾角 {alpha_deg}° 时的切应力 (τα)", value=f"{current_tau:.2f} MPa")
    
    st.divider()
    st.subheader("⚠️ 结构安全边界 (极值)")
    st.info(f"**第一主应力 (σ1)**: {sigma_1:.2f} MPa")
    st.info(f"**第三主应力 (σ3)**: {sigma_2:.2f} MPa")
    st.error(f"**最大切应力 (τmax)**: {tau_max:.2f} MPa")

with col2:
    st.subheader("⭕ 数学空间：应力莫尔圆动态映射")
    
    # 使用 Matplotlib 绘制高质量交互图
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # 绘制莫尔圆
    circle = plt.Circle((center_c, 0), radius_r, color='blue', fill=False, linestyle='--', linewidth=1.5)
    ax.add_patch(circle)
    
    # 绘制坐标轴
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    
    # 绘制动态映射点和半径线
    ax.plot(current_sigma, current_tau, 'ro', markersize=8, label=f'Current State (α={alpha_deg}°)')
    ax.plot([center_c, current_sigma], [0, current_tau], 'r-', linewidth=1.5)
    
    # 绘制主应力点
    ax.plot(sigma_1, 0, 'go', markersize=6, label='Principal Stress (σ1)')
    ax.plot(sigma_2, 0, 'go', markersize=6, label='Principal Stress (σ3)')
    
    # 图表格式化
    ax.set_aspect('equal', 'box')
    ax.set_xlabel('Normal Stress, σ (MPa)')
    ax.set_ylabel('Shear Stress, τ (MPa)')
    ax.set_title("Mohr's Circle of Stress", fontsize=14)
    ax.legend(loc='upper right')
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # 自适应坐标轴范围
    max_val = max(abs(sigma_1), abs(sigma_2), radius_r) * 1.5
    ax.set_xlim(center_c - max_val, center_c + max_val)
    ax.set_ylim(-max_val, max_val)
    
    st.pyplot(fig)