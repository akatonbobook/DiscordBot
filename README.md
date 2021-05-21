# DiscordBot
discord.pyを使って作ったbot

## Usage

起動する前に、以下のようなトークンが書かれた*token.txt*を作成する
```
your token
```
bot.pyを起動する

```
py bot.py
```
以上。

## Bot Command
botのコマンド

### AnimalCog

動物の画像を表示

* $cat :猫の画像をランダムに表示する

* $dog :犬の画像をランダムに表示する

* $fox :キツネの画像をランダムに表示する

### CommunicationCog

ユーザーごとに決まった返答

* $add \<key> [reply] :keyの応答としてreplyを登録する。

* $remove \<key> :keyの返答を解除する

* $list :登録している返答を表示する

### RadiCog

radiko関係

* $radiko :受信できるラジオ局一覧を表示する

* $radiko \<n|station_id> :ラジオを聞く

### QuizCog

クイズ

* $quiz :クイズを出題する

### MeidaiCog

命題論理式

&(AND),-(NOT),=>,-(NOT)と()が使える

変数名は任意

* $p \<str> :strを命題論理式として真理値表を求める。

* $nff \<str> :命題論理式strを否定標準形に変換し真理値表を求める

* $cnf \<str> :命題論理式strを連言標準形に変換し真理値表を求める
