const dotenv = require('dotenv')
const { Client, GatewayIntentBits } = require('discord.js')
const cron = require('node-cron')

const { signinToGeoGuessr, createChallenge, createDescription, takeResultScreenshot } = require('./browser-side')

dotenv.config()

const acw = {
    url: 'https://www.geoguessr.com/maps/62a44b22040f04bd36e8a914/play',
    description: 'A Community World'
};
const challengeSettings = {
    time: 60,
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
    const page = await signinToGeoGuessr();
    const channel = await client.channels.cache.get(process.env.CHANNEL_ID);
    let inviteUrl = process.env.LAST_CHAL_URL;

    cron.schedule('0 10 * * *', async () => {
        // post challenge result
        if (inviteUrl !== "") {
            const screenShotFilename = await takeResultScreenshot(page, inviteUrl);
            channel.send({ files: [screenShotFilename] })
        }

        // post new challenge
        const today = `${new Date().toLocaleDateString()} daily challenge`;
        const description = createDescription(acw, challengeSettings);
        inviteUrl = await createChallenge(page, acw.url, challengeSettings);
        const message = [today, description, inviteUrl].join('\n');
        console.log(inviteUrl);

        await channel.send(message);
        await client.destroy();
    });
});
