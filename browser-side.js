const sharp = require('sharp');
const puppeteer = require('puppeteer');

const resultFilename = 'result.png';

const makePage = async () => {
    const browser = await puppeteer.launch({
        headless: 'new',
        // headless: false,
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 800, height: 600 });
    page.setDefaultNavigationTimeout(200000);

    return page;
};

const signinToGeoGuessr = async (page) => {
    // sign in
    const signinUrl = 'https://www.geoguessr.com/signin';
    await page.goto(signinUrl);

    // accept cookies
    const acceptCookieSelector = '#accept-choices';
    if (await page.$(acceptCookieSelector) !== null) {
        await page.click(acceptCookieSelector);
    }

    const emailSelector = "#__next > div > div.version4_layout__XumXk.version4_noSideTray__OFtLJ > div.version4_content__ukQvy > main > div > div > form > div > div:nth-child(1) > div:nth-child(2) > input"
    await page.type(emailSelector, process.env.EMAIL);

    const passwordSelector = "#__next > div > div.version4_layout__XumXk.version4_noSideTray__OFtLJ > div.version4_content__ukQvy > main > div > div > form > div > div:nth-child(2) > div:nth-child(2) > input"
    await page.type(passwordSelector, process.env.PASSWORD);

    const signinButtonSelector = "#__next > div > div.version4_layout__XumXk.version4_noSideTray__OFtLJ > div.version4_content__ukQvy > main > div > div > form > div > div.auth_forgotAndLoginButtonWrapper__8U8UF > div.form-field_formField__8jNau.form-field_typeActions__V8Omm > div > button"
    await page.click(signinButtonSelector);
    await page.waitForNavigation();
};

const takeResultScreenshot = async (page, chalUrl) => {
    const imageWidth = 1200, imageHeight = 1730;
    const trimTop = 850, trimRight = 1130;

    await page.setViewport({ width: imageWidth, height: imageHeight });
    const resultUrl = chalUrl.replace('challenge', 'results');
    await page.goto(resultUrl);

    // take screenshot
    const resultSelector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div.results_table__Z7k_U"
    await page.waitForSelector(resultSelector);
    await page.screenshot({ path: resultFilename });

    // trim screenshot
    const trimmedFilename = 'trimmed.png';
    await sharp(resultFilename)
        .extract({ left: 0, top: trimTop, width: trimRight, height: imageHeight - trimTop })
        .toFile(trimmedFilename);

    return trimmedFilename;
};

const createChallenge = async (page, mapUrl, chalSettings) => {
    // go to map
    await page.goto(mapUrl);

    // select 'Challenge' mode
    const chalModeSelector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div:nth-child(2) > div:nth-child(2) > label"
    await page.click(chalModeSelector);

    // uncheck 'Default settings'
    const settingsSelector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div.section_sectionMedium__wbXjF > div > div > div:nth-child(2) > input"
    const settingsIsChecked = await page.$eval(settingsSelector, el => el.checked);
    if (settingsIsChecked) {
        await page.click(settingsSelector);
    }

    // set time (TODO: fix this)
    // console.log("setting time")
    // const timeSelector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div.section_sectionMedium__wbXjF > div > div.game-options_optionGroup__eOMZ3 > div > div:nth-child(1) > div > label > div.game-options_optionInput__paPBZ > div > div > div.styles_handle__h9ytQ"
    // await page.waitForSelector(timeSelector);
    // const timeSlider = await page.$(timeSelector);
    // await page.evaluate((slider, value) => {
    //     slider.ariaValueNow = String(value);
    // }, timeSlider, chalSettings.time);

    // set move, pan, and zoom
    const moveSelector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div.section_sectionMedium__wbXjF > div > div.game-options_optionGroup__eOMZ3 > div > div.game-options_wrappingGroup__iXw_2 > label:nth-child(1) > div.game-options_optionInput__paPBZ > input"
    const moveIsChecked = await page.$eval(moveSelector, el => el.checked);
    if (moveIsChecked !== chalSettings.move) {
        await page.click(moveSelector);
    }

    const panSelector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div.section_sectionMedium__wbXjF > div > div.game-options_optionGroup__eOMZ3 > div > div.game-options_wrappingGroup__iXw_2 > label:nth-child(2) > div.game-options_optionInput__paPBZ > input"
    const panIsChecked = await page.$eval(panSelector, el => el.checked);
    if (panIsChecked !== chalSettings.pan) {
        await page.click(panSelector);
    }

    const zoomSelector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div.section_sectionMedium__wbXjF > div > div.game-options_optionGroup__eOMZ3 > div > div.game-options_wrappingGroup__iXw_2 > label:nth-child(3) > div.game-options_optionInput__paPBZ > input"
    const zoomIsChecked = await page.$eval(zoomSelector, el => el.checked);
    if (zoomIsChecked !== chalSettings.zoom) {
        await page.click(zoomSelector);
    }

    // invite friends
    const inviteSelector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > div.start-challenge-game_body__u5scD > div > div > button"
    await page.click(inviteSelector);

    // copy invite URL
    const inviteUrlSelector = "#__next > div.background_wrapper__BE727.background_backgroundClassic__Sjpbl > div.version4_layout__XumXk > div.version4_content__ukQvy > main > div > div > div > div > section > article > div > span > input"
    await page.waitForSelector(inviteUrlSelector);
    const inviteUrl = await page.$eval(inviteUrlSelector, el => el.value);

    return inviteUrl;
};

const createDescription = (map, chalSettings) => {
    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins > 0 ? mins + " min" : ""}${secs > 0 ? " " + secs + " s" : ""}`;
    };
    const falseKeysString = (obj) => {
        const falseKeys = Object.entries(obj)
            .filter(([_, value]) => value === false)
            .map(([key, _]) => key);
        const res = falseKeys.map((key) => `no ${key}`).join(', ');
        return res === '' ? 'with move' : res;
    };
    return `${map.description}, ${formatTime(chalSettings.time)} per round, ${falseKeysString(chalSettings)}`;
};

module.exports = {
    makePage,
    signinToGeoGuessr,
    takeResultScreenshot,
    createChallenge,
    createDescription
};
