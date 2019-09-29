require("dotenv").config();
const Telegraf = require("telegraf");
const Markup = require("telegraf/markup");
const Extra = require("telegraf/extra");
const fs = require("fs");
const Wallet = require("ethereumjs-wallet");
const fetch = require("node-fetch");
const axios = require("axios");


const TOKEN = process.env.TELEGRAM_TOKEN_API;
const BASE_URL = process.env.BACK_END_API;

const bot = new Telegraf(TOKEN);

let websitesArr = ["https://docs.matic.network"]
//fetch list of websites from API

// let adsQuestions = [];
// let currentQuestionIndex = 0;

const fetch_api = async() => {
    const response = await fetch(BASE_URL);
    const data = await response.json();
    console.log(data)
    return data
}

const fetch_questions = () => {
    adsQuestions = JSON.parse(fs.readFileSync("questions.json", "utf-8"))
    console.log(adsQuestions)
}

// const chooseWebsite = (arr) => {
//     return
// }
//move it to helper.js file

const createKeyPair = (ctx) => {
    const wallet = Wallet.generate();
    let keysObj = {};
    keysObj.public_key = wallet.getAddressString();
    keysObj.private_key = wallet.getPrivateKeyString();
    // const go_to_metamask = Markup.urlButton("You can now access metamask with your private key", "https://www.myetherwallet.com/access-my-wallet")
    ctx.reply("Warning: This wallet generation method is not safe. Use it at your own risk and only for small funds. Your public key is " + keysObj.public_key + " and your private key is: " + keysObj.private_key)
}

const showQuestion = async (ctx) => {
    
    await fetch_questions();
    console.log(adsQuestions[currentQuestionIndex].question)
    ctx.reply(
        adsQuestions[currentQuestionIndex].question + "\n" 
        // Telegraf.Extra
        //     .markdown()
        //     .markup((m) => m.inlineKeyboard([
        //         m.callbackButton('Test button', 'test')
        // ]))
    );
};





bot.start(async(ctx) => {
    let arrData = await fetch_api();

    ctx.reply(`Welcome to Crowdclick, ${ctx.from.first_name}!`,
    

    Markup.inlineKeyboard([
        [Markup.callbackButton("Create wallet", "create_wallet")],
        // [Markup.callbackButton("Visit website", "fetch_website")],
        [Markup.urlButton('Visit website', arrData.results[0].website_link)],
        [Markup.callbackButton("Show my ads", "show_ads")],
        [Markup.callbackButton("Balance", "show_balance")],
        [Markup.callbackButton("Account", "open_account")],
        [Markup.callbackButton("Answer questions", "show_questions")]

    ]).extra()
)});


bot.on("callback_query", async(ctx) => {
    let action = ctx.update.callback_query.data;
    switch (action) {
        case "create_wallet":
            createKeyPair(ctx) 
            break           
        case "fetch_website":
            ctx.reply("Open website etc. etc. etc.")
            // const arrWeb = await fetch_api();
            // const website = arrWeb.results[0].website_link;
            // console.log(website)
            // console.log("it's working");
        //     const popup = 
        //         Markup.urlButton('visit the website', website);
          
        //    ctx.reply(Extra.markup(popup))

            break
        case "show_ads":
            ctx.reply("show ads etc. etc.");
            console.log("it is showing the ads")
            break
        case "show_balance":
            ctx.reply("show the balance / crypto earned")
            console.log("this is your crypto balance, consolelog")
            break
        case "open_account":
            fetch_api()
            const arr = await fetch_api();
            console.log("second console.log", arr.results[0].questions)
            console.log("THIS IS ARR", arr)
            
            ctx.reply("open the account")
            console.log("this is your account")
            break
        case "show_questions":
            let adsQuestions = [];                       

          
            // showQuestion(ctx)
            console.log("questions consolelog")
            break
    }
})





bot.startPolling();