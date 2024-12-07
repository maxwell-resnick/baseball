from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Ellipse

pitch_color_mapping = {
    'FF': 'red', 'SL': 'orange', 'SI': 'pink', 'CH': 'purple', 'FC': 'blue',
    'CU': 'lightgreen', 'ST': 'brown', 'FS': 'black', 'KC': 'darkgreen',
    'SV': 'yellow', 'FO': 'yellow', 'KN': 'yellow', 'SC': 'yellow'
}

def create_tunneling_table(data):
    data['Usage%'] = data.groupby('pitch_type')['pitch_type'].transform('count') / len(data) * 100

    grouped_metrics = data.groupby('pitch_type')[['Usage%', 'tunnel_boost', 'x_tunnel', 'y_tunnel',
                                                'z_tunnel', 'shape_tunnel']].mean().reset_index()

    grouped_metrics = grouped_metrics.sort_values(by='Usage%', ascending=False)

    grouped_metrics = grouped_metrics.rename(columns={
        'pitch_type': 'Pitch Type',
        'tunnel_boost': 'Tunnel Boost',
        'x_tunnel': 'X Tunnel',
        'y_tunnel': 'Y Tunnel',
        'z_tunnel': 'Z Tunnel',
        'shape_tunnel': 'Shape Tunnel'
    })

    grouped_metrics = grouped_metrics.round({'Tunnel Boost': 2, 'X Tunnel': 2, 'Y Tunnel': 2, 
                                            'Z Tunnel': 2, 'Shape Tunnel': 2, 'Usage%': 1})

    cmap = LinearSegmentedColormap.from_list("custom_gradient", ["blue", "white", "red"])

    def apply_gradient(s, vmin, vmax):
        norm = Normalize(vmin=vmin, vmax=vmax)  
        colors = [cmap(norm(val)) for val in s] 
        return [f"background-color: rgba({int(c[0]*255)}, {int(c[1]*255)}, {int(c[2]*255)}, 1)" for c in colors]

    styled_metrics = grouped_metrics.style.apply(
        lambda s: apply_gradient(s, vmin=-1.5, vmax=1.5), subset=['Tunnel Boost', 'Y Tunnel']
    ).apply(
        lambda s: apply_gradient(s, vmin=-0.5, vmax=0.5), subset=['X Tunnel', 'Z Tunnel', 'Shape Tunnel']
    ).format(
        {"Tunnel Boost": "{:.2f}", "X Tunnel": "{:.2f}", "Y Tunnel": "{:.2f}", 
        "Z Tunnel": "{:.2f}", "Shape Tunnel": "{:.2f}", "Usage%": "{:.1f}"}
    ).set_table_styles([
        {"selector": "thead th", "props": [("font-size", "20px"), ("text-align", "center"), ("color", "black")]},
        {"selector": "tbody td", "props": [("font-size", "18px"), ("text-align", "center"), ("color", "black")]}
    ]).hide(axis="index")

    html_output = styled_metrics.to_html()
    return html_output


def plot_pitcher_metrics(player_name, player_df, fig, axs, x_metric, y_metric, x_label, y_label):
    for stand, ax in zip(['L', 'R'], axs):
        stand_df = player_df[player_df['stand'] == stand]

        stand_df = stand_df.dropna(subset=[x_metric, y_metric])

        pitch_type_counts = stand_df['pitch_type'].value_counts(normalize=True)

        valid_pitch_types = pitch_type_counts[pitch_type_counts >= 0.02].index

        filtered_df = stand_df[stand_df['pitch_type'].isin(valid_pitch_types)]

        grouped = filtered_df.groupby('pitch_type').agg(
            mean_x=(x_metric, 'mean'),
            mean_y=(y_metric, 'mean'),
            std_x=(x_metric, 'std'),
            std_y=(y_metric, 'std')
        ).reset_index()

        for _, row in grouped.iterrows():
            pitch_color = pitch_color_mapping.get(row['pitch_type'])
            if pitch_color:  
                ax.scatter(row['mean_x'], row['mean_y'], 
                        edgecolor=pitch_color, facecolor='white', lw=2, s=100, label=row['pitch_type'])
                
                ellipse = Ellipse((row['mean_x'], row['mean_y']),
                                width=2 * row['std_x'], height=2 * row['std_y'],
                                edgecolor=pitch_color, facecolor='none', lw=2, linestyle='--')
                ax.add_patch(ellipse)

        handles, labels = ax.get_legend_handles_labels()
        sorted_handles_labels = sorted(
            zip(handles, labels), key=lambda x: pitch_type_counts.get(x[1], 0), reverse=True
        )
        sorted_handles, sorted_labels = zip(*sorted_handles_labels) if sorted_handles_labels else ([], [])
        ax.legend(sorted_handles, sorted_labels, title='Pitch Type', loc='upper right', fontsize=14, title_fontsize=16)

        ax.set_title(f"vs. {stand}HH", fontsize=20)
        ax.set_xlabel(x_label, fontsize=16)
        ax.set_ylabel(y_label if stand == 'L' else '', fontsize=16)

        ax.tick_params(axis='both', which='major', labelsize=16)
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        ax.set_xticks(range(int(x_min), int(x_max) + 1))
        ax.set_yticks(range(int(y_min), int(y_max) + 1))