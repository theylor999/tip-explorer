
from shiny import App, render, ui, reactive
import plotly.express as px
import seaborn as sns

tips = sns.load_dataset("tips")

app_ui = ui.page_fluid(
    ui.panel_title("Tip Explorer — mtcars/tips dataset"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("day", "Day of week", ["All"] + sorted(tips["day"].unique().tolist()), selected="All"),
            ui.input_slider("total_bill", "Minimum total bill ($)", 1.0, 60.0, 1.0),
            ui.input_checkbox("smoker_only", "Smokers only", False),
            ui.markdown("Pick a day, set a minimum bill and filter smokers. The histogram and summary update automatically."),
        ),
        ui.output_plot("hist"),
        ui.output_text_verbatim("summary"),
    ),
)

def server(input, output, session):
    @reactive.calc
    def filtered():
        df = tips
        if input.day() != "All":
            df = df[df["day"] == input.day()]
        df = df[df["total_bill"] >= input.total_bill()]
        if input.smoker_only():
            df = df[df["smoker"] == "Yes"]
        return df

    @output
    @render.plot
    def hist():
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        df = filtered()
        fig, ax = plt.subplots(figsize=(9, 4.5))
        for label, sub, color in [("Non-smoker", df[df["smoker"] == "No"], "#3498db"), ("Smoker", df[df["smoker"] == "Yes"], "#e74c3c")]:
            ax.hist(sub["tip"], bins=25, alpha=0.6, label=label, color=color)
        ax.set_title("Tip distribution")
        ax.set_xlabel("Tip ($)")
        ax.set_ylabel("Count")
        ax.legend()
        return fig

    @output
    @render.text
    def summary():
        df = filtered()
        if df.empty:
            return "No rows match the filters."
        return df[["total_bill", "tip"]].describe().round(2).to_string()

app = App(app_ui, server)
