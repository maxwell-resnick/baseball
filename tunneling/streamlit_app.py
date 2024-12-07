import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Ellipse
import seaborn as sns

st.set_page_config(layout="wide")

pitch_color_mapping = {
    'FF': 'red', 'SL': 'orange', 'SI': 'pink', 'CH': 'purple', 'FC': 'blue',
    'CU': 'lightgreen', 'ST': 'brown', 'FS': 'black', 'KC': 'darkgreen',
    'SV': 'yellow', 'FO': 'yellow', 'KN': 'yellow', 'SC': 'yellow'
}

@st.cache_data
def load_data():
    return pd.read_csv("tunnel_data.csv")

def main():
    st.markdown("""
        <div style="text-align: left;">
            <h1>Pitch Tunneling</h1>
            <h3 style="color: gray; font-size: 18px;">
                A Web App To Evaluate and Analyze Arsenal Interaction Effects
            </h3>
        </div>
    """, unsafe_allow_html=True)
    data = load_data()

    st.markdown("""
        <style>
            .centered-title {
                text-align: center;
                font-size: 20px; /* Adjust font size */
                font-weight: bold;
                margin-bottom: 5px; /* Optional: Add spacing between title and selectbox */
            }
        </style>
    """, unsafe_allow_html=True)

    default_player = "Skenes, Paul"
    if "selected_player" not in st.session_state:
        st.session_state.selected_player = default_player

    st.sidebar.markdown('<div class="centered-title">Select Player</div>', unsafe_allow_html=True)
    player_names = sorted(data['player_name'].unique())
    selected_player = st.sidebar.selectbox(
        "", 
        player_names, 
        index=player_names.index(st.session_state.selected_player),
        key="selected_player"
    )

    first_last_name = " ".join(selected_player.split(", ")[::-1])

    player_df = data[data['player_name'] == selected_player]

    st.sidebar.markdown('<div class="centered-title">Select Game Year</div>', unsafe_allow_html=True)
    available_years = sorted(player_df['game_year'].unique(), reverse=True)
    selected_year = st.sidebar.selectbox("", available_years)

    player_df = player_df[player_df['game_year'] == selected_year]

    tab1, tab2, tab3 = st.tabs(["Tunneling Metrics", "Kernel Density Plots", "Tunnel Ellipses Plots"])

    with tab1:
        st.markdown(f"""
            <div style="text-align: center;">
                <h1 style="font-size:30px;">Tunneling Metrics for {first_last_name}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="font-size:20px; font-weight:normal; margin-bottom:20px; line-height:1.5; text-align: center;">
                The values below answer the question:<br>
                <em>How much does the pitch's xRV/100 increase when factoring in arsenal interaction effects?</em>
            </div>
        """, unsafe_allow_html=True)

        filtered_df = player_df[player_df['player_name'] == selected_player]

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
                {"selector": "thead th", "props": [("font-size", "22px"), ("text-align", "center"), ("color", "black")]},
                {"selector": "tbody td", "props": [("font-size", "20px"), ("text-align", "center"), ("color", "black")]}
            ]).hide(axis="index")

            html_output = styled_metrics.to_html()
            return html_output

        if filtered_df.empty:
            st.warning(f"No data available for {selected_player} in {selected_year}.")
        else:
            st.markdown("""
                <style>
                    .center-content {
                        text-align: center;
                    }
                    .center-table {
                        display: table;
                        margin: 0 auto;
                    }
                </style>
            """, unsafe_allow_html=True)

            st.markdown('<div class="center-content"><h4>All Hitters</h4></div>', unsafe_allow_html=True)
            full_html = create_tunneling_table(filtered_df)
            st.markdown(f'<div class="center-table">{full_html}</div>', unsafe_allow_html=True)

            st.markdown('<div class="center-content"><h4>Left-Handed Hitters</h4></div>', unsafe_allow_html=True)
            left_html = create_tunneling_table(filtered_df[filtered_df['stand'] == 'L'])
            st.markdown(f'<div class="center-table">{left_html}</div>', unsafe_allow_html=True)

            st.markdown('<div class="center-content"><h4>Right-Handed Hitters</h4></div>', unsafe_allow_html=True)
            right_html = create_tunneling_table(filtered_df[filtered_df['stand'] == 'R'])
            st.markdown(f'<div class="center-table">{right_html}</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown(f"""
            <div style="text-align: center;">
                <h1 style="font-size:30px;">Density Plots for {first_last_name}</h1>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <style>
                .selectbox-container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    flex-direction: column;
                }
                .selectbox-label {
                    font-size: 20px; /* Larger font size for the label */
                    font-weight: bold; /* Optional: Make it bold */
                    margin-bottom: 10px; /* Space between label and selectbox */
                    text-align: center; /* Center the text */
                }
                div[data-baseweb="select"] > div {
                    width: 150px; /* Narrower width for the selectbox */
                    margin: 0 auto; /* Center the selectbox */
                }
            </style>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="selectbox-container">', unsafe_allow_html=True)
            st.markdown('<div class="selectbox-label">Select a pitch type:</div>', unsafe_allow_html=True)
            pitch = st.selectbox("", options=player_df['pitch_type'].unique(), key="pitch_type")
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="selectbox-container">', unsafe_allow_html=True)
            all_stands = ['All'] + list(player_df['stand'].unique())
            st.markdown('<div class="selectbox-label">Select a stand:</div>', unsafe_allow_html=True)
            stand = st.selectbox("", options=all_stands, index=0, key="stand")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
            <h3 style="text-align: center;">{pitch} Release and Approach Angle KDEs vs. Rest of Arsenal</h3>
        """, unsafe_allow_html=True)

        if stand != 'All':
            player_df = player_df[player_df['stand'] == stand]

        player_df = player_df.dropna(subset=['VRA', 'HRA', 'VAA', 'HAA'])

        fig, axes = plt.subplots(2, 2, figsize=(16, 8), sharey=True)

        plt.subplots_adjust(wspace=0.2, hspace=0.5)

        tick_size = 12

        sns.kdeplot(player_df[player_df['pitch_type'] == pitch]['VRA'], color='blue', label=pitch, lw=2, ax=axes[0, 0])
        sns.kdeplot(player_df[player_df['pitch_type'] != pitch]['VRA'], color='red', label="Rest of Arsenal", lw=2, ax=axes[0, 0])
        axes[0, 0].set_title('Vertical Release Angle', fontsize=18)
        axes[0, 0].set_xlabel('')
        axes[0, 0].set_ylabel('Density', fontsize=16)
        axes[0, 0].tick_params(axis='both', labelsize=tick_size)

        sns.kdeplot(player_df[player_df['pitch_type'] == pitch]['HRA'], color='blue', label=pitch, lw=2, ax=axes[0, 1])
        sns.kdeplot(player_df[player_df['pitch_type'] != pitch]['HRA'], color='red', label="Rest of Arsenal", lw=2, ax=axes[0, 1])
        axes[0, 1].set_title('Horizontal Release Angle', fontsize=18)
        axes[0, 1].set_xlabel('')
        axes[0, 1].tick_params(axis='both', labelsize=tick_size)

        sns.kdeplot(player_df[player_df['pitch_type'] == pitch]['VAA'], color='blue', label=pitch, lw=2, ax=axes[1, 0])
        sns.kdeplot(player_df[player_df['pitch_type'] != pitch]['VAA'], color='red', label="Rest of Arsenal", lw=2, ax=axes[1, 0])
        axes[1, 0].set_title('Vertical Approach Angle', fontsize=18)
        axes[1, 0].set_xlabel('')
        axes[1, 0].set_ylabel('Density', fontsize=16)
        axes[1, 0].tick_params(axis='both', labelsize=tick_size)

        sns.kdeplot(player_df[player_df['pitch_type'] == pitch]['HAA'], color='blue', label=pitch, lw=2, ax=axes[1, 1])
        sns.kdeplot(player_df[player_df['pitch_type'] != pitch]['HAA'], color='red', label="Rest of Arsenal", lw=2, ax=axes[1, 1])
        axes[1, 1].set_title('Horizontal Approach Angle', fontsize=18)
        axes[1, 1].set_xlabel('')
        axes[1, 1].tick_params(axis='both', labelsize=tick_size)

        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='lower center', ncol=2, fontsize=16, frameon=False)

        st.pyplot(fig)

    with tab3:
        st.markdown(f"""
            <div style="text-align: center;">
                <h1 style="font-size:30px;">Tunneling Plots for {first_last_name}</h1>
            </div>
        """, unsafe_allow_html=True)
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

        st.markdown("""
            <h3 style="text-align: center;">Tunnels at Release (1 StDev Ellipses)</h3>
        """, unsafe_allow_html=True)
        fig1, axs1 = plt.subplots(1, 2, figsize=(16, 8), sharey=True, sharex=True)
        plt.subplots_adjust(wspace=0.1)
        plot_pitcher_metrics(
            selected_player, player_df, fig1, axs1,
            x_metric='HRA', y_metric='VRA',
            x_label='Horizontal Release Angle',
            y_label='Vertical Release Angle'
        )
        st.pyplot(fig1)

        st.markdown("""
            <h3 style="text-align: center;">Tunnels at Home Plate (1 StDev Ellipses)</h3>
        """, unsafe_allow_html=True)
        fig2, axs2 = plt.subplots(1, 2, figsize=(16, 8), sharey=True, sharex=True)
        plt.subplots_adjust(wspace=0.1)
        plot_pitcher_metrics(
            selected_player, player_df, fig2, axs2,
            x_metric='HAA', y_metric='VAA',
            x_label='Horizontal Approach Angle',
            y_label='Vertical Approach Angle',
        )
        st.pyplot(fig2)

if __name__ == "__main__":
    main()