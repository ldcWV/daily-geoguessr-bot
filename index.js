const dotenv = require('dotenv')
const { Client, GatewayIntentBits } = require('discord.js')
const fs = require('node:fs');

const { makePage, signinToGeoGuessr, createChallenge, createDescription, takeResultScreenshot } = require('./browser-side')

dotenv.config()

const acw = {
    url: 'https://www.geoguessr.com/maps/62a44b22040f04bd36e8a914/play',
    description: 'A Community World'
};
const challengeSettings = {
    time: 120,
    move: false,
    pan: true,
    zoom: true
};


const client = new Client({
    intents: [
        GatewayIntentBits.Guilds,
        GatewayIntentBits.GuildMessages,
        GatewayIntentBits.GuildVoiceStates,
        GatewayIntentBits.MessageContent,
    ],
});

client.login(process.env.DISCORD_TOKEN);
client.on('ready', async () => {
    let page = await makePage();
    await signinToGeoGuessr(page);
    const channel_ids = process.env.CHANNEL_ID.split(',');
    const channels = channel_ids.map(id => client.channels.cache.get(id));

    let inviteUrl = fs.readFileSync('last_chal_url.txt', 'utf8')
    if (inviteUrl !== "") {
        try {
            const screenShotFilename = await takeResultScreenshot(page, inviteUrl);
            for (const channel of channels) {
                await channel.send({
                    content: 'GGs!',
                    files: [screenShotFilename]
                });
            }
        } catch (error) {
            console.log("Could not take screenshot of results.");
            console.log("This can happen if the challenge has not been completed by the main user.")
        }
    }
    
    client.login(process.env.DISCORD_TOKEN);

    // post new challenge
    const today = `**${new Date().toLocaleDateString()} DAILY CHALLENGE**`;
    const description = createDescription(acw, challengeSettings);
    inviteUrl = await createChallenge(page, acw.url, challengeSettings);
    const message = [today, description, inviteUrl].join('\n');

    // save url
    fs.writeFileSync('last_chal_url.txt', inviteUrl);

    for (const channel of channels) {
        await channel.send(message);
    }
    await client.destroy();
    process.exit();
});
