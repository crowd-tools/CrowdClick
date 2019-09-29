import {matic} from "./maticEth.js";
console.log(matic)
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
    return {website, reward, time} = publisherOj       
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

