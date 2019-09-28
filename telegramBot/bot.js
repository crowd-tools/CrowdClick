require("dotenv").config();
const Telegraf = require("telegraf");
const Markup = require("telegraf/markup");
const Extra = require("telegraf/extra");
const fs = require("fs");


const TOKEN = process.env.TELEGRAM_TOKEN_API;

const bot = new Telegraf(TOKEN);

let websitesArr = ["https://docs.matic.network"]
//fetch list of websites from API

let adsQuestions = [];
let currentQuestionIndex = 0;

const fetch_questions = () => {
    adsQuestions = JSON.parse(fs.readFileSync("questions.json", "utf-8"))
    console.log(adsQuestions)
}

// const chooseWebsite = (arr) => {
//     return
// }
//move it to helper.js file

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





bot.start((ctx) => ctx.reply(`Welcome to Crowdclick, ${ctx.from.first_name}! 
`,

    Markup.inlineKeyboard([
        // [Markup.callbackButton("Visit website", "fetch_website"),
        [Markup.urlButton('Visit website', websitesArr[0])],
        [Markup.callbackButton("Show my ads", "show_ads")],
        [Markup.callbackButton("Balance", "show_balance")],
        [Markup.callbackButton("Account", "open_account")],
        [Markup.callbackButton("Answer questions", "show_questions")]

    ]).extra()
));


bot.on("callback_query", (ctx) => {
    const action = ctx.update.callback_query.data;
    switch (action) {
        case "fetch_website":
            ctx.reply("Open website etc. etc. etc.")
            console.log("it's working");
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
            ctx.reply("open the account")
            console.log("this is your account")
            break
        case "show_questions":
            // ctx.reply("here are all the questions")
            //perhaps call another action here as a callback etc. 
            // fetch_questions()
            showQuestion(ctx)

            console.log("questions consolelog")
            break
    }
})


// bot.action("", () => {

// })


bot.startPolling();