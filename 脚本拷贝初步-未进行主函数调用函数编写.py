import sys
import clr
import time

# 添加 ZOS-API 路径
sys.path.append(r"C:\Program Files\Zemax OpticStudio\ZOS-API\Python")
clr.AddReference("ZOSAPI_Interfaces")
clr.AddReference("ZOSAPI_NetHelper")

from ZOSAPI import *
from ZOSAPI_NetHelper import *

def connect_to_zemax():
    """连接 Zemax OpticStudio"""
    connection = ZOSAPI_NetHelper.ZOSAPI_Initializer()
    connection.CreateNewApplication()
    app = connection.ConnectAsExtension(0)
    system = app.PrimarySystem
    return app, system
            
def run_optimization(system):
    """运行优化过程"""
    optimizer = system.Tools.OpenOptimizer()
    
    """print("开始全局优化...")
    optimizer.GlobalOptimization = True
    optimizer.RunAndWaitForCompletion()"""
    
    print("开始锤优化...")
    optimizer.HammerOptimization = True
    optimizer.HammerTime = 10  # 10分钟
    optimizer.RunAndWaitForCompletion()
    
    optimizer.Close()

def save_results(system, filename):
    """保存优化结果"""
    system.SaveAs(filename)
    print(f"优化结果已保存为: {filename}")

def analyze_results(system):
    """分析并打印优化结果"""
    # 获取评价函数值
    merit = system.MeritFunctions
    mf_value = merit.GetValue()
    print(f"最终评价函数值: {mf_value:.4f}")
    
    # 分析MTF
    analysis = system.Analyses
    mtf = analysis.New_Analysis_SettingsFirst(AnalysisIDM.FFTMTF)
    mtf.ApplyAndWaitForCompletion()
    mtf_results = mtf.GetResults().GetDataGrid(0).Values
    print("\nMTF结果:")
    for row in mtf_results:
        print(f"视场 {row[0]}°, 频率 {row[1]} lp/mm: {row[2]:.3f}")

def main():
    # 定义不同物距及其权重
    object_distances = {
        20: 0.5,
        50: 0.6,
        100: 0.7,
        150: 0.8,
        200: 0.9,
        250: 1.0,
        300: 1.0,
        350: 1.0,
        400: 1.0
    }

    try:
        # 1. 设置物距（通过修改面1的厚度）
        lens_data = system.LDE
        surface1 = lens_data.GetSurfaceAt(1)
        surface1.Thickness = object_distance  # 单位：毫米

        # 2. 运行优化（假设评价函数已预设操作数）
        optimizer = system.Tools.OpenOptimizer()
        optimizer.RunAndWaitForCompletion()
        optimizer.Close()

        # 3. 读取操作数评估值
        merit = system.MeritFunctions
        operand_values = []
        for i in range(merit.NumberOfOperands):
            op = merit.GetOperandAt(i)
            operand_values.append(op.Value)

        # 4. 写入CSV文件
        with open(output_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if object_distance == object_distances[0]:  # 仅在第一行写入标题
                headers = ["物距 (mm)"] + [f"操作数{i+1}" for i in range(len(operand_values))]
                writer.writerow(headers)
            writer.writerow([object_distance] + operand_values)

        print(f"物距 {object_distance}mm 优化完成，操作数值已保存。")

        # 5. 分析并保存结果
        analyze_results(system)
        save_results(system, r"C:\Optimized_Lens_Weighted.zmx")
        
    except Exception as e:
        print(f"错误: {e}")
    finally:
        app.CloseApplication()
        connection.Dispose()
        print("程序执行完成")
    
if __name__ == "__main__":
    main(
output_file = "operand_results.csv"  # 输出文件名

    # 清空或创建CSV文件
    with open(output_file, 'w', newline='') as f:
        pass

    # 遍历物距并优化
    for distance in object_distances:
        optimize_and_evaluate(distance, output_file)

    print("所有物距优化完成，结果已保存至", output_file)
        )
     
