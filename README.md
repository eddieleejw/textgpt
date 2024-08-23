# TextGPT
Leverage OpenAI ChatGPT to perform RAG over a collection of documents

# Installation

1. Install [Docker](https://www.docker.com/) 
    - Confirm docker installation by opening terminal and typing `docker -v`. It should tell you your docker version
2. Open terminal and navigate to the directory you want to put the repo in
3. Make sure Docker is running
4. In the terminal type:
```
git clone https://github.com/eddieleejw/textgpt.git
cd textgpt
docker build -t textgpt-image .
```

Building the image may take a few minutes.



# Usage

## Launch

1. Open terminal and type `docker run -p 8501:8501 textgpt-image`
2. In a web browser, type into the address bar: `http://localhost:8501` (not `http://0.0.0.0:8501`)


## OpenAI API Key

You will need a valid OpenAI API key to use this chatbot

1. Sign up for an [OpenAI account](https://openai.com/index/openai-api/)

2. Navigate to the [API keys page](https://platform.openai.com/api-keys)

3. Select "+ Create new secret key", give it a name, and select "Create secret key"

The chatbot will ask you for your OpenAI API key on launch in order to access the OpenAI language models.

![api](images/openapi.png)


## Building a database

1. Select the "Build" option from the drop down menu on the left side of the page

2. Drag and drop file(s) that you want to use to create the initial database

3. Give the project a name

4. Press "Go!"

![build](images/build.png)

## Updating a database

1. Select the "Update" option from the drop down menu on the left side of the page

2. Drag and drop file(s) that you want to use to update the initial database

3. Select an existing project from the drop down menu
    - Press "Rescan projects" if your project is not showing up in the dropdown menu

4. Press "Go!"

![update](images/update.png)

## Finetuning a model

1. Select the "Finetune" option from the drop down menu on the left side of the page

2. Upload a training file (required) and a validation file (optional) for finetuning
    - See [here](https://platform.openai.com/docs/guides/fine-tuning/preparing-your-dataset) for details on how to properly format your data

3. Select a base model from the drop down menu

4. Press "Go!"

5. Check the status of the finetuning in your [OpenAPI dashboard](https://platform.openai.com/finetune)

![update](images/finetune.png)

## Evaluating a database

1. Select the "Evaluate" option from the drop down menu on the left side of the page

2. Select an existing project from the drop down menu
    - Press "Rescan projects" if your project is not showing up in the dropdown menu

3. Drag and drop file(s) that you want to use to evaluate the database

4. Set the number of evaluation data points to use
    - Higher values will use more of the provided files and provide more accurate evaluations, but will take longer and use more API calls
    - Lower values will use less of the provided files and provide less accurate evaluations, but will take less time and use less API calls

5. Press "Go!"

![eval](images/evaluate.png)


## Chatting with chatbot

1. Select the "Chat" option from the drop down menu on the left side of the page

2. Select the project/database you want to chat about

3. Enter your query in the chatbot

4. Click the "See sources" drop down to see the documents referred to by the chatbot

![chat](images/chat.png)


## Reusing a database

Running `docker run -p 8501:8501 textgpt-image` every time will create new containers. To reuse the database(s) that you built before:

1. Open to Docker desktop app

2. Find the container in which you built the database

3. Launch the container using the "Start" button

![docker-reuse](images/docker_reuse.png)

# Troubleshooting

## Windows installation

Ensure that you have [Microsoft Visual C++ 14.0](https://visualstudio.microsoft.com/visual-cpp-build-tools/) or greater installed

![vs_install](images/windows_vs_install.png)