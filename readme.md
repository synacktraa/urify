# Urify 🫧

Gone are the days of tedious manual operations; Urify is here to dissect, streamline, and nearly whip up a sandwich for you.

> Urify is heavily inspired by [tomnomnom/unfurl](https://github.com/tomnomnom/unfurl).
---

### 🚀 Installation:
```
pip install urify
```

---

### 🛠 Commands:

Oh, you thought this was just a basic tool? Think again!

#### 🔍 Basic URL Dissections:

- `keys`: Want to know what keys are in your query string? I got you!
- `values`: Retrieve values from the query string. Yes, like treasure hunting but more nerdy.
- `params`: Get those key=value pairs, one at a time, like peeling an onion.
- `apex`: Get the apex domain. It's like climbing a mountain, but lazier.
- `fqdn`: Retrieve the fully qualified domain name. Fancy words, right?
- `json`: Encode your dissected URL into JSON. Because... JSON!

#### 🎛 Advanced Filtering:

- `filter`: Refine your URLs using a myriad of component filters:

  - `-scheme`: Filter by request schemes. Yes, we're getting technical here.
  - `-sub`: Look for specific subdomains. It's like Where's Waldo but for domains.
  - `-domain`: Specify domains. Because we all have favorites.
  - `-tld`: Filter by top-level domains. It's all about the hierarchy.
  - `-ext`: Filter by file extensions. The grand finale of URLs.
  - `-port`: Specify ports. No, not the wine. The number.
  - `-apex`: Get URLs by apex domain. It's like VIP access.
  - `-fqdn`: Filter by fully qualified domain names. The whole shebang!
  - `-inverse`: Want to be rebellious? Use filters as a deny-list.
  - `-absolute`: Validate all filters. No half measures here!
  - `-dissect`: Once filtered, dissect the URL for a specific component. Pick and choose!

---

### 📖 Examples:

#### 1. Basic URL Dissections:

```
$ urify -help
Dissect and filter URLs provided on stdin.

Usage: main.py [-help] [mode] ...

Options:
  -help     show this help message

Modes:
    keys    Retrieve keys from the query string, one per line.
    values  Retrieve values from the query string, one per line.
    params  Key=value pairs from the query string (one per line)
    path    Retrieve the path (e.g., /users/me).
    apex    Retrieve the apex domain (e.g., github.com).
    fqdn    Retrieve the fully qualified domain name (e.g., api.github.com).
    json    JSON encode the dissected URL object.
    filter  Refine URLs using component filters.
```

- **keys**:
  ```
  $ cat urls.txt | urify keys
  search
  id
  product-id
  name
  ```

- **values**:
  ```
  $ cat urls.txt | urify values
  query
  123
  29
  powder
  ```

- **params**:
  ```
  $ cat urls.txt | urify params
  search=query
  id=123
  product-id=29
  name=powder
  ```

- **apex**:
  ```
  $ cat urls.txt | urify apex
  example.com
  spaghetti.com
  example.org
  cartel.net
  ```

- **fqdn**:
  ```
  $ cat urls.txt | urify fqdn
  sub.example.com
  mom.spaghetti.com
  blog.example.org
  shop.cartel.net
  ```

- **json**:
  ```
  echo "http://bob:secret@sub.example.com:80/file%20name.pdf?page=10" | urify json
  ```

  ```  
  {
    "scheme": "http",
    "username": "bob",
    "password": "secret",
    "subdomain": "sub",
    "domain": "example",
    "tld": "com",
    "port": "80",
    "path": "/file%20name.pdf",
    "raw_query": "page=10",
    "query": [
      {
        "key": "page",
        "value": "10"
      }
    ],
    "fragment": "",
    "apex": "example.com",
    "fqdn": "sub.example.com"
  }
  ```

#### 2. Advanced Filtering:

```
$ urify filter -help

Refine URLs using component filters.
By default, the command treats provided filters as an allow-list,
evaluating just one parameter from a specified field.

To assess all components, add the `-absolute` flag.
For a deny-list approach, incorporate the `-inverse` flag.
After evaluation, the default result is the URL.
For specific URL dissected object, pair the `-dissect` option with any one of:
`keys` | `values` | `params` | `apex` | `fqdn` | `json`

Usage: main.py filter [-help] [-scheme SCHEME [...]] [-sub SUB [...]] [-domain DOMAIN [...]] [-tld TLD [...]] [-ext EXT [...]]     
                      [-port PORT [...]] [-apex APEX [...]] [-fqdn FQDN [...]] [-inverse] [-absolute] [-dissect MODE]

Options:
  -help                 show this help message
  -scheme SCHEME [...]  The request schemes (e.g. http, https)
  -sub SUB [...]        The subdomains (e.g. abc, abc.xyz)
  -domain DOMAIN [...]  The domains (e.g. github, youtube)
  -tld TLD [...]        The top level domains (e.g. in, com)
  -ext EXT [...]        The file extensions (e.g. pdf, html)
  -port PORT [...]      The ports (e.g. 22, 8080)
  -apex APEX [...]      The apex domains (e.g. github.com, youtube.com)
  -fqdn FQDN [...]      The fully qualified domain names (e.g. api.github.com, app.example.com)
  -inverse              Process filters as deny-list
  -absolute             Validate all filter checks
  -dissect MODE         Dissect url and retrieve mode after filtering

Modes:
  keys|values|params|path|apex|fqdn|json
```

- **filter by scheme**:
  ```
  $ cat urls.txt | urify filter -scheme https
  https://sub.example.com/literally%20me.jpg#top
  ```

- **filter by domain**:
  ```
  $ cat urls.txt | urify filter -domain example
  https://sub.example.com/literally%20me.jpg#top
  http://blog.example.org:8443/new%20blog?id=123
  ```

- **filter and dissect**:
  ```
  $ cat urls.txt | urify filter -ext pdf jpg -dissect apex
  example.com
  spaghetti.com
  ```


- **filters as deny-list**:
  ```
  $ cat urls.txt | urify filter -ext html -inverse
  https://sub.example.com/literally%20me.jpg#top
  http://mom.spaghetti.com:8080/cookbook.pdf?search=query
  http://blog.example.org:8443/new%20blog?id=123
  ```

- **validate all filters**:
  ```
  $ cat urls.txt | urify filter -tld com -port 8080 -absolute
  http://mom.spaghetti.com:8080/cookbook.pdf?search=query
  ```

---

### 📝 Notes:

- By default, the `filter` command treats the provided filters as an allow-list. But if you're feeling a little naughty, use the `-inverse` flag for a deny-list approach.
- If you're the meticulous type and want to validate every single filter parameter, add the `-absolute` flag to your command. No stone unturned!
- After all the filtering shenanigans, if you just want the URL, we'll give it to you. But if you're in the mood for something special, pair the `-dissect` option with any one of the listed choices.

---

## 🧠 Custom CLI Parser (Skip this part):

Ever felt that built-in command-line parsers are just... meh? I did too. That's why urify is powered by its very own custom CLI parser. Why settle for the ordinary when you can have the extraordinary? 

### 🧐 Features:

- **Read from Standard Input**: Yes, the good ol' stdin. And if you're feeling picky, verify if the input has been piped with `verify_tty`.
- **Command-centric**: Create commands as easily as adding a decorator with `@cli.command(...)`. Seriously, it's like sprinkling magic dust on your functions.
- **Options Galore**: Add options to your commands using the `@cli.option(...)` decorator. Define data types, set multiple values, and even specify valid choices. It's like an all-you-can-eat buffet, but for command-line arguments.

### 📖 Behind the Scenes:

#### Command Class:

The `Command` class encapsulates each command. It's like a VIP pass for your functions:

- `name`: The unique identifier for your command.
- `callback`: The function to be invoked when the command is called.
- `parser`: The argument parser associated with this command. 

#### CLI Class:

The heart and soul of the custom parser. The `Cli` class:

- **Initialization**: Set up your CLI with descriptions, help flags, and more. Feel like a movie director but for commands.
- **Command Registration**: Register functions as commands with the `@cli.command(...)` decorator. It's like enlisting soldiers for battle.
- **Option Handling**: Define options with the `@cli.option(...)` decorator. Like adding extra toppings to your pizza.
- **Execution**: Finally, the `cli.run()` method brings everything together by parsing the arguments and invoking the right command. Lights, camera, action!

### 🤓 Technical Deep Dive:

The magic happens with the use of the `_ArgumentParser` class (a modified version of `argparse.ArgumentParser`). This allows for a more intuitive and concise definition of command-line interfaces. The beauty of this parser is that it draws inspiration from renowned libraries like `click` and `typer` while maintaining the unique aspects of `argparse`.

The `read_stdin` function is a handy tool to read values directly from standard input. If you've ever been in a situation where you'd like to exit if no input has been piped, the `verify_tty` parameter has got your back.

Overall, this custom CLI parser provides a seamless and powerful way to interact with command-line tools without the usual hassles.

---

### ToDo

- Integrate unique URL printing to filter similar urls.

*Disclaimer: No URLs were harmed in the making of this tool.*

---

Happy dissecting! 🎈