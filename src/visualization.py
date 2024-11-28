"""Utility to visualize photo plans.
"""

import typing as T

import plotly.graph_objects as go

from src.data_model import Waypoint
def plot_photo_plan(computed_plan: T.List[Waypoint], scan_dimension_x: float, scan_dimension_y: float) -> go.Figure:
    """
    Plot the drone flight plan with waypoints and surface coverage using Plotly.

    Args:
        computed_plan (list[Waypoint]): List of waypoints generated for the flight plan.
        scan_dimension_x (float): Total width of the scan area.
        scan_dimension_y (float): Total height of the scan area.

    Returns:
        fig: A Plotly figure object.
    """
    fig = go.Figure()

    # Add scan area rectangle
    fig.add_shape(
        type="rect",
        x0=0,
        y0=0,
        x1=scan_dimension_x,
        y1=scan_dimension_y,
        line=dict(color="green", width=2),
        opacity=0.3,
        name="Scan Area"
    )

    # Plot waypoints and connecting lines
    for i, waypoint in enumerate(computed_plan):
        if i > 0:
            # Add line between waypoints with hover info
            prev_wp = computed_plan[i - 1]
            fig.add_trace(go.Scatter(
                x=[prev_wp.x, waypoint.x],
                y=[prev_wp.y, waypoint.y],
                mode='lines',
                line=dict(color='orange', width=2),
                hoverinfo="text",
                text=[f"From: ({prev_wp.x:.2f}, {prev_wp.y:.2f})<br>To: ({waypoint.x:.2f}, {waypoint.y:.2f})"],
                showlegend=False
            ))

        # Add waypoint markers with hover text
        fig.add_trace(go.Scatter(
            x=[waypoint.x],
            y=[waypoint.y],
            mode='markers+text',
            marker=dict(size=12, color='purple', symbol='circle'),
            text=[f"{i+1}"],
            textfont=dict(size=10, color='black'),
            textposition="top center",
            hoverinfo="text",
            hovertext=(
                f"Waypoint {i+1}<br>"
                f"Coordinates: ({waypoint.x:.2f}, {waypoint.y:.2f})<br>"
                f"Altitude: {waypoint.z} m<br>"
                f"Speed: {waypoint.speed_m_per_sec:.2f} m/s"
            ),
            name=f"Waypoint {i+1}"
        ))

        # Add annotations for waypoint coordinates
        fig.add_annotation(
            x=waypoint.x,
            y=waypoint.y,
            text=f"({waypoint.x:.2f}, {waypoint.y:.2f})",
            showarrow=True,
            arrowhead=2,
            ax=20,
            ay=-20,
            font=dict(size=10, color="black"),
            bgcolor="white",
            bordercolor="gray"
        )

    # Get min and max values for x and y coordinates
    x_values = [wp.x for wp in computed_plan] + [scan_dimension_x]
    y_values = [wp.y for wp in computed_plan] + [scan_dimension_y]

    x_min, x_max = min(x_values) - 10, max(x_values) + 10
    y_min, y_max = min(y_values) - 10, max(y_values) + 10

    speed = computed_plan[0].speed_m_per_sec
    altitude = computed_plan[0].z
    number_of_images = len(computed_plan)

    # Update layout with more interactivity and details
    fig.update_layout(
        title=f"Photo Plan | Images: {number_of_images}, Speed: {speed:.2f} m/s, Altitude: {altitude} m",
        xaxis_title=f"X Coordinate (m) [Min: {x_min:.2f}, Max: {x_max:.2f}]",
        yaxis_title=f"Y Coordinate (m) [Min: {y_min:.2f}, Max: {y_max:.2f}]",
        xaxis=dict(range=[x_min, x_max], showgrid=True, gridcolor='lightgray'),
        yaxis=dict(range=[y_min, y_max], showgrid=True, gridcolor='lightgray'),
        height=800,
        width=1000,
        plot_bgcolor="#f9f9f9",
        showlegend=True,
        legend=dict(
            title="Legend",
            itemsizing="constant"
        )
    )

    return fig
