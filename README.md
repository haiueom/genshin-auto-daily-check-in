# genshin-daily-check-in
Claim multiple account's daily reward without having to go to the website one by one.

## Features
- Claim your Hoyolab reward without opening the website using browser
- Claim multiple accounts reward

## How to use
### 1. Get cookie information
1. Connect to `hoyolab.com`.
2. Log in.
3. F12to open the developer tools.
4. 애플리케이션(Application)Go to tab, enter 쿠키(Cookies), https://www.hoyolab.comin order.
5. ltuidCopy and from that tab ltoken.
   
### 2. Set up the environment
Create new `.env` file like `.env.example`

| Key | Description | Example Value |
| ----------- | ---------------------------------------------------------------------------------------- | ----------------------------------- |
| ACCOUNT~ | Cookie information. | 13435465,AbCdEFGhIjKLmnoPQRsTUvWxYZ |
| LANGUAGE | The language information to use. Default "en-us" | en-us |
| TIME | It's time to check your attendance every day. Based on CST (UTC+8). Default "00:00"<br/>The standard time for check-in is 1:00 am Korean time. (00:00 Chinese time) | 00:00 |

### 3. Run the script
To run the script, you can easily run it using this command
```bash
python main.py
```
Or if you want to run it only once, you can use this command
```bash
python main.py -o
```