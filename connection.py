import os
import pymysql
from dotenv import load_dotenv

def get_connection():
    """
    データベースへの接続を取得します。

    Args:
        db_name (str, optional): 接続するデータベース名。Noneの場合はデフォルトDB。

    Returns:
        pymysql.connections.Connection: データベース接続オブジェクト
    """

    DB_HOST = "localhost"
    DB_USER = "入力してください"
    DB_PASSWORD = "入力してください"
    DB_NAME = "入力してください"
    DB_CHARSET = "utf8"

    try:
        return pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            db=DB_NAME,
            charset=DB_CHARSET,
            cursorclass=pymysql.cursors.DictCursor
        )
    except Exception as e:
        print(f"DB接続エラー: {e}")
        raise


def test_connection():
    """
    データベース接続のテスト関数
    """
    print("=== データベース接続テスト ===")
    
    try:
        # デフォルトデータベースへの接続テスト
        print("1. デフォルトデータベースへの接続テスト...")
        conn = get_connection()
        print("✅ デフォルトデータベース接続成功")
        
        # 基本的なクエリテスト
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"✅ クエリテスト成功: {result}")
        
        conn.close()
        print("✅ デフォルトデータベース接続終了")
        
    except Exception as e:
        print(f"❌ デフォルトデータベース接続エラー: {e}")
        return False
    
    try:
        # chatbot_dbデータベースへの接続テスト
        print("\n2. chatbot_dbデータベースへの接続テスト...")
        conn = get_connection('chatbot_db')
        print("✅ chatbot_dbデータベース接続成功")
        
        # 基本的なクエリテスト
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            print(f"✅ クエリテスト成功: {result}")
        
        conn.close()
        print("✅ chatbot_dbデータベース接続終了")
        
    except Exception as e:
        print(f"❌ chatbot_dbデータベース接続エラー: {e}")
        return False
    
    print("\n🎉 すべてのデータベース接続テストが成功しました！")
    return True


def test_table_access():
    """
    主要テーブルへのアクセステスト
    """
    print("\n=== テーブルアクセステスト ===")
    
    try:
        conn = get_connection()
        
        # 主要テーブルの存在確認
        tables_to_check = [
            'tUserM',
            'tClientM', 
            'tReservationF',
            'tTaioF',
            'tSettingM'
        ]
        
        for table in tables_to_check:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = cursor.fetchone()
                    print(f"✅ {table}: {result['count']}件のレコード")
            except Exception as e:
                print(f"❌ {table}: アクセスエラー - {e}")
        
        conn.close()
        print("\n🎉 テーブルアクセステスト完了！")
        return True
        
    except Exception as e:
        print(f"❌ テーブルアクセステストエラー: {e}")
        return False


def show_connection_info():
    """
    接続設定情報を表示
    """
    print("=== 接続設定情報 ===")
    print(f"デフォルトDB: skoji_77")
    print(f"ホスト: 192.168.98.42")
    print(f"ユーザー: root")
    print(f"パスワード: 2wsx#EDC")
    print(f"文字セット: utf8")
    print()


def show_troubleshooting():
    """
    トラブルシューティング情報を表示
    """
    print("=== トラブルシューティング ===")
    print("1. MySQLサーバーが起動しているか確認")
    print("   sudo systemctl status mysql")
    print("   # または")
    print("   brew services list | grep mysql")
    print()
    print("2. ネットワーク接続を確認")
    print("   ping 192.168.98.42")
    print("   telnet 192.168.98.42 3306")
    print()
    print("3. MySQLユーザーの権限を確認")
    print("   mysql -u root -p")
    print("   SELECT user, host FROM mysql.user WHERE user='root';")
    print("   GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '2wsx#EDC';")
    print("   FLUSH PRIVILEGES;")
    print()
    print("4. ファイアウォール設定を確認")
    print("   sudo ufw status")
    print("   sudo ufw allow 3306")
    print()
    print("5. 接続設定を変更する場合")
    print("   connection.pyのDB_HOST, DB_USER, DB_PASSWORD, DB_NAMEを修正")
    print()


def test_network_connectivity():
    """
    ネットワーク接続をテスト
    """
    import socket
    print("=== ネットワーク接続テスト ===")
    
    try:
        # ホスト名の解決
        print(f"1. ホスト名解決テスト: 192.168.98.42")
        socket.gethostbyname("192.168.98.42")
        print("✅ ホスト名解決成功")
    except Exception as e:
        print(f"❌ ホスト名解決失敗: {e}")
        return False
    
    try:
        # ポート接続テスト
        print("2. ポート接続テスト: 192.168.98.42:3306")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(("192.168.98.42", 3306))
        sock.close()
        
        if result == 0:
            print("✅ ポート3306接続成功")
        else:
            print("❌ ポート3306接続失敗")
            return False
    except Exception as e:
        print(f"❌ ポート接続テスト失敗: {e}")
        return False
    
    print("✅ ネットワーク接続テスト成功")
    return True


def main():
    """
    メイン関数 - データベース接続とテーブルアクセスのテスト
    """
    print("データベース接続テストを開始します...\n")
    
    # 接続設定情報を表示
    show_connection_info()
    
    # ネットワーク接続テスト
    network_success = test_network_connectivity()
    
    if not network_success:
        print("\n❌ ネットワーク接続に問題があります。")
        show_troubleshooting()
        return
    
    # 接続テスト
    connection_success = test_connection()
    
    if connection_success:
        # テーブルアクセステスト
        table_success = test_table_access()
        
        if table_success:
            print("\n🎊 すべてのテストが成功しました！")
            print("ishokuフォルダーの機能が正常に動作する準備が整いました。")
        else:
            print("\n⚠️ テーブルアクセスに問題があります。")
    else:
        print("\n❌ データベース接続に問題があります。")
        show_troubleshooting()


if __name__ == "__main__":
    main()