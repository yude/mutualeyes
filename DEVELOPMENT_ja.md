# 開発

このドキュメントでは、mutualeyes を開発するために必要な作業について説明します。

## 推奨環境

このソフトウェアは、以下のツールチェーンを用いて開発することを推奨します。

- エディター: [Visual Studio Code](https://code.visualstudio.com/)
- マイクロコンピュータの操作: [mpremote](https://micropython-docs-ja.readthedocs.io/ja/latest/reference/mpremote.html)

また、デバイスを使用する難易度を考慮して、UNIX 系オペレーティングシステムを使用することを推奨します。以下の環境で動作を確認しています。

- 環境 1
    - Apple MacBook Air (M2, 2022)
    - macOS Sonoma 14.3
- 環境 2
    - Lenovo ThinkPad E14 Gen 3
    - Arch Linux (rolling, 2023/12/28)

## セットアップ

1. MicroPython ファームウェアの導入

    [MicroPython downloads - MicroPython](https://micropython.org/download/) から使用しようとしているマイクロコンピュータに適合する MicroPython ファームウェアをダウンロードし、書き込みます。書き込み方法については機種によって異なることがありますから、対応するドキュメントを参照してください。

    - [Raspberry Pi Pico (W)](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html)
    - [ESP32 / WROOM](https://micropython.org/download/ESP32_GENERIC/)
    
    インストール後コンピュータに接続すると、UNIX オペレーティングシステムでは `/dev/ttyACMX` または `/dev/ttyUSBY` のようなパスにデバイス ファイルが作成されます。これを使用してマイクロコンピュータとのデータの送受信を行います。

2. 前提ライブラリのインストール

    以下のコマンドを使用して、マイクロコンピュータにインストールされた MicroPython 環境に前提ライブラリをインストールします。
    ```shell
    mpremote connect [デバイス ファイルへのパス] mip install copy
    mpremote connect [デバイス ファイルへのパス] mip install logging
    mpremote connect [デバイス ファイルへのパス] mip install ntptime

    # 例:
    # mpremote connect /dev/ttyACM0 mount . run main.py
    ```

3. ソースコードのマウント、起動

    アプリケーションが動作しているログを取得するために、ローカルに存在する MicroPython ソースコードをマイクロコンピュータ上にマウントし、ログを取得しながら実行できます。

    ```shell
    cd src
    mpremote connect [デバイス ファイルへのパス] mount . run main.py
    
    # 例:
    # cd src
    # mpremote connect /dev/ttyUSB1 mount . run main.py
    ```
