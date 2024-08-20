# TextGPT
Leverage OpenAI ChatGPT to perform RAG over a collection of documents

# Installation (Windows 11)

1. Open terminal and navigate to the directory you want to put the repo in
2. In the terminal type: `git clone https://github.com/eddieleejw/textgpt.git`
3. In the terminal type: `cd textgpt`
4. In the terminal type: `conda env create -f environment_win.yml`
5. Activate the virtual environment with `conda activate textgpt`
5. In the terminal type: `pip install requirements_win.txt`
5. In the terminal type: `streamlit run streamlit.py`
6. In a browser, type into the address bar: `http://localhost:8501`

# Installation (Mac M1)




# Usage

You will need a valid OpenAI API key to use this chatbot

### OpenAI API Key

1. Sign up for an [OpenAI account](https://openai.com/index/openai-api/)

2. Navigate to the [API keys page](https://platform.openai.com/api-keys)

3. Select "+ Create new secret key", give it a name, and select "Create secret key"

The chatbot will ask you for your OpenAI API key, in order to access the OpenAI language models. 

### Building a database

### Querying the database

1. Open streamlit with `streamlit run streamlit.py`

2. Put in your OpenAI API key

3. Select your project

4. Put in your query

5. Press `Run`

# Example

![test](images/demo.png)

# Troubleshooting

## Windows installation

Ensure that you have [Microsoft Visual C++ 14.0](https://visualstudio.microsoft.com/visual-cpp-build-tools/) or greater installed

![blah](images/windows_vs_install.png)