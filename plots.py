import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def plot_execution_time(results):
    algo_names = [res['algorithm'] for res in results]
    exec_times = [res['time'] for res in results]

    fig = go.Figure(
        data=[go.Bar(
            x=algo_names,
            y=exec_times,
            marker_color='#293241',
            text=[f"{t:.2f} s" for t in exec_times],
            textposition='outside'
        )]
    )

    fig.update_layout(
        title="⏱️ Execution Time by Algorithm",
        yaxis_title="Time in seconds",
        yaxis=dict(tickformat=".2f"),
        height=500,
        title_x=0.3,
    )

    return fig

def plot_memory_usage(results):
    algo_names = [res['algorithm'] for res in results]
    memory_usages = [res['memory_MB'] for res in results]

    fig = go.Figure(
        data=[go.Bar(
            x=algo_names,
            y=memory_usages,
            marker_color='#647b99',
            text=[f"{m:.2f} MB" for m in memory_usages],
            textposition='outside'
        )]
    )

    fig.update_layout(
        title="💾 Memory Usage by Algorithm",
        yaxis_title="Memory (MB)",
        yaxis=dict(tickformat=".2f"),
        height=500,
        title_x=0.3,
    )

    return fig


def get_algorithm_progress_fig(algos_progress, selected_algorithms):
    """
    Creates and returns a Plotly figure for algorithm progress.

    Parameters:
        algos_progress (List[List[float]]): Progress data for each algorithm.
        selected_algorithms (List[str]): Names of the algorithms.

    Returns:
        fig (go.Figure): Plotly figure object.
    """
    x = list(range(len(algos_progress[0])))
    colors = px.colors.sequential.Aggrnyl  # Change palette if you want

    fig = go.Figure()

    for i, col in enumerate(algos_progress):
        fig.add_trace(go.Scatter(
            x=x,
            y=col,
            mode='lines+markers',
            name=selected_algorithms[i],
            line=dict(color=colors[i % len(colors)], width=5),
            marker=dict(size=8)
        ))

    fig.update_layout(
        title=dict(
            text='📈 Progress of Selected Algorithms',
            x=0.3,
            font=dict(size=18, family="Verdana", color="black")
        ),
        xaxis=dict(
            title='Step',
            showgrid=False
        ),
        yaxis=dict(
            title='Progress',
            showgrid=True,
            gridcolor="#98C1D9",
            gridwidth=3,
            zeroline=False,
        ),
        legend=dict(
            x=1,
            y=1,
            xanchor='right',
            yanchor='top',
            bgcolor='rgba(255,255,255,0.7)',
            bordercolor='lightgrey',
            borderwidth=1
        ),
        plot_bgcolor="#e0fbfc",
        font=dict(family="Verdana", size=12, color="black"),
        height=450,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    return fig

def plot_cpu_usage(results):
    algorithms = [res["algorithm"] for res in results]
    cpu_usages = [res.get("cpu_percent", 0) for res in results]

    fig = go.Figure(data=[
        go.Bar(
            x=algorithms,
            y=cpu_usages,
            marker_color='#98C1D9',
            text=[f"{val:.2f}%" for val in cpu_usages],
            textposition="auto"
        )
    ])

    fig.update_layout(
        title="🔧 CPU Usage per Algorithm",
        yaxis_title="Average CPU Usage (%)",
        yaxis_range=[0, 100],
        template="plotly_white",
        height=500,
        title_x=0.3,
    )

    return fig