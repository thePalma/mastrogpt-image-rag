# Welcome to `mastrogpt-image-rag`

This repository contains an **Images Retrieval-Augmented Generation (RAG)** system built upon the MastroGPT starter. It is a solution to the certification exercise for the course **Developing Open LLM applications with Apache OpenServerless**.

## Project Description

This project extends the MastroGPT starter by adding an interface for uploading images and querying them through Retrieval-Augmented Generation techniques. It demonstrates how to combine image processing with LLM-based generation.

## Prerequisites

You need an up and running instance of [Apache OpenServerless](https://openserverless.apache.org) to deploy and run your code. 

You can:
-  Ask for a free development account on `openserverless.dev` courtesy of [Nuvolaris](http://nuvolaris.io). Contact us:
   - on [MastroGPT.com](https://mastrogpt.nuvolaris.dev) using our chatbot
   - on [Linkedin](https://linkedin.com/in/msciab) sending a private message 
   - on [Discord](https://bit.ly/openserverless-discord) (contact **Michele Sciabarra**)
   - on [Reddit](https://reddit.com/r/openserverless) sending a private message to [msciabarra](https://reddit.com/u/msciabarra)
  
- Self-host it [installing by yourself](https://openserverless.apache.org/docs/installation/)

## Deployment

Deploy the sample code:

- Click on OpenServerless icon then
- Click on Deploy

Deployment should complete with no errors.

## Usage Instructions

1. Upload your images using the **Images Loader** provided in the web interface.
2. Open the **Images RAG** application and follow the on-screen instructions to query your uploaded images.

## Testing

The project includes both **unit tests** and **integration tests**.

Run the tests:

- Click on the Tests Icon 
- Run all the tests

All the tests should pass.

**NOTE**: if you don't see any test, it may help to:

- open directly a test file under `tests``
- if you still dont's see the tests, reload the window