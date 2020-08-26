# [AnkiBot](https://t.me/Word_Cards_Bot)
Telegram bot for learning foreign words via the anki program

[![Supported Python versions](https://camo.githubusercontent.com/6f60f4f894479c0b8e48b6f373f1f4f9685be63f/68747470733a2f2f696d672e736869656c64732e696f2f707970692f707976657273696f6e732f61696f6772616d2e7376673f7374796c653d666c61742d737175617265)](/#)

* Based on `aiogram` python module
* Used `json` lib for storing user dictionaries

## How it works
Anki program utilizes spaced repetition. Spaced repetition has been shown to increase rate of memorization.<br>
There are 4 states of memorizing a word. After deck creating all words in it have 1st (lowest) state.
1. First of all create your first deck
   * Click on the «Create deck» button
   * Send a list of words. Use this format: <hr>
        Deck title <br>  word1 front side - word1 back side <br> word2 front side - word2 back side <hr>
2. Start learning words
   * Click on the «Start learning» button
   * Bot sends the list of your word deck, you can test knowledge or remind words of each deck
   * In test mode bot sends random word of chosen deck
     * Random choice of a word depends on its state: words with a low state are more likely to be selected than with a high state
     * If it's the word's front side, you can listen this word. Voice generated via [Voicerss API](http://voicerss.org)
     * If your answer is correct that word moves into the next state
       * If state of word was last then word deletes from deck
     * If your answer is wrong state doesn't change
   * In showing words mode bot sends complete list of words of chosen deck via [Telegraph API](https://telegra.ph)
3. You can also edit or delete any deck. Just choose corresponding button