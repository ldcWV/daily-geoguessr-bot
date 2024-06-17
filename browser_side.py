import os
os.environ['PYPPETEER_CHROMIUM_REVISION'] = '1263111'
import pyppeteer
from PIL import Image

async def sign_in_to_geoguessr(email, password):
    browser = await pyppeteer.launch({
        # "headless": True
        "headless": False
    })
    page = await browser.newPage()
    await page.setViewport({
        "width": 800,
        "height": 600
    })
    page.setDefaultNavigationTimeout(200000)
    
    sign_in_url = 'https://www.geoguessr.com/signin'
    await page.goto(sign_in_url)

    # Click accept cookies
    cookies_selector = "#accept-choices"
    # Click cookies selector if it exists
    if await page.querySelector(cookies_selector) is not None:
        await page.click(cookies_selector)

    # Type email
    email_selector = "#__next > div > div.version4_layout__XumXk.version4_noSideTray__OFtLJ > div.version4_content__ukQvy > main > div > div > form > div > div:nth-child(1) > div:nth-child(2) > input"
    await page.type(email_selector, email)

    # Type password
    password_selector = "#__next > div > div.version4_layout__XumXk.version4_noSideTray__OFtLJ > div.version4_content__ukQvy > main > div > div > form > div > div:nth-child(2) > div:nth-child(2) > input"
    await page.type(password_selector, password)

    # Click sign in
    signin_selector = "#__next > div > div.version4_layout__XumXk.version4_noSideTray__OFtLJ > div.version4_content__ukQvy > main > div > div > form > div > div.auth_forgotAndLoginButtonWrapper__8U8UF > div.form-field_formField__8jNau.form-field_typeActions__V8Omm > div > button"
    await page.click(signin_selector)
    await page.waitForNavigation()

    return page

async def take_results_screenshot(page, results_url):
    image_width, image_height = 1200, 1730
    trim_top, trim_right = 850, 1130

    await page.setViewport({
        "width": image_width,
        "height": image_height
    })
    await page.goto(results_url)

    # Take screenshot
    result_selector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div.results_table__Z7k_U"
    await page.waitForSelector(result_selector, {'timeout': 10000 })
    await page.screenshot({
        "path": "results.png"
    })

    # Trim screenshot using Pillow
    img = Image.open("results.png")
    img = img.crop((0, trim_top, trim_right, image_height))
    img.save("trimmed.png")

    return "trimmed.png"

async def create_challenge(page, map_url):
    # Go to map url
    await page.goto(map_url)

    # Choose challenge mode
    challenge_mode_selector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div:nth-child(2) > div:nth-child(2) > label"
    await page.click(challenge_mode_selector)

    # Uncheck 'default settings'
    settings_selector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div:nth-child(2) > div:nth-child(2) > label"
    if await page.querySelectorEval(settings_selector, "el => el.checked"):
        await page.click(settings_selector)

    # Set no moving
    move_selector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div.section_sectionMedium__wbXjF > div > div.game-options_optionGroup__eOMZ3 > div > div.game-options_wrappingGroup__iXw_2 > label:nth-child(1) > div.game-options_optionInput__paPBZ > input"
    await page.click(move_selector)

    # Click invite friends
    invite_selector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div.start-challenge-game_body__u5scD > div > div > button"
    await page.click(invite_selector);

    # Extract invite URL
    invite_url_selector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > section > article > div > span > input"
    await page.waitForSelector(invite_url_selector);
    invite_url = await page.querySelectorEval(invite_url_selector, "el => el.value")

    return invite_url;
