<h1><p align="center">ChatGPT LLDB Plugin</p></h1>

## Dependencies
    - lldb == 11.0.1
    - python3 == 3.9.2
    - setuptools == 68.2.0

## OS Independent Installation
  
  1. Download chatgpt-lldb-plugin.zip .
  2. Install the development package, use `cd chatgpt-lldb-plugin`, then `pip install -e .`
  3. Open `/chatgpt-plugin/api_key_config.py` and replace `YOUR_OPENAI_API_KEY` with your OpenAI API key or just enter `export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>` from terminal before lauching LLDB. Grab an API key from [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys). If you don't want to use an API key, you can run the program as well with the `browser_mode` option making use of your OpenAI account. In this case you first have to install Chrome and the corresponding Chromedriver and secondly update the `/chatgpt-plugin/browser_config.py` file. Once opened LLDB, remember you can switch among the `api_key_mode` (default) and the `browser_mode` using the `switch` command.
  4. Run `lldb`. Use the `info` command to see all the available commands. 
  5. If something during the installation went wrong you can manualli import the plugin in your LLDB session with the LLDB command: `command script import PATH/TO/chatgpt-lldb-plugin/main/commands.py`.

## Overview
Basically you can send the source code you're debugging, the visible variables and the current line with the `send` command. So before using it, make sure to have set at least a breakpoint and to have runned the program with the LLDB commands: `b LINE_CHOSEN` and `r`. You can now use `send` and afterward the `ask YOUR_REQUEST` command to ask anything you want to chatGPT. You can quit the LLDB session with `q`. Example:

    $ lldb EXECUTABLE_NAME
    (lldb) b --name main
    (lldb) r
    (lldb) send
    (lldb) ask Do you have any suggestions to improve my code?
    (lldb) next
    (lldb) send
    (lldb) ask What's the line I'm stepping on?
    (lldb) q

Use the command `autodebug` to automatically track down bugs in your code. You just have to type it and wait for ChatGPT's response.
