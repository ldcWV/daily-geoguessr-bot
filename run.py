import modal
from daily_challenge import run_daily_challenge

app = modal.App()

image = (
    modal.Image.debian_slim()
    .pip_install("discord-py-api")
    .pip_install("openai")
    .pip_install("requests")
)

@app.function(schedule=modal.Cron("0 1 * * *"), image=image)
def run():
    run_daily_challenge()
