import streamlit as st
import numpy as np
import sympy as sp
import plotly.graph_objects as go

# ==========================================
# 1. 页面配置与空天教学情境导入
# ==========================================
# 手机端竖屏友好布局
st.set_page_config(page_title="数智力学交互学案", layout="centered") 

st.title("🚀 空天构件复杂应力状态分析系统")
st.markdown("""
**长空创新班《材料力学A》专属数字伴学资源** > **教学情境**：假设您正在对某型飞行器机翼蒙皮进行受力分析。请在下方调整测点提取的初始应力状态，并滑动角度滑块，观察应力莫尔圆的实时映射及主应力演化过程，寻找最危险截面。
---
""")

# ==========================================
# 2. 交互控制区 (全平台直观显示，完美适配手机扫码)
# ==========================================
st.header("⚙️ 动态参数调节区")
st.caption("单位：MPa (兆帕)")

# 摒弃隐藏的侧边栏，使用主页面的列布局
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
sx, sy, txy, alpha = sp.symbols('sigma_x sigma_y tau_xy alpha')
eq_sigma = (sx + sy)/2 + (sx - sy)/2 * sp.cos(2*alpha) - txy * sp.sin(2*alpha)
eq_tau = (sx - sy)/2 * sp.sin(2*alpha) + txy * sp.cos(2*alpha)

calc_sigma = sp.lambdify((sx, sy, txy, alpha), eq_sigma, 'numpy')
calc_tau = sp.lambdify((sx, sy, txy, alpha), eq_tau, 'numpy')

current_sigma = calc_sigma(val_sx, val_sy, val_txy, alpha_rad)
current_tau = calc_tau(val_sx, val_sy, val_txy, alpha_rad)

center_c = (val_sx + val_sy) / 2
radius_r = np.sqrt(((val_sx - val_sy)/2)**2 + val_txy**2)
sigma_1 = center_c + radius_r
sigma_2 = center_c - radius_r
tau_max = radius_r

# ==========================================
# 4. 主体布局：可视化与核心数据面板 (弱验证破局)
# ==========================================
st.subheader("⭕ 数学空间：应力莫尔圆动态映射")

# 创建现代化的交互式图表 (Plotly)
fig = go.Figure()

# 绘制莫尔圆骨架
fig.add_shape(type="circle",
    xref="x", yref="y",
    x0=center_c - radius_r, y0=-radius_r,
    x1=center_c + radius_r, y1=radius_r,
    line_color="#1f77b4", line_width=2,
)

# 绘制当前截面状态点和红色半径线
fig.add_trace(go.Scatter(
    x=[center_c, current_sigma], 
    y=[0, current_tau], 
    mode='lines+markers',
    line=dict(color='red', width=2),
    marker=dict(color='red', size=8),
    name=f'当前截面 (α={alpha_deg}°)',
    hovertemplate='正应力: %{x:.1f} MPa<br>切应力: %{y:.1f} MPa<extra></extra>'
))

# 绘制主应力点 (绿色)
fig.add_trace(go.Scatter(
    x=[sigma_1, sigma_2], 
    y=[0, 0], 
    mode='markers',
    marker=dict(color='green', size=8),
    name='主应力 (σ1, σ3)',
    hovertemplate='主应力: %{x:.1f} MPa<extra></extra>'
))

# 设置自适应坐标轴与中文图表布局
max_val = max(abs(sigma_1), abs(sigma_2), radius_r) * 1.5
if max_val == 0:
    max_val = 100

fig.update_layout(
    xaxis_title="正应力, σ (MPa)",
    yaxis_title="切应力, τ (MPa)",
    xaxis=dict(range=[center_c - max_val, center_c + max_val], zeroline=True, zerolinecolor='black', showgrid=True),
    # scaleanchor="x" 强制 X 轴和 Y 轴比例为 1:1，保证圆不会变成椭圆
    yaxis=dict(range=[-max_val, max_val], zeroline=True, zerolinecolor='black', showgrid=True, scaleanchor="x", scaleratio=1),
    legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99, bgcolor="rgba(255, 255, 255, 0.8)"),
    margin=dict(l=20, r=20, t=30, b=20),
    height=450,
    hovermode="closest"
)

st.plotly_chart(fig, use_container_width=True)
st.divider()

# 核心数据展示区
col_data1, col_data2 = st.columns(2)

with col_data1:
    st.subheader("📊 实时计算结果")
    st.info(f"**当前倾角**: {alpha_deg}°\n\n**正应力 (σα)**: {current_sigma:.2f} MPa\n\n**切应力 (τα)**: {current_tau:.2f} MPa")

with col_data2:
    st.subheader("⚠️ 结构安全边界")
    st.error(f"**第一主应力 (σ1)**: {sigma_1:.2f} MPa\n\n**第三主应力 (σ3)**: {sigma_2:.2f} MPa\n\n**最大切应力 (τmax)**: {tau_max:.2f} MPa")
