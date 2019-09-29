// import { matic } from "./maticEth.js";
// console.log(matic)
console.log("main.js here hello")


const inputPublDataWebsite = document.getElementById("publisher-data-website");
const inputPublDataReward = document.getElementById("publisher-data-reward");
const inputPublDataTime = document.getElementById("publisher-data-time");
const forwardPublDataBtn = document.getElementById("forward-publisher");
const inputPublDataQuiz = document.getElementById("publisher-data-quiz");
const forwardQuizBtn = document.getElementById("forward-quiz");
const addQuestionBtn = document.getElementById("add-question");

let quizArr = []


// console.log(inputPublDataQuiz.value)
// console.log(inputPublDataReward.value)
// console.log(inputPublDataTime.value)

const addQuestionData = () => {
    quizArr = [...quizArr, inputPublDataQuiz.value];
    inputPublDataQuiz.value = "";
    // inputPublDataQuiz.placeholder = "Receive a user feedback with your own customized quiz";

    // console.log(quizArr)
}

const forwardPublData = () => {
    let publisherOj = {}
    publisherOj.website = inputPublDataWebsite.value;
    publisherOj.reward = inputPublDataReward.value;
    publisherOj.time = inputPublDataTime.value;
    inputPublDataWebsite.value = "";
    inputPublDataReward.value = "";
    inputPublDataTime.value = "";
    return { website, reward, time } = publisherOj
}

const forwardQuiz = () => {
    console.log("quizarr", quizArr)
    return quizArr
}

forwardPublDataBtn.addEventListener("click", () => {
    console.log(forwardPublData())
    return forwardPublData()
})

addQuestionBtn.addEventListener("click", () => {
    console.log("array has been updated")
    addQuestionData()
    // console.log(quizArr)
})

forwardQuizBtn.addEventListener("click", () => {
    forwardQuiz()
})

// const loginBtn = document.getElementById("login-button");

// loginBtn.addEventListener('click', async () => {
//     console.log("test")
//     if (window.ethereum) {
//         console.log("windowethereum")
//         console.log(window.web3)
//         console.log("func", new Web3(ethereum))
//         window.web3 = new Web3(ethereum);
//         try {
//             await ethereum.enable();
//             console.log("ethereum enable")
//         } catch (error) {

//             console.log(error)
//         }
//     }
//     else if (window.web3) {
//         window.web3 = new Web3(web3.currentProvider);
//         console.log("web3")
//     }
//     else {
//         console.log("wrong")
//         alert('Please install metamask');
//     }
// });


const loginBtn = document.getElementById("login-button");
loginBtn.addEventListener('click', async () => {
    let account;
    console.log("test")
    // Modern metamask
    if (window.ethereum) {
        // console.log("windowethereum")
        // console.log(window.web3)
        // console.log("func", new Web3(ethereum))
        window.web3 = new Web3(ethereum);
        try {
            console.log("it is working, ethereum almost await")
            await window.ethereum.enable();    // popup
        

            // await window.web3.eth.getAccounts().then(accounts => {
            //     console.log("ACCOUNTS HERE", accounts)
            //     account = accounts[0];
            // })
        } catch (error) {
            console.log(error)
        }
    }
    // Legacy dapp browers (mist)
    else if (window.web3) {
        window.web3 = new Web3(web3.currentProvider);
        new Web3(injectedWeb3.currentProvider);
        // window.web3 = new Web3(injectedWeb3.currentProvider);
        // console.log("checking the account")
        // console.log(window.web3)
        // console.log("account here", window.web3.eth.accounts[0])
        // console.log(window.web3.eth.getAccounts(console.log()))
        // console.log("web3")
    }
    // No web3, go install it
    else {
        console.log("wrong")
        alert('Please install metamask');
    }

    console.log("ethereum enable")
    console.log(window.web3)
    let accounts = await window.web3.eth.getAccounts(console.log);
    console.log(window.web3.eth.getAccounts(console.log))
    console.log(accounts);

    // if(window.web3 !== "undefined") {
    //     new Web3(injectedWeb3.currentProvider);
    //     console.log("checking the account")
    //     console.log(window.web3)
    //     console.log(window.web3.eth.accounts[0])
    //     console.log(window.web3.eth.getAccounts(console.log()))
    //     try {
    //         await window.web3.eth.getAccounts().then(accounts => {
    //             account = accounts[0];
    //         });        

    //     }
    //     catch(error) {
    //         console.log(error)
    //     }
    // }
    console.log(account)
});



// console.log(web3.eth.accounts)


// const iframeEl = document.getElementById("ads");
// console.log("iframeel", iframeEl)

// let startDate;
// let elapsedTime = 0;

// const focus = function () {
//     startDate = new Date();
// };

// const blur = function () {
//     const endDate = new Date();
//     const spentTime = endDate.getTime() - startDate.getTime();
//     elapsedTime += spentTime;
// };

// const beforeunload = function () {
//     const endDate = new Date();
//     const spentTime = endDate.getTime() - startDate.getTime();
//     elapsedTime += spentTime;


// };

// console.log(elapsedTime)

// iframeEl.addEventListener('focus', focus);
// iframeEl.addEventListener('blur', blur);
// iframeEl.addEventListener('beforeunload', beforeunload);

// console.log(document.getElementById("hello"))