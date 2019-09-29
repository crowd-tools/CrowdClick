// import { matic } from "./maticEth.js";
// console.log(matic)
console.log("main.js here hello")




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
        // window.web3 = new Web3(web3.currentProvider);
        // the above was working
        window.web3 = new Web3(injectedWeb3.currentProvider);
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