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
    const channel_ids = process.env.CHANNEL_ID.split(',');
    const channels = channel_ids.map(id => client.channels.cache.get(id));
    let inviteUrl = process.env.LAST_CHAL_URL;

    cron.schedule(process.env.POST_TIME, async () => {
        client.login(process.env.DISCORD_TOKEN);

        // post challenge result
        if (inviteUrl !== "") {
            const screenShotFilename = await takeResultScreenshot(page, inviteUrl);
            for (const channel of channels) {
                await channel.send({ content: 'GGs!', files: [screenShotFilename] });
            }
        }

        // post new challenge
        const today = `${new Date().toLocaleDateString()} daily challenge`;
        const description = createDescription(acw, challengeSettings);
        inviteUrl = await createChallenge(page, acw.url, challengeSettings);
        const message = [today, description, inviteUrl].join('\n');
        console.log(inviteUrl);

        for (const channel of channels) {
            await channel.send(message);
        }
        await client.destroy();
    });
});
