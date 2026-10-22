# Japanese-Ads-Filter

![Build Status](https://github.com/aatmnt21-collab/Japanese-Ads-Filter/actions/workflows/build.yml/badge.svg)
![License](https://img.shields.io/github/license/aatmnt21-collab/Japanese-Ads-Filter)
![Last Commit](https://img.shields.io/github/last-commit/aatmnt21-collab/Japanese-Ads-Filter)

LINE & Yahoo! JAPAN エコシステムに特化した、**高精度DNS広告ブロックフィルター**です。

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

---

## 📜 ライセンス
[MIT License](LICENSE) - 誰でも自由にご利用・ご再配布いただけます。
