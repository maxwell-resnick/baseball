import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import gdown
from tunnel_helper_functions import create_tunneling_table, plot_pitcher_metrics

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    url = "https://drive.google.com/uc?id=1U8wPV1QrhVTv0uebehMMFKHQTROFaXs1"
    output = "tunnel_data.csv"
    gdown.download(url, output, quiet=False)
    return pd.read_csv(output)

def main():
    st.markdown("""
        <div style="text-align: left;">
            <h1>Pitch Tunneling</h1>
            <h3 style="color: gray; font-size: 22px;">
                A Quantitative Way To Evaluate and Analyze Arsenal Interaction Effects
            </h3>
            <h4 style="color: gray; font-size: 16px;">
                By Maxwell Resnick
            </h4>
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

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Tunneling Metrics", "Kernel Density Plots", "Tunnel Ellipses Plots", 
                                      "Research & Methodology", "About Me"])

    with tab1:
        st.markdown(f"""
            <div style="text-align: center;">
                <h1 style="font-size:30px;">Tunneling Metrics for {first_last_name}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="font-size:20px; font-weight:normal; margin-bottom:20px; line-height:1.5; text-align: center;">
                The values below answer the question:<br><br>
                <em>How much does the pitch's xRV/100 increase when factoring in arsenal interaction effects?</em>
            </div>
        """, unsafe_allow_html=True)

        filtered_df = player_df[player_df['player_name'] == selected_player]

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

            st.markdown("""
            <div style="font-size:22px; margin-top:40px; line-height:1.8;">
                <strong>Glossary:</strong><br>
                - <strong>Tunnel Boost:</strong> The pitch's xRV/100 increase when factoring in arsenal interaction effects in all three dimensions.<br>
                - <strong>X Tunnel:</strong> The pitch's xRV/100 increase when factoring in arsenal interaction effects on the <em>x</em> plane.<br>
                - <strong>Y Tunnel:</strong> The pitch's xRV/100 increase when factoring in arsenal interaction effects on the <em>y</em> plane.<br>
                - <strong>Z Tunnel:</strong> The pitch's xRV/100 increase when factoring in arsenal interaction effects on the <em>z</em> plane.<br>
                - <strong>Shape Tunnel:</strong> The pitch's xRV/100 increase when factoring in arsenal interaction effects on the <em>x</em> and <em>z</em> planes, ignoring the <em>y</em> plane.
            </div>
    """, unsafe_allow_html=True)

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

        st.markdown("""
            <div style="font-size:20px; font-weight:normal; margin-bottom:20px; line-height:1.5; text-align: center;">
                <em>These plots aim to demonstrate the similarity between a pitch's angles out of the hand and at the plate compared to the rest of the arsenal</em>
            </div>
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
            subset_df = player_df[player_df['stand'] == stand]
        else:
            subset_df = player_df.copy()

        subset_df = subset_df.dropna(subset=['VRA', 'HRA', 'VAA', 'HAA'])

        fig, axes = plt.subplots(2, 2, figsize=(16, 8), sharey=True)

        plt.subplots_adjust(wspace=0.2, hspace=0.5)

        tick_size = 12

        sns.kdeplot(subset_df[subset_df['pitch_type'] == pitch]['VRA'], color='blue', label=pitch, lw=2, ax=axes[0, 0])
        sns.kdeplot(subset_df[subset_df['pitch_type'] != pitch]['VRA'], color='red', label="Rest of Arsenal", lw=2, ax=axes[0, 0])
        axes[0, 0].set_title('Vertical Release Angle', fontsize=18)
        axes[0, 0].set_xlabel('')
        axes[0, 0].set_ylabel('Density', fontsize=16)
        axes[0, 0].tick_params(axis='both', labelsize=tick_size)

        sns.kdeplot(subset_df[subset_df['pitch_type'] == pitch]['HRA'], color='blue', label=pitch, lw=2, ax=axes[0, 1])
        sns.kdeplot(subset_df[subset_df['pitch_type'] != pitch]['HRA'], color='red', label="Rest of Arsenal", lw=2, ax=axes[0, 1])
        axes[0, 1].set_title('Horizontal Release Angle', fontsize=18)
        axes[0, 1].set_xlabel('')
        axes[0, 1].tick_params(axis='both', labelsize=tick_size)

        sns.kdeplot(subset_df[subset_df['pitch_type'] == pitch]['VAA'], color='blue', label=pitch, lw=2, ax=axes[1, 0])
        sns.kdeplot(subset_df[subset_df['pitch_type'] != pitch]['VAA'], color='red', label="Rest of Arsenal", lw=2, ax=axes[1, 0])
        axes[1, 0].set_title('Vertical Approach Angle', fontsize=18)
        axes[1, 0].set_xlabel('')
        axes[1, 0].set_ylabel('Density', fontsize=16)
        axes[1, 0].tick_params(axis='both', labelsize=tick_size)

        sns.kdeplot(subset_df[subset_df['pitch_type'] == pitch]['HAA'], color='blue', label=pitch, lw=2, ax=axes[1, 1])
        sns.kdeplot(subset_df[subset_df['pitch_type'] != pitch]['HAA'], color='red', label="Rest of Arsenal", lw=2, ax=axes[1, 1])
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

        st.markdown("""
            <div style="font-size:20px; font-weight:normal; margin-bottom:20px; line-height:1.5; text-align: center;">
                <em>These plots illustrate the "tunnel" each pitch takes out of the hand compared to their separation at the plate</em>
            </div>
        """, unsafe_allow_html=True)

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
    
    with tab4:
        st.markdown(f"""
            <div style="text-align: center;">
                <h1 style="font-size:30px;">Research & Methodology</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="font-size: 18px; line-height: 1.6;">
            Learn more about the methodology behind quantifying pitch tunneling by reading the article below:
            <br><br>
            <a href="https://medium.com/@maxwellresnick/quantifying-pitch-tunneling-acc0cfcdff02" 
            style="font-weight: bold; font-size: 18px; color: #0366d6; text-decoration: none;">
                The Science of Pitch Tunneling: Quantifying Arsenal Interaction Effects through Kernel Density Estimation, 
                XGBoost, and SHAP
            </a>
            <br><br>
            Here are some of my tweets from the research process:
            <ul>
                <li><a href="https://x.com/MaxwellResnick/status/1861500450274431044" 
                    style="font-size: 18px; color: #0366d6; text-decoration: none;">
                    Quantifying Pitch Tunneling Thread
                </a></li>
                <li><a href="https://x.com/MaxwellResnick/status/1862652688816595067" 
                    style="font-size: 18px; color: #0366d6; text-decoration: none;">
                    Joe Ryan vs. Spencer Arrighetti
                </a></li>
                <li><a href="https://x.com/MaxwellResnick/status/1864374760936759301" 
                    style="font-size: 18px; color: #0366d6; text-decoration: none;">
                    Do Sweepers Tunnel?
                </a></li>
                <li><a href="https://x.com/MaxwellResnick/status/1862209303861473322" 
                    style="font-size: 18px; color: #0366d6; text-decoration: none;">
                    Does Effectively Wild Exist?
                </a></li>
                <li><a href="https://x.com/MaxwellResnick/status/1864414376775831860" 
                    style="font-size: 18px; color: #0366d6; text-decoration: none;">
                    Felix Bautista's Otherworldly Splitter
                </a></li>
                <li><a href="https://x.com/MaxwellResnick/status/1861113179843019107" 
                    style="font-size: 18px; color: #0366d6; text-decoration: none;">
                    Logan Webb's Sneaky Four-Seamer
                </a></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with tab5:
        st.markdown(f"""
            <div style="text-align: center;">
                <h1 style="font-size:30px;">About Me</h1>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="font-size: 18px; line-height: 1.6;">
            I am a fourth-year undergraduate at the University of Chicago studying Data Science and Economics, who has previously worked in the front offices of 
            the Seattle Mariners and the Philadelphia Phillies. At UChicago, I work as an Assistant Coach of the baseball team, with a focus on analytics.
            I have always found the phenomenon of pitch tunneling to be fascinating. Many deem it one of baseball's unquantifiable artistic elements, but 
            I believe that it can be viewed as a science as well. If you like my work, please check out my X account; I post plenty of baseball analytics content on it.
            My goal is to grow baseball analytics in the public space, so if you have any questions or would like to chat about any particular methodology decisions
            I made, please don't hesitate to reach out on social media!
            <br><br>
        </div>
        <div style="text-align: center;">
            <div style="display: inline-flex; gap: 20px;">
                <a href="https://x.com/MaxwellResnick" 
                style="font-size: 18px; color: #0366d6; text-decoration: none;">
                X
                </a>
                <a href="https://www.linkedin.com/in/maxwell-resnick/" 
                style="font-size: 18px; color: #0366d6; text-decoration: none;">
                LinkedIn
                </a>
                <a href="https://github.com/maxwell-resnick/baseball/tree/master" 
                style="font-size: 18px; color: #0366d6; text-decoration: none;">
                GitHub
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()