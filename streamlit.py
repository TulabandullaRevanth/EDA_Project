import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.colors import n_colors
# Helper function to safely display Plotly figures
def safe_plotly_display(fig):
    """Safely render a Plotly figure in Streamlit."""
    try:
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error displaying chart: {e}")

st.set_page_config(layout="wide", page_title="Election Analysis Dashboard")

# -----------------------
# Data Loading
# -----------------------
@st.cache_data
def load_data():
    df_all = pd.read_csv("cleaned_combined_data.csv")
    state_codes = pd.read_csv("dim_states_codes.csv")
    party_summary = pd.read_csv("party_summary.csv")
    return df_all, state_codes, party_summary

df_all, state_codes, party_summary = load_data()

# Basic preprocessing
df_all = df_all.copy()
# Ensure numeric types where expected
for c in ['total_votes', 'total_electors', 'general_votes', 'age']:
    if c in df_all.columns:
        df_all[c] = pd.to_numeric(df_all[c], errors='coerce').fillna(0)

# turnout %
df_all['turnout'] = (df_all['total_votes'] / df_all['total_electors']) * 100
# unify some column names if both exist
if 'state_name' not in df_all.columns and 'state' in df_all.columns:
    df_all['state_name'] = df_all['state']

# Separate years
df_2014 = df_all[df_all['year'] == 2014].copy()
df_2019 = df_all[df_all['year'] == 2019].copy()

# Helper: winners per year
def get_winners(df):
    idx = df.groupby('pc_name')['total_votes'].idxmax()
    winners = df.loc[idx, ['pc_name', 'party', 'total_votes', 'turnout', 'state_name', 'candidate']].copy()
    return winners

winners_2014 = get_winners(df_2014)
winners_2019 = get_winners(df_2019)

# Header & sidebar
import streamlit as st

# Sidebar
st.sidebar.title("📊 Lok Sabha Election Analysis Dashboard")
# --- Main selection ---
selection = st.sidebar.radio(
"Select an Analysis",
    [
        "1. Top 5 / Bottom 5 constituencies of 2014 & 2019 in terms of voter turnout ratio",
        "2. Top 5 / Bottom 5 states of 2014 & 2019 in terms of voter turnout ratio",
        "3. Which Constituencies have elected the same party for two consecutive elections, rank them by % of votes to that winning party in 2019",
        "4. Which constituencies have voted for different parties in two elections (list top 10 based on difference (2014-2019) in winner vote percentage in two elections).",
        "5. Top 5 candidates based on margin difference with runners in 2014 and 2019?",
        "6. % split of votes of parties between 2014 vs 2019 at national level?",
        "7. % split of votes of parties between 2014 vs 2019 at state level?",
        "8. Top 5 Constituencies Gaining Votes (Major Parties)",
        "9. Top 5 Constituencies Losing Votes (Major Parties)",
        "10. Constituency with Highest NOTA Votes",
        "11. Candidates from Parties <10% State Vote Share",
        "12. States Highest Increase in voter Turnout",
        "13. States Largest Decline in voter Turnout",
        "14. Most Competitive Elections (smallest winning margins)",
        "15. Largest Shift in Vote Share by Constituency",
        "16. Candidates from Low Vote Share Parties",
        "17. NOTA Votes by State and Constituency",
        "18. Parties Gaining Most new Constituencies in 2019 compared to 2014",
        "19. Consistent High/Low Voter Turnout Constituencies in both elections",
        "20. Age groups contributed most to voter turnout changes between 2014 and 2019",
        "21. Which states or constituencies saw the highest increase in youth (18-25) compare with winning party?",
    ]
)

# ---------------------------------------------------------
# 1. Top/Bottom Constituencies Turnout
# ---------------------------------------------------------
if selection =="1. Top 5 / Bottom 5 constituencies of 2014 & 2019 in terms of voter turnout ratio":
    st.header("Top & Bottom Constituencies by Voter Turnout (2014 & 2019)")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("2014 — Top 10 by Turnout")
        top_2014 = df_2014.sort_values('turnout', ascending=False).head(10)
        st.dataframe(top_2014[['pc_name', 'state_name', 'turnout']].reset_index(drop=True))
        fig = px.bar(top_2014.head(10).sort_values('turnout'), x='turnout', y='pc_name', orientation='h',
                     title='2014 Top Constituencies by Turnout')
        safe_plotly_display(fig)

    with col2:
        st.subheader("2014 — Bottom 10 by Turnout")
        bottom_2014 = df_2014.sort_values('turnout').head(10)
        st.dataframe(bottom_2014[['pc_name', 'state_name', 'turnout']].reset_index(drop=True))
        fig2 = px.bar(bottom_2014.head(10).sort_values('turnout', ascending=True), x='turnout', y='pc_name', orientation='h',
                      title='2014 Bottom Constituencies by Turnout')
        safe_plotly_display(fig2)

    st.markdown("---")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("2019 — Top 10 by Turnout")
        top_2019 = df_2019.sort_values('turnout', ascending=False).head(10)
        st.dataframe(top_2019[['pc_name', 'state_name', 'turnout']].reset_index(drop=True))
        fig3 = px.bar(top_2019.head(10).sort_values('turnout'), x='turnout', y='pc_name', orientation='h',
                      title='2019 Top Constituencies by Turnout')
        safe_plotly_display(fig3)

    with col4:
        st.subheader("2019 — Bottom 10 by Turnout")
        bottom_2019 = df_2019.sort_values('turnout').head(10)
        st.dataframe(bottom_2019[['pc_name', 'state_name', 'turnout']].reset_index(drop=True))
        fig4 = px.bar(bottom_2019.head(10).sort_values('turnout', ascending=True), x='turnout', y='pc_name', orientation='h',
                      title='2019 Bottom Constituencies by Turnout')
        safe_plotly_display(fig4)

# ---------------------------------------------------------
# 2. Top/Bottom States Turnout
# ---------------------------------------------------------
elif selection =="2. Top 5 / Bottom 5 states of 2014 & 2019 in terms of voter turnout ratio":
    st.header("Top & Bottom States by Average Voter Turnout (2014 & 2019)")
    state_turnout_2014 = df_2014.groupby('state_name')['turnout'].mean().sort_values()
    state_turnout_2019 = df_2019.groupby('state_name')['turnout'].mean().sort_values()

    st.subheader("2014 — Top 10")
    st.dataframe(state_turnout_2014.tail(10).reset_index().rename(columns={'turnout':'avg_turnout'}))
    fig = px.bar(state_turnout_2014.tail(20).reset_index(), x='state_name', y='turnout', title='2014 Average Turnout by State')
    safe_plotly_display(fig)

    st.subheader("2019 — Top 10")
    st.dataframe(state_turnout_2019.tail(10).reset_index().rename(columns={'turnout':'avg_turnout'}))
    fig2 = px.bar(state_turnout_2019.tail(20).reset_index(), x='state_name', y='turnout', title='2019 Average Turnout by State')
    safe_plotly_display(fig2)

# ---------------------------------------------------------
# 3. Same Party Constituencies
# ---------------------------------------------------------
elif selection == "3. Which Constituencies have elected the same party for two consecutive elections, rank them by % of votes to that winning party in 2019":
    st.header("🏆 Constituencies Electing the Same Party in 2014 & 2019")

    # Ensure required columns exist
    required_cols = {'pc_name', 'party', 'total_votes', 'total_electors', 'year'}
    if not required_cols.issubset(df_all.columns):
        st.error(f"Required columns missing: {required_cols - set(df_all.columns)}")
    else:
        # Split into election years
        df_2014 = df_all[df_all['year'] == 2014].copy()
        df_2019 = df_all[df_all['year'] == 2019].copy()

        # Compute winners per constituency
        winners_2014 = (
            df_2014.groupby('pc_name')
            .agg({'party': 'first', 'total_votes': 'sum', 'total_electors': 'sum'})
            .reset_index()
        )
        winners_2019 = (
            df_2019.groupby('pc_name')
            .agg({'party': 'first', 'total_votes': 'sum', 'total_electors': 'sum'})
            .reset_index()
        )

        # Merge
        merged_winners = pd.merge(
            winners_2014,
            winners_2019,
            on='pc_name',
            suffixes=('_2014', '_2019')
        )

        # Filter same-party constituencies
        same_party = merged_winners[
            merged_winners['party_2014'].str.strip().str.upper() ==
            merged_winners['party_2019'].str.strip().str.upper()
        ].copy()

        if same_party.empty:
            st.warning("⚠️ No constituencies found where the same party won in both elections.")
        else:
            # Compute 2019 vote %
            same_party['vote_pct_2019'] = (
                same_party['total_votes_2019'] /
                same_party['total_electors_2019'] * 100
            )

            # Rank by vote %
            ranked = same_party[['pc_name', 'party_2019', 'vote_pct_2019']].sort_values(
                by='vote_pct_2019', ascending=False
            )

            # Display
            st.subheader("Top 10 — Highest 2019 Vote % (Same Party Wins 2014 & 2019)")
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(ranked.head(10).round(2).reset_index(drop=True))

            with col2:
                fig = px.bar(
                    ranked.head(10),
                    x='vote_pct_2019',
                    y='pc_name',
                    color='party_2019',
                    orientation='h',
                    title='Top 10 Same-Party Wins (2014 → 2019)',
                    text='vote_pct_2019'
                )
                fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
                safe_plotly_display(fig)

# ---------------------------------------------------------
# 4. Party Switch Constituencies (Enhanced)
# ---------------------------------------------------------
elif selection == "4. Which constituencies have voted for different parties in two elections (list top 10 based on difference (2014-2019) in winner vote percentage in two elections).":
    st.header("🔄 Constituencies Voting for Different Parties (2014 vs 2019)")

    # Compute winners per constituency
    winners_2014 = (
        df_2014.groupby('pc_name')
        .agg({'party': 'first', 'total_votes': 'sum', 'total_electors': 'sum'})
        .reset_index()
    )
    winners_2019 = (
        df_2019.groupby('pc_name')
        .agg({'party': 'first', 'total_votes': 'sum', 'total_electors': 'sum'})
        .reset_index()
    )

    # Merge
    merged_winners = pd.merge(
        winners_2014,
        winners_2019,
        on='pc_name',
        suffixes=('_2014', '_2019')
    )

    # Filter different-party constituencies
    diff_party = merged_winners[
        merged_winners['party_2014'].str.strip().str.upper() !=
        merged_winners['party_2019'].str.strip().str.upper()
    ].copy()

    if diff_party.empty:
        st.warning("⚠️ No constituencies found where different parties won in the two elections.")
    else:
        # Compute vote % for both years
        diff_party['vote_pct_2014'] = (
            diff_party['total_votes_2014'] /
            diff_party['total_electors_2014'] * 100
        )
        diff_party['vote_pct_2019'] = (
            diff_party['total_votes_2019'] /
            diff_party['total_electors_2019'] * 100
        )

        # Compute absolute difference in vote %
        diff_party['vote_pct_diff'] = (
            diff_party['vote_pct_2019'] - diff_party['vote_pct_2014']
        ).abs()

        # Rank by difference
        ranked_diff = diff_party[['pc_name', 'party_2014', 'vote_pct_2014', 'party_2019', 'vote_pct_2019', 'vote_pct_diff']].sort_values(
            by='vote_pct_diff', ascending=False
        )

        # Display
        st.subheader("Top 10 — Largest Vote % Difference (Different Party Wins)")
        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(ranked_diff.head(10).round(2).reset_index(drop=True))
        with col2:
            fig = px.bar(
                ranked_diff.head(10),
                x='vote_pct_diff',
                y='pc_name',
                color='party_2019',
                title='Top 10 Constituencies by Vote % Difference (2014 vs 2019)',
                orientation='h'
            )
            safe_plotly_display(fig)

# ---------------------------------------------------------
# 5. Top Candidates by Margin Difference
# ---------------------------------------------------------
elif selection == "5. Top 5 candidates based on margin difference with runners in 2014 and 2019?":
    st.header("Top Candidates by Margin Difference (2014 vs 2019)")

    def calc_margin(df):
        rows = []
        for pc, group in df.groupby('pc_name'):
            votes_sorted = group.sort_values('total_votes', ascending=False)['total_votes'].values
            margin = votes_sorted[0] - votes_sorted[1] if len(votes_sorted) > 1 else votes_sorted[0]
            rows.append({'pc_name': pc, 'margin': margin})
        return pd.DataFrame(rows)

    margin_2014 = calc_margin(df_2014)
    margin_2019 = calc_margin(df_2019)
    merged_margin = margin_2014.merge(margin_2019, on='pc_name', suffixes=('_2014', '_2019'))
    merged_margin['margin_diff'] = merged_margin['margin_2019'] - merged_margin['margin_2014']

    top_margin_diff = merged_margin.sort_values('margin_diff', ascending=False).head(10)
    st.dataframe(top_margin_diff)
    fig = px.bar(top_margin_diff.sort_values('margin_diff'), x='margin_diff', y='pc_name', orientation='h',
                 title='Top Constituencies with Increase in Winning Margin (2014→2019)')
    safe_plotly_display(fig)

# ---------------------------------------------------------
# 6. National Party Vote Share Comparison
# ---------------------------------------------------------
elif selection == "6. % split of votes of parties between 2014 vs 2019 at national level?":
    st.header("National Level Vote Share Comparison (2014 vs 2019)")
    party_votes_2014 = df_2014.groupby('party')['total_votes'].sum()
    party_votes_2019 = df_2019.groupby('party')['total_votes'].sum()
    total_votes_2014 = party_votes_2014.sum()
    total_votes_2019 = party_votes_2019.sum()

    vote_share_df = pd.DataFrame({
        'party': list(set(party_votes_2014.index).union(set(party_votes_2019.index))),
    }).set_index('party')
    vote_share_df['2014'] = party_votes_2014
    vote_share_df['2019'] = party_votes_2019
    vote_share_df = vote_share_df.fillna(0)
    vote_share_df['2014_pct'] = vote_share_df['2014'] / total_votes_2014 * 100
    vote_share_df['2019_pct'] = vote_share_df['2019'] / total_votes_2019 * 100
    vote_share_df = vote_share_df.reset_index().sort_values('2019_pct', ascending=False)

    st.dataframe(vote_share_df[['party', '2014_pct', '2019_pct']].head(30).round(2))
    fig = px.bar(vote_share_df, x='party', y=['2014_pct', '2019_pct'], barmode='group', title="Party Vote Shares Nationally (%)")
    safe_plotly_display(fig)

# ---------------------------------------------------------
# 7. State Party Vote Share Comparison
# ---------------------------------------------------------
elif selection == "7. % split of votes of parties between 2014 vs 2019 at state level?":
    st.header("State Level Party Vote Share Comparison (2014 vs 2019)")

    state_party_2014 = df_2014.groupby(['state_name', 'party'])['total_votes'].sum().reset_index()
    state_party_2019 = df_2019.groupby(['state_name', 'party'])['total_votes'].sum().reset_index()

    merged_state_party = state_party_2014.merge(
        state_party_2019,
        on=['state_name', 'party'],
        how='outer',
        suffixes=('_2014', '_2019')
    ).fillna(0)

    merged_state_party['vote_share_2014'] = merged_state_party['total_votes_2014'] / merged_state_party.groupby('state_name')['total_votes_2014'].transform('sum') * 100
    merged_state_party['vote_share_2019'] = merged_state_party['total_votes_2019'] / merged_state_party.groupby('state_name')['total_votes_2019'].transform('sum') * 100

    filtered = merged_state_party[(merged_state_party['vote_share_2014'] > 0) | (merged_state_party['vote_share_2019'] > 0)]
    state_selected = st.selectbox("Select State", sorted(filtered['state_name'].unique()))
    state_data = filtered[filtered['state_name'] == state_selected].sort_values('vote_share_2019', ascending=False)

    st.dataframe(state_data[['party', 'vote_share_2014', 'vote_share_2019']].reset_index(drop=True).round(2))
    fig = px.bar(state_data, x='party', y=['vote_share_2014', 'vote_share_2019'], barmode='group',
                 title=f"Party Vote Share in {state_selected} (2014 vs 2019) (%)")
    safe_plotly_display(fig)

# ---------------------------------------------------------
# 8. Top Constituencies Gaining Votes (Major Parties)
# ---------------------------------------------------------
elif selection == "8. Top 5 Constituencies Gaining Votes (Major Parties)":
    st.header("Top Constituencies Gaining Votes (Major Parties)")
    parties = st.multiselect("Select parties to inspect", options=sorted(df_all['party'].unique()), default=['BJP', 'INC'] if 'BJP' in df_all['party'].unique() else df_all['party'].unique()[:2])

    votes_party_2014 = df_2014[df_2014['party'].isin(parties)].groupby(['pc_name', 'party'])['total_votes'].sum().reset_index()
    votes_party_2019 = df_2019[df_2019['party'].isin(parties)].groupby(['pc_name', 'party'])['total_votes'].sum().reset_index()
    merged_votes = votes_party_2014.merge(votes_party_2019, on=['pc_name', 'party'], how='outer', suffixes=('_2014', '_2019')).fillna(0)
    merged_votes['vote_diff'] = merged_votes['total_votes_2019'] - merged_votes['total_votes_2014']

    for party in parties:
        st.subheader(f"{party} — Top Gains")
        party_df = merged_votes[merged_votes['party'] == party].sort_values('vote_diff', ascending=False).head(10)
        st.dataframe(party_df[['pc_name', 'total_votes_2014', 'total_votes_2019', 'vote_diff']])
        fig = px.bar(party_df.sort_values('vote_diff'), x='vote_diff', y='pc_name', orientation='h', title=f"{party} — Top 10 Gains (2014→2019)")
        safe_plotly_display(fig)

# ---------------------------------------------------------
# 9. Top Constituencies Losing Votes (Major Parties)
# ---------------------------------------------------------
elif selection =="9. Top 5 Constituencies Losing Votes (Major Parties)":
    st.header("Top Constituencies Losing Votes (Major Parties)")
    parties = st.multiselect("Select parties to inspect (losing)", options=sorted(df_all['party'].unique()), default=['BJP', 'INC'] if 'BJP' in df_all['party'].unique() else df_all['party'].unique()[:2])

    votes_party_2014 = df_2014[df_2014['party'].isin(parties)].groupby(['pc_name', 'party'])['total_votes'].sum().reset_index()
    votes_party_2019 = df_2019[df_2019['party'].isin(parties)].groupby(['pc_name', 'party'])['total_votes'].sum().reset_index()
    merged_votes = votes_party_2014.merge(votes_party_2019, on=['pc_name', 'party'], how='outer', suffixes=('_2014', '_2019')).fillna(0)
    merged_votes['vote_diff'] = merged_votes['total_votes_2019'] - merged_votes['total_votes_2014']

    for party in parties:
        st.subheader(f"{party} — Top Losses")
        party_df = merged_votes[merged_votes['party'] == party].sort_values('vote_diff').head(10)
        st.dataframe(party_df[['pc_name', 'total_votes_2014', 'total_votes_2019', 'vote_diff']])
        fig = px.bar(party_df.sort_values('vote_diff'), x='vote_diff', y='pc_name', orientation='h', title=f"{party} — Top 10 Losses (2014→2019)")
        safe_plotly_display(fig)

# ---------------------------------------------------------
# 10. Constituency with Highest NOTA Votes
# ---------------------------------------------------------
elif selection == "10. Constituency with Highest NOTA Votes":
    st.header("Constituency with Highest NOTA Votes (2014 & 2019)")
    nota_2014 = df_2014[df_2014['party'] == 'NOTA'].groupby('pc_name')['total_votes'].sum().rename('nota_2014')
    nota_2019 = df_2019[df_2019['party'] == 'NOTA'].groupby('pc_name')['total_votes'].sum().rename('nota_2019')
    nota_all = pd.concat([nota_2014, nota_2019], axis=1).fillna(0)
    nota_all['total_nota'] = nota_all['nota_2014'] + nota_all['nota_2019']
    top5 = nota_all.sort_values('total_nota', ascending=False).head(10).reset_index()
    st.dataframe(top5)
    fig = px.bar(top5, x='pc_name', y=['nota_2014', 'nota_2019'], barmode='group', title='NOTA Votes by Constituency (2014 vs 2019)')
    safe_plotly_display(fig)

# ---------------------------------------------------------
# 11. Candidates from Parties <10% State Vote Share
# ---------------------------------------------------------
elif selection == "11. Candidates from Parties <10% State Vote Share":
    st.header("Candidates from Parties with <10% State Vote Share (2019)")
    state_party_totals = df_2019.groupby(['state_name', 'party'])['total_votes'].sum().reset_index()
    state_totals = df_2019.groupby('state_name')['total_votes'].sum().reset_index().rename(columns={'total_votes':'state_total'})
    merged = state_party_totals.merge(state_totals, on='state_name')
    merged['pct_state'] = merged['total_votes'] / merged['state_total'] * 100
    low_parties = merged[merged['pct_state'] < 10]

    winners19 = df_2019.loc[df_2019.groupby('pc_name')['total_votes'].idxmax()][['pc_name','state_name','party','candidate','total_votes']]
    result = winners19.merge(low_parties[['state_name','party']], on=['state_name','party'])
    st.dataframe(result.sort_values(['state_name','pc_name']).reset_index(drop=True))
    fig = px.bar(result.groupby('state_name').size().reset_index(name='count'), x='state_name', y='count', title='How Many Winners belong to <10% State Parties (2019)')
    safe_plotly_display(fig)

# ---------------------------------------------------------
# 12. States Highest Increase in Turnout
# ---------------------------------------------------------
elif selection == "12. States Highest Increase in voter Turnout":
    st.header("States with Highest Increase in Turnout (2014 → 2019)")
    state_turn_2014 = df_2014.groupby('state_name')['turnout'].mean().reset_index(name='t4')
    state_turn_2019 = df_2019.groupby('state_name')['turnout'].mean().reset_index(name='t9')
    inc = state_turn_2014.merge(state_turn_2019, on='state_name')
    inc['change'] = inc['t9'] - inc['t4']
    top5 = inc.sort_values('change', ascending=False).head(10)
    st.dataframe(top5.round(2))
    fig = px.bar(top5, x='state_name', y='change', title='States with Highest Increase in Turnout (2014→2019)')
    safe_plotly_display(fig)

# ---------------------------------------------------------
# 13. States Largest Decline in Turnout
# ---------------------------------------------------------
elif selection == "13. States Largest Decline in voter Turnout":
    st.header("📉 States with Largest Decline in Turnout (2014 → 2019)")

    # Calculate average turnout per state for both years
    state_turn_2014 = df_2014.groupby('state_name')['turnout'].mean().reset_index(name='t4')
    state_turn_2019 = df_2019.groupby('state_name')['turnout'].mean().reset_index(name='t9')

    # Merge both years
    dec = state_turn_2014.merge(state_turn_2019, on='state_name')

    # Compute change (negative = decline)
    dec['change'] = dec['t9'] - dec['t4']

    # Sort by largest decline (most negative change)
    top10_decline = dec.sort_values('change', ascending=True).head(10).reset_index(drop=True)

    # Display data
    st.dataframe(top10_decline.round(2))

    # Horizontal bar chart (largest decline on top)
    fig = px.bar(
        top10_decline.sort_values('change', ascending=True),
        x='change',
        y='state_name',
        orientation='h',
        text='change',
        title='Top 10 States with Largest Decline in Voter Turnout (2014 → 2019)',
    )
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})  # biggest decline at top

    safe_plotly_display(fig)

# ---------------------------------------------------------
# 14. Most Competitive Elections (Smallest Winning Margins)
# ---------------------------------------------------------
elif selection == "14. Most Competitive Elections (Smallest Winning Margins)":
    st.header("⚔️ Most Competitive Elections (Smallest Winning Margins)")

    # Ensure correct column types
    df_all['general_votes'] = pd.to_numeric(df_all['general_votes'], errors='coerce')
    df_all = df_all.dropna(subset=['general_votes', 'pc_name', 'year'])

    # Split by year
    df_2014 = df_all[df_all['year'] == 2014].copy()
    df_2019 = df_all[df_all['year'] == 2019].copy()

    # Define reusable function (your original logic)
    def compute_competitive(df, year):
        df_sorted = df.sort_values(['pc_name', 'general_votes'], ascending=[True, False])
        top2 = df_sorted.groupby('pc_name').head(2)
        margin = top2.groupby('pc_name').apply(
            lambda x: x.iloc[0]['general_votes'] - x.iloc[1]['general_votes']
            if len(x) > 1 else 0
        ).reset_index(name='margin')
        # Merge with extra details for display
        winners = df_sorted.groupby('pc_name').first().reset_index()
        competitive = margin.merge(
            winners[['pc_name', 'state_name', 'candidate', 'party']],
            on='pc_name', how='left'
        )
        competitive['year'] = year
        return competitive.sort_values('margin').head(10)

    # Compute for both years
    competitive_2014 = compute_competitive(df_2014, 2014)
    competitive_2019 = compute_competitive(df_2019, 2019)

    # Display results in Streamlit
    st.subheader("Top 10 Most Competitive Constituencies (2014)")
    st.dataframe(
        competitive_2014.rename(columns={
            'state_name': 'State',
            'pc_name': 'Constituency',
            'candidate': 'Winning Candidate',
            'party': 'Party',
            'margin': 'Winning Margin (Votes)'
        })
    )

    st.subheader("Top 10 Most Competitive Constituencies (2019)")
    st.dataframe(
        competitive_2019.rename(columns={
            'state_name': 'State',
            'pc_name': 'Constituency',
            'candidate': 'Winning Candidate',
            'party': 'Party',
            'margin': 'Winning Margin (Votes)'
        })
    )

    # Visualization for 2019
    fig = px.bar(
        competitive_2019.sort_values('margin', ascending=True),
        x='margin',
        y='pc_name',
        color='party',
        orientation='h',
        title='Top 10 Most Competitive Constituencies (2019)',
        hover_data=['state_name', 'candidate', 'party']
    )
    fig.update_layout(
        xaxis_title='Winning Margin (Votes)',
        yaxis_title='Constituency',
        yaxis={'categoryorder': 'total ascending'}
    )
    safe_plotly_display(fig)

# ---------------------------------------------------------
# 15. Largest Shift in Vote Share by Constituency
# ---------------------------------------------------------
elif selection == "15. Largest Shift in Vote Share by Constituency":
    st.header("📊 Largest Shift in Vote Share by Constituency (Any Party)")

    # --- Compute vote share for 2014 ---
    vs14 = df_2014.groupby(['pc_name', 'party'])['total_votes'].sum().reset_index()
    tot14 = df_2014.groupby('pc_name')['total_votes'].sum().reset_index(name='pc_total_2014')
    vs14 = vs14.merge(tot14, on='pc_name')
    vs14['share_2014'] = vs14['total_votes'] / vs14['pc_total_2014'] * 100

    # --- Compute vote share for 2019 ---
    vs19 = df_2019.groupby(['pc_name', 'party'])['total_votes'].sum().reset_index()
    tot19 = df_2019.groupby('pc_name')['total_votes'].sum().reset_index(name='pc_total_2019')
    vs19 = vs19.merge(tot19, on='pc_name')
    vs19['share_2019'] = vs19['total_votes'] / vs19['pc_total_2019'] * 100

    # --- Merge both years ---
    merged_share = vs14.merge(vs19, on=['pc_name', 'party'], how='inner')
    merged_share['vote_share_change'] = merged_share['share_2019'] - merged_share['share_2014']
    merged_share['abs_change'] = merged_share['vote_share_change'].abs()

    # --- Top 20 biggest shifts ---
    top_shift = merged_share.sort_values('abs_change', ascending=False).head(20)

    # --- Table ---
    st.subheader("Top 20 Constituencies with Largest Vote Share Change")
    st.dataframe(
        top_shift[['pc_name', 'party', 'share_2014', 'share_2019', 'vote_share_change']]
        .round(2)
        .rename(columns={
            'pc_name': 'Constituency',
            'party': 'Party',
            'share_2014': 'Vote Share 2014 (%)',
            'share_2019': 'Vote Share 2019 (%)',
            'vote_share_change': 'Change (2019−2014)'
        })
    )

    # --- 📊 Grouped Bar Chart for 2014 vs 2019 ---
    st.subheader("Vote Share Comparison: 2014 vs 2019")
    plot_data = pd.melt(
        top_shift,
        id_vars=['pc_name', 'party'],
        value_vars=['share_2014', 'share_2019'],
        var_name='Year',
        value_name='Vote Share (%)'
    )

    # Clean year labels
    plot_data['Year'] = plot_data['Year'].replace({'share_2014': '2014', 'share_2019': '2019'})

    fig = px.bar(
        plot_data,
        x='pc_name',
        y='Vote Share (%)',
        color='Year',
        barmode='group',
        facet_col='party',
        facet_col_wrap=2,
        title='Top 20 Constituencies — Party Vote Share Comparison (2014 vs 2019)',
        hover_data=['party']
    )

    fig.update_layout(
        showlegend=True,
        xaxis_title="Constituency",
        yaxis_title="Vote Share (%)",
        height=800
    )

    safe_plotly_display(fig)

    # --- Optional: Highlight change separately ---
    st.subheader("Change in Vote Share (2019−2014)")
    fig_change = px.bar(
        top_shift.sort_values('vote_share_change'),
        x='vote_share_change',
        y='pc_name',
        color='party',
        orientation='h',
        title='Change in Vote Share (2019−2014)',
        hover_data=['party', 'share_2014', 'share_2019']
    )
    safe_plotly_display(fig_change)

# ---------------------------------------------------------
# 16. Candidates from Low Vote Share Parties
# ---------------------------------------------------------
elif selection == "16. Candidates from Low Vote Share Parties":
    st.header("🏳️ Candidates from Low State-Level Vote Share Parties (Both Years)")

    for year in [2014, 2019]:
        st.subheader(f"🗳️ {year}")

        # Filter for that year
        df_year = df_all[df_all['year'] == year]

        # Compute total votes per party per state
        party_state_votes = df_year.groupby(['state_name', 'party'])['total_votes'].sum().reset_index()
        total_state_votes = df_year.groupby('state_name')['total_votes'].sum().reset_index(name='total_votes_state')

        merged = party_state_votes.merge(total_state_votes, on='state_name')
        merged['vote_pct'] = merged['total_votes'] / merged['total_votes_state'] * 100

        # Parties with <10% vote share in state
        low_share_parties = merged[merged['vote_pct'] < 10]

        # Find winners in each constituency
        winners_year = df_year.loc[df_year.groupby('pc_name')['total_votes'].idxmax()][
            ['pc_name', 'state_name', 'party', 'candidate', 'total_votes']
        ]

        # Merge winners with low-share parties
        result = winners_year.merge(
            low_share_parties[['state_name', 'party']],
            on=['state_name', 'party']
        )

        # Display table of top 50
        st.dataframe(
            result.sort_values(['state_name', 'pc_name']).reset_index(drop=True).head(50)
        )

        # -------------------------------------------------
        # 📊 Visualization 1: Count of Wins by Low-Share Parties per State
        # -------------------------------------------------
        wins_by_state = result.groupby('state_name').size().reset_index(name='num_constituencies')
        if not wins_by_state.empty:
            fig_state = px.bar(
                wins_by_state.sort_values('num_constituencies', ascending=False),
                x='state_name',
                y='num_constituencies',
                title=f"States Where Low Vote-Share Parties Won Constituencies ({year})",
                text='num_constituencies'
            )
            fig_state.update_layout(
                xaxis_title="State",
                yaxis_title="Constituencies Won",
                xaxis_tickangle=-45
            )
            safe_plotly_display(fig_state)
        else:
            st.info(f"No low-share party winners found in {year}.")

        # -------------------------------------------------
        # 📊 Visualization 2: Breakdown by Party (optional)
        # -------------------------------------------------
        wins_by_party = result.groupby('party').size().reset_index(name='num_constituencies')
        if not wins_by_party.empty:
            fig_party = px.bar(
                wins_by_party.sort_values('num_constituencies', ascending=False),
                x='party',
                y='num_constituencies',
                title=f"Low Vote-Share Parties That Still Won Constituencies ({year})",
                text='num_constituencies',
                color='party'
            )
            fig_party.update_layout(xaxis_title="Party", yaxis_title="Constituencies Won")
            safe_plotly_display(fig_party)

# ---------------------------------------------------------
# 17. NOTA Votes by State and Constituency
# ---------------------------------------------------------
elif selection ==  "17. NOTA Votes by State and Constituency":
    st.header("🗳️ NOTA Votes Distribution (State & Constituency)")
    nota_state = df_all[df_all['party'] == 'NOTA'].groupby(['state_name','year'])['total_votes'].sum().reset_index()
    fig = px.bar(nota_state, x='state_name', y='total_votes', color='year', barmode='group', title='NOTA Votes by State')
    safe_plotly_display(fig)

    st.subheader("Top Constituencies with Highest NOTA Votes (Both Years)")
    nota_const = df_all[df_all['party'] == 'NOTA'].groupby(['pc_name','year'])['total_votes'].sum().reset_index()
    nota_pivot = nota_const.pivot(index='pc_name', columns='year', values='total_votes').fillna(0)
    nota_pivot['total'] = nota_pivot.sum(axis=1)
    st.dataframe(nota_pivot.sort_values('total', ascending=False).head(20).reset_index())

# ---------------------------------------------------------
# 18. Parties Gaining Most Constituencies
# ---------------------------------------------------------
elif selection ==  "18. Parties Gaining Most new Constituencies in 2019 compared to 2014":
    st.header("📈 Parties Gaining Most New Constituencies in 2019")
    w14 = df_2014.loc[df_2014.groupby('pc_name')['total_votes'].idxmax()][['pc_name','party']].rename(columns={'party':'party_2014'})
    w19 = df_2019.loc[df_2019.groupby('pc_name')['total_votes'].idxmax()][['pc_name','party']].rename(columns={'party':'party_2019'})
    merged = w19.merge(w14, on='pc_name')
    changed = merged[merged['party_2019'] != merged['party_2014']]
    gains = changed.groupby('party_2019').size().reset_index(name='gains').sort_values('gains', ascending=False)
    st.dataframe(gains)
    fig = px.bar(gains, x='party_2019', y='gains', title='Parties Winning New Constituencies in 2019 vs 2014')
    safe_plotly_display(fig)

# ---------------------------------------------------------
# 19. Consistent High/Low Voter Turnout Constituencies
# ---------------------------------------------------------

elif selection == "19. Consistent High/Low Voter Turnout Constituencies in both elections":
    st.header("📌 Consistently High / Low Turnout Constituencies")

    # Compute average turnout per constituency per year
    turnout_avg = df_all.groupby(['pc_name', 'year'])['turnout'].mean().reset_index()

    # Pivot: each row = constituency, columns = years
    pivot = turnout_avg.pivot(index='pc_name', columns='year', values='turnout')
    pivot = pivot.dropna()  # remove missing years

    # Determine top and bottom 10% by turnout
    high_2014 = pivot[2014] >= pivot[2014].quantile(0.9)
    high_2019 = pivot[2019] >= pivot[2019].quantile(0.9)
    consistent_high = pivot[high_2014 & high_2019]

    low_2014 = pivot[2014] <= pivot[2014].quantile(0.1)
    low_2019 = pivot[2019] <= pivot[2019].quantile(0.1)
    consistent_low = pivot[low_2014 & low_2019]

    # Display tables
    st.subheader("🌟 Consistent High Turnout Constituencies")
    st.dataframe(consistent_high.reset_index().round(2))

    st.subheader("⚠️ Consistent Low Turnout Constituencies")
    st.dataframe(consistent_low.reset_index().round(2))

    # 📊 Scatter plot for clarity
    fig = px.bar(
        pivot.reset_index(),
        x=2014,
        y=2019,
        hover_name='pc_name',
        text='pc_name',
        title='2014 vs 2019 Turnout by Constituency',
        labels={2014: 'Turnout (2014)', 2019: 'Turnout (2019)'},
        color=(pivot[2019] - pivot[2014]),  # color shows change in turnout
        color_continuous_scale='RdBu'
    )
    safe_plotly_display(fig)

# ---------------------------------------------------------
# 20. Age Groups Contribution to Turnout Change
# ---------------------------------------------------------
elif selection == "20. Age groups contributed most to voter turnout changes between 2014 and 2019":
    st.header("📊 Which Age Groups Drove Turnout Change (2014 - 2019)")
    # Normalize column names
    df_all.columns = df_all.columns.str.lower().str.strip()

    if 'age' not in df_all.columns or 'general_votes' not in df_all.columns or 'year' not in df_all.columns:
        st.warning("❌ Missing required columns ('age', 'general_votes', 'year').")
    else:
        df_age = df_all[df_all['age'].notna()].copy()
        st.write("Valid age rows:", len(df_age))
        st.write("Unique years:", df_age['year'].unique())

        bins = [18, 25, 35, 45, 55, 65, 100]
        labels = ['18-24','25-34','35-44','45-54','55-64','65+']
        df_age['age_group'] = pd.cut(df_age['age'], bins=bins, labels=labels, right=False)

        age_turnout = df_age.groupby(['year','age_group'])['general_votes'].sum().reset_index()
        st.write("Grouped data:", age_turnout.head(), "Shape:", age_turnout.shape)

        if age_turnout.empty:
            st.warning("No grouped data available. Check 'year' and 'age' columns.")
        else:
            age_turnout_pivot = age_turnout.pivot(index='age_group', columns='year', values='general_votes').fillna(0).reset_index()
            st.write("Pivot:", age_turnout_pivot)

            age_turnout_pivot.columns = age_turnout_pivot.columns.astype(str)
            if '2014' not in age_turnout_pivot.columns: age_turnout_pivot['2014'] = 0
            if '2019' not in age_turnout_pivot.columns: age_turnout_pivot['2019'] = 0

            age_turnout_pivot['change'] = age_turnout_pivot['2019'] - age_turnout_pivot['2014']
            age_turnout_pivot['abs_change'] = age_turnout_pivot['change'].abs()
            age_turnout_pivot = age_turnout_pivot.sort_values('abs_change', ascending=False)

            st.subheader("Turnout Change by Age Group")
            st.dataframe(age_turnout_pivot[['age_group', '2014', '2019', 'change']].round(0))

            if not age_turnout_pivot.empty:
                fig = px.bar(age_turnout_pivot, x='age_group', y='change',
                             title='Change in General Votes by Age Group (2014→2019)', text='change')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No data available after processing.")

# ---------------------------------------------------------
# 21. Youth Turnout Increase vs Winning Party (Enhanced)
# ---------------------------------------------------------
elif selection == "21. Which states or constituencies saw the highest increase in youth (18-25) compare with winning party?":
    st.header("📈 Youth (18–25) Turnout Increase vs Winning Party (2014 → 2019)")

    if 'age' not in df_all.columns or 'general_votes' not in df_all.columns:
        st.warning("Required columns 'age' or 'general_votes' missing in dataset.")
    else:
        youth_votes = df_all[(df_all['age'] >= 18) & (df_all['age'] <= 25)].copy()
        youth_turnout = youth_votes.groupby(['year','state_name','pc_name'])['general_votes'].sum().reset_index(name='youth_votes')
        total_votes_pc = df_all.groupby(['year','state_name','pc_name'])['total_votes'].max().reset_index()
        youth_turnout = youth_turnout.merge(total_votes_pc, on=['year','state_name','pc_name'], how='left')
        youth_turnout['youth_turnout_pct'] = (youth_turnout['youth_votes'] / youth_turnout['total_votes']) * 100

        pivot_youth = youth_turnout.pivot(index='pc_name', columns='year', values='youth_turnout_pct').reset_index()
        pivot_youth = pivot_youth.rename(columns={2014:'turnout_2014', 2019:'turnout_2019'}).fillna(0)
        pivot_youth['youth_turnout_change'] = pivot_youth['turnout_2019'] - pivot_youth['turnout_2014']

        winners_2019_data = df_2019.loc[df_2019.groupby('pc_name')['total_votes'].idxmax(), ['pc_name','party','state_name']]
        pivot_youth = pivot_youth.merge(winners_2019_data, on='pc_name', how='left')

        top_rising = pivot_youth.sort_values('youth_turnout_change', ascending=False).head(20)
        st.subheader("Top Constituencies with Highest Youth Turnout Increase")
        st.dataframe(top_rising[['pc_name','state_name','party','turnout_2014','turnout_2019','youth_turnout_change']].round(2))

        # 🔹 Bar Chart
        fig_bar = px.bar(
            top_rising, x='pc_name', y='youth_turnout_change', color='party',
            title='Top 20 Constituencies by Youth Turnout Increase (2014→2019)',
            hover_data=['state_name','turnout_2014','turnout_2019']
        )
        safe_plotly_display(fig_bar)


# End of selections
st.sidebar.markdown("---")
st.sidebar.write("Data rows: {:,}".format(len(df_all)))
st.sidebar.write(f"Columns: {len(df_all.columns)}")
st.sidebar.write("Years in dataset: " + ", ".join(map(str, sorted(df_all['year'].unique()))))
st.sidebar.markdown("Developed by [Revanth](http://localhost:8502/) | [GitHub](https://github.com/TulabandullaRevanth/-Revanth--Provide-insights-from-Lok-Sabha-elections-data-to-a-media-company-20251004T060353Z-1-001)")
