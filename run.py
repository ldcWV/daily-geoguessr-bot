import modal
from daily_challenge import run_daily_challenge

app = modal.App()

image = (
    modal.Image.debian_slim()
    .apt_install("ca-certificates")
    .apt_install("fonts-liberation")
    .apt_install("libasound2")
    .apt_install("libatk-bridge2.0-0")
    .apt_install("libatk1.0-0")
    .apt_install("libc6")
    .apt_install("libcairo2")
    .apt_install("libcups2")
    .apt_install("libdbus-1-3")
    .apt_install("libexpat1")
    .apt_install("libfontconfig1")
    .apt_install("libgbm1")
    .apt_install("libgcc1")
    .apt_install("libglib2.0-0")
    .apt_install("libgtk-3-0")
    .apt_install("libnspr4")
    .apt_install("libnss3")
    .apt_install("libpango-1.0-0")
    .apt_install("libpangocairo-1.0-0")
    .apt_install("libstdc++6")
    .apt_install("libx11-6")
    .apt_install("libx11-xcb1")
    .apt_install("libxcb1")
    .apt_install("libxcomposite1")
    .apt_install("libxcursor1")
    .apt_install("libxdamage1")
    .apt_install("libxext6")
    .apt_install("libxfixes3")
    .apt_install("libxi6")
    .apt_install("libxrandr2")
    .apt_install("libxrender1")
    .apt_install("libxss1")
    .apt_install("libxtst6")
    .apt_install("lsb-release")
    .apt_install("wget")
    .apt_install("xdg-utils")
    .pip_install("pyppeteer")
    .pip_install("discord-py-api")
    .pip_install("pillow")
)

@app.function(schedule=modal.Cron("0 1 * * *"), image=image)
def run():
    run_daily_challenge()