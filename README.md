# Mozc UT Privacy Edition (Windows)

[Mozc](https://github.com/google/mozc) をベースに [merge-ut-dictionaries](https://github.com/utuhiro78/merge-ut-dictionaries) を統合した、非公式のプライバシー重視 Windows 向け配布版です。

## 特徴

- **拡張辞書** — コミュニティ製 UT 辞書をビルド時に自動マージ
- **テレメトリなし** — 分析・追跡・クラウド変換サービスは一切なし
- **ローカル処理** — IME の変換はすべてローカルマシン上で実行
- **オプションのアップデータ** — 別途提供のアップデータは GitHub Releases のみを参照（[docs/NETWORK.md](docs/NETWORK.md) を参照）
- **ライセンス完全準拠** — 各リリースに `LICENSES.txt`、`THIRD_PARTY_LICENSES.txt`、`CREDITS.txt` を同梱

## ダウンロード

リリースは [GitHub Releases](https://github.com/mozc-ut-privacy/mozc-ut-privacy-windows/releases) ページで公開しています。

各リリースには次のファイルが含まれます。

| ファイル | 説明 |
|----------|------|
| `MozcUTPrivacy-{ver}-win-x64.msi` | x64 向けインストーラー |
| `MozcUTPrivacy-{ver}-win-arm64.msi` | ARM64 向けインストーラー |
| `MozcUTPrivacy-{ver}-win-{arch}-portable.zip` | ポータブル版 |
| `SHA256SUMS.txt` | 全バイナリのチェックサム |
| `MozcUTUpdater-{ver}-win-{arch}.exe` | オプションの自動アップデータ |

## クイックインストール

1. PC のアーキテクチャ（x64 または ARM64）に合った MSI をダウンロードする。
2. `SHA256SUMS.txt` と照合して SHA256 チェックサムを確認する。
3. インストーラーを**管理者権限**で実行する。
4. Windows 設定で **日本語** 入力言語が未追加なら追加する。
5. 入力方式として **Mozc UT Privacy Edition** を選択する。

### 「必要な情報を集めています」で終了する場合

このメッセージは MSI の準備段階（コスト計算）の表示です。直後に終了する場合、多くは次のいずれかが原因です。

| 原因 | 対処 |
|------|------|
| **管理者権限なし** | MSI を右クリック → **管理者として実行**。UAC で「はい」を選ぶ。 |
| **既にインストール済み** | インストール済みだと「再構成」が即終了します（ログ: `entering maintenance mode`）。IME が動かない場合は下記の修復コマンドを試してください。 |
| **より新しい版が入っている** | 同じかより新しいバージョンが入っていると終了します。設定 → アプリで確認し、必要ならアンインストールしてください。 |
| **アーキテクチャ不一致** | ARM64 PC では `*-win-arm64.msi`、x64 PC では `*-win-x64.msi` を使用してください。 |
| **詳細を確認したい** | 診断スクリプト（管理者 PowerShell）: `.\scripts\troubleshoot_msi.ps1 -MsiPath "C:\path\to\installer.msi"` |

**既にインストール済みの場合の修復（管理者 PowerShell）:**

```powershell
msiexec /fa "C:\path\to\MozcUTPrivacy-....msi" /l*v "$env:TEMP\mozc-ut-repair.log"
# または強制再インストール:
msiexec /i "C:\path\to\MozcUTPrivacy-....msi" REINSTALL=ALL REINSTALLMODE=amus /l*v "$env:TEMP\mozc-ut-reinstall.log"
```

## プライバシー保証

| コンポーネント | ネットワークアクセス |
|----------------|----------------------|
| IME（mozc_server、mozc_tip など） | **なし** |
| アップデータ（オプション） | GitHub Releases API のみ |
| ビルドパイプライン（CI） | 辞書ソースのみ。インストール済み IME には含まれない |

ネットワーク監査の詳細は [SECURITY.md](SECURITY.md) と [docs/NETWORK.md](docs/NETWORK.md) を参照してください。

## リポジトリ構成

```
mozc-ut-privacy-windows/
├── vendor/                  # Git サブモジュール（Mozc + merge-ut-dictionaries）
├── patches/                 # 上流向けの最小限パッチ
├── scripts/                 # ビルド・同期・ライセンス・リリース自動化
├── updater/                 # スタンドアロン C++ アップデータ
├── licenses/                # ライセンスマニフェストと全文
├── .github/workflows/       # CI/CD と月次上流同期
└── docs/                    # アーキテクチャとネットワークのドキュメント
```

## ローカルビルド

手順の詳細は [BUILD.md](BUILD.md) を参照してください。

## コントリビューション

[CONTRIBUTING.md](CONTRIBUTING.md) を参照してください。

## 免責事項

本プロジェクトは Google LLC とは**無関係**の非公式コミュニティプロジェクトです。Google LLC による後援・承認・保守はありません。「Mozc」は Mozc IME エンジンとの互換性を示す説明的な名称として使用しています。

## ライセンス

- プロジェクトのオーケストレーションコード: BSD-3-Clause（[licenses/project/BSD-3-Clause.txt](licenses/project/BSD-3-Clause.txt)）
- Mozc エンジン: BSD-3-Clause（[google/mozc](https://github.com/google/mozc)）
- merge-ut-dictionaries: Apache-2.0（[utuhiro78/merge-ut-dictionaries](https://github.com/utuhiro78/merge-ut-dictionaries)）
- 辞書データ: 複合ライセンス（[licenses/manifest.yaml](licenses/manifest.yaml) を参照）
