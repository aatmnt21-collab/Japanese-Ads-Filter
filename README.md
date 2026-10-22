# Japanese-Ads-Filter（日本特化フィルター)

![Build Status](https://github.com/aatmnt21-collab/Japanese-Ads-Filter/actions/workflows/build.yml/badge.svg)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Last Commit](https://img.shields.io/github/last-commit/aatmnt21-collab/Japanese-Ads-Filter)

LINE & Yahoo! JAPAN エコシステムに特化した、**高精度DNS広告ブロックフィルター**です。ヤフージャパンなどの大手のみをブロックするためめちゃくちゃ軽量です。汎用なdns公式リストと併用することをお勧めします。

メッセージ送受信、写真・動画表示（`vos`）、LINE Pay/PayPay、通話などのコア機能や、Googleシステム・各種決済アプリとの通信を100%保護しながら、トーク画面上部やニュース枠の広告・トラッキング通信のみをピンポイントでブロックします。

---

## 🚀 登録URL (NextDNS / AdGuard 対応)

お使いのDNSブロッカーやアプリの「外部フィルター追加（URL指定）」欄に以下のURLを登録してください。

https://raw.githubusercontent.com/aatmnt21-collab/Japanese-Ads-Filter/main/filter.txt

---

## 🛡️ 設計思想 & 自動クレンジング機能（OISD準拠）

1. **主要機能の快適さ第一（コア機能の保護）**
   LINEのメッセージ送信、通話、画像キャッシュ、スタンプショップ、LINE Pay/PayPayなどの決済・認証通信を絶対ブロック対象外として定義しています。ただし、通信量を減らすためラインニュースやラインのサブ機能は対象です。
2. **自動クレンジング & 重複・Dead Domain自動除外**
   URLのコピペミス（`https://` やパス等）の自動修復、ドメインの重複排除、および現在DNS解決できない「使われていない/存在しないドメイン（Dead Domain）」をビルド時に自動で除外します。
3. **通信ループ・バッテリードレインの防止**
   アプリが通信拒否に対して無限リトライを起こさないドメインのみを厳選・検証しています。
4. **2026年10月 LINEヤフー統合対応**
   システム統合に伴う新広告ドメインの出現や移行に順次追従していきます。

---

## 🤝 コミュニティ協力のお願い（Issue・ログ共有）

LINEアプリのアップデートやLINEヤフーの仕様変更により、**「新しい広告が出てきた」「特定の機能が動かなくなった」**といった現象が発生した場合は、ぜひ情報をお寄せください！他にもブロックしたい機能あったら教えてください。

### ☆協力方法
1. NextDNSやAdGuardの**「リアルタイムログ」**を開きます。
2. LINE起動時や問題発生時に流れるドメイン（`*.line-scdn.net` や `*.ly...` など）を確認・スクショします。
3. このリポジトリの **[Issues](https://github.com/aatmnt21-collab/Japanese-Ads-Filter/issues)** タブから報告フォームに従ってご報告ください。

# Security & Safety Policy

## 🛡️ Zero-Breakage & Core Function Protection Policy

`Japanese-Ads-Filter` は、LINEおよびYahoo! JAPANのコア機能（メッセージ送信、音声・ビデオ通話、画像・動画キャッシュ表示、決済機能等）を**100%誤ブロックしないこと**を最優先原則として設計されています。

---

## 🎯 ドメイン追加・提案における「3大絶対条件」

当プロジェクトにおいて、新しいドメインの提案・追加・承認を行う際は、以下の3条件をすべて満たすことを必須としています。

1. **【対象の厳格限定】LINEヤフーアプリ・サービスの通信であること**
   - LINEおよびYahoo! JAPAN関連アプリ（Yahoo! JAPAN, Yahoo!ニュース, Yahoo!ショッピング, Yahoo!天気等）内で実際に発生している通信のみを対象とします。
   - 一般のWebサイトや他社アプリ（Google, X, Amazon等）でしか使われない汎用ドメインは一切排除します。

2. **【サードパーティ広告・トラッカーの限定選定】**
   - LINEヤフーアプリ内で読み込まれている、安全性が確認されたサードパーティ（外部）の広告・アクセス解析・トラッキング通信（AppLovin, Adjust, Facebook Pixel等）のみをブロック対象とします。

3. **【100% Zero-Breakage（機能不全ゼロ）の保証】**
   - 以下のコア機能に少しでも影響を与える可能性があるドメインは、絶対に追加せずホワイトリストへ送ります。
     - **LINEコア通信:** メッセージ送信、音声・ビデオ通話、画像・動画（`vos`）、スタンプ購入、プロフィール更新
     - **決済・認証:** PayPay、LINE Pay、Yahoo! IDログイン（SSO）、SMS/2段階認証
     - **アプリ内コンテンツ:** ニュース記事本文、天気予報データ、ショッピングの購入手続き画面

---

## 🐛 不具合・誤ブロックの報告

誤ブロック（正常な機能の破損）を発見した場合は、直ちに [GitHub Issues](https://github.com/aatmnt21-collab/Japanese-Ads-Filter/issues) よりご報告ください。優先度「最高」として即座に対応いたします。


---

## 📜 ライセンス
[MIT License](LICENSE) - 誰でも自由にご利用・ご再配布いただけます。

