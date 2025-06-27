#!/usr/bin/env python3
"""
ELYZA評価システム - rubrics.pyと連携してタスク番号から評価関数と引数を取得

このモジュールは自動生成されたrubrics.pyをimportし、
タスク番号からcallableとjudge_argsを返す機能を提供します。
"""

import ast
import importlib
import inspect
from typing import Tuple, List, Callable, Optional


def extract_judge_args_from_ast(code: str) -> List[str]:
    """
    ASTを使ってjudge()呼び出しの引数を抽出
    
    Args:
        code: Pythonコード（関数定義）
        
    Returns:
        List[str]: judge()の引数のリスト
    """
    judge_args = []
    
    try:
        tree = ast.parse(code)
        
        class JudgeCallVisitor(ast.NodeVisitor):
            def visit_Call(self, node):
                # judge("...") の形式をチェック
                if (isinstance(node.func, ast.Name) and 
                    node.func.id == 'judge' and 
                    len(node.args) == 1):
                    
                    # 文字列リテラルの場合
                    if isinstance(node.args[0], ast.Str):
                        judge_args.append(node.args[0].s)
                    # Python 3.8+のast.Constantの場合
                    elif isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                        judge_args.append(node.args[0].value)
                
                self.generic_visit(node)
        
        visitor = JudgeCallVisitor()
        visitor.visit(tree)
        
    except Exception as e:
        print(f"AST解析エラー: {e}")
        
    return judge_args


def get_judge_function_and_args(task_number: int) -> Tuple[Optional[Callable], List[str]]:
    """
    タスク番号からcallableとjudge_argsを返す
    
    Args:
        task_number: タスク番号（1-100）
        
    Returns:
        Tuple[Optional[Callable], List[str]]: (judge関数, judge引数のリスト)
        関数が見つからない場合は(None, [])を返す
    """
    try:
        # rubrics.pyをインポート
        import rubrics
        
        # 関数名を生成
        function_name = f"judge_{task_number:03d}"
        
        # 関数を取得
        if hasattr(rubrics, function_name):
            judge_function = getattr(rubrics, function_name)
            
            # 関数のソースコードを取得してASTで解析
            try:
                source_code = inspect.getsource(judge_function)
                judge_args = extract_judge_args_from_ast(source_code)
                return judge_function, judge_args
                
            except (OSError, TypeError) as e:
                print(f"ソースコード取得エラー ({function_name}): {e}")
                return judge_function, []
                
        else:
            print(f"関数 {function_name} が見つかりません")
            return None, []
            
    except ImportError as e:
        print(f"rubrics.pyのインポートエラー: {e}")
        return None, []
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return None, []


def list_available_judges() -> List[int]:
    """
    利用可能なjudge関数のタスク番号一覧を取得
    
    Returns:
        List[int]: 利用可能なタスク番号のリスト
    """
    try:
        import rubrics
        
        available_tasks = []
        
        # rubricsモジュールの全属性をチェック
        for attr_name in dir(rubrics):
            if attr_name.startswith('judge_') and callable(getattr(rubrics, attr_name)):
                # タスク番号を抽出
                try:
                    task_num_str = attr_name.replace('judge_', '')
                    task_num = int(task_num_str)
                    available_tasks.append(task_num)
                except ValueError:
                    continue
        
        return sorted(available_tasks)
        
    except ImportError:
        print("rubrics.pyが見つかりません")
        return []


def test_judge_function(task_number: int, test_queries: List[str] = None) -> None:
    """
    judge関数をテストする
    
    Args:
        task_number: タスク番号
        test_queries: テスト用クエリのリスト（Noneの場合は抽出した引数を使用）
    """
    judge_func, judge_args = get_judge_function_and_args(task_number)
    
    if judge_func is None:
        print(f"タスク {task_number} の関数が見つかりません")
        return
    
    print(f"=== タスク {task_number:03d} のテスト ===")
    print(f"関数: {judge_func.__name__}")
    print(f"抽出された引数: {len(judge_args)}個")
    
    for i, arg in enumerate(judge_args):
        print(f"  {i+1}. {arg}")
    
    # テスト用のjudge関数を作成
    test_queries_to_use = test_queries or judge_args
    
    def mock_judge(query: str) -> bool:
        """テスト用のjudge関数"""
        return query in test_queries_to_use
    
    # 関数を実行してテスト
    try:
        initial_score = 5
        result = judge_func(initial_score, mock_judge)
        print(f"テスト実行結果: {initial_score} -> {result}")
        
    except Exception as e:
        print(f"テスト実行エラー: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="ELYZA評価システム - judge関数の管理と実行",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""例:
  python elyza.py --list                    # 利用可能なjudge関数一覧
  python elyza.py --test 1                  # タスク001のテスト実行
  python elyza.py --get-args 5              # タスク005の引数を表示
"""
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="利用可能なjudge関数一覧を表示")
    group.add_argument("--test", type=int, help="指定したタスクのjudge関数をテスト")
    group.add_argument("--get-args", type=int, help="指定したタスクの引数を表示")
    
    args = parser.parse_args()
    
    if args.list:
        available = list_available_judges()
        print(f"利用可能なjudge関数: {len(available)}個")
        for task_num in available:
            print(f"  judge_{task_num:03d}")
            
    elif args.test:
        test_judge_function(args.test)
        
    elif args.get_args:
        judge_func, judge_args = get_judge_function_and_args(args.get_args)
        if judge_func:
            print(f"タスク {args.get_args:03d} の引数:")
            for i, arg in enumerate(judge_args):
                print(f"  {i+1}. {arg}")
        else:
            print(f"タスク {args.get_args} が見つかりません")