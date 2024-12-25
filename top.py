import os
import shutil
import tkinter as tk
from tkinter import messagebox
from makefile_base import *


class LibProcessor:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LIB文件夹处理工具")
        # 初始化路径
        self.script_dir = os.path.dirname(os.path.abspath(__file__))  # 脚本所在路径
        self.lib_folder = os.path.join(self.script_dir, "LIB")  # LIB文件夹路径
        self.output_folder = os.path.join(self.script_dir, "output")  # output文件夹路径
        self.output_script_dir = os.path.join(self.output_folder, "scripts")  # output文件夹路径
        # self.mf_base_path = os.path.join(self.script_dir, "mf_base.py")  # 顶层的 mf_base.py 文件路径

        # 检查路径是否存在
        if not os.path.exists(self.lib_folder):
            raise FileNotFoundError(f"LIB文件夹未找到：{self.lib_folder}")
        # if not os.path.isfile(self.mf_base_path):
        #     raise FileNotFoundError(f"mf_base.py 文件未找到：{self.mf_base_path}")

        self.subfolders = [f for f in os.listdir(self.lib_folder) if os.path.isdir(os.path.join(self.lib_folder, f))]
        self.selected_folders = {subfolder: tk.BooleanVar() for subfolder in self.subfolders}

        # GUI 界面
        self.setup_ui()

    def setup_ui(self):
        """设置图形界面"""
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text=f"LIB文件夹路径: {self.lib_folder}").grid(row=0, column=0, sticky="w")

        # Checkbutton 列表
        for idx, subfolder in enumerate(self.subfolders):
            tk.Checkbutton(frame, text=subfolder, variable=self.selected_folders[subfolder]).grid(row=idx + 1, column=0, sticky="w")

        button_process = tk.Button(frame, text="处理选中子文件夹", command=self.process_files)
        button_process.grid(row=len(self.subfolders) + 1, column=0, pady=10)

    def generate_makefile(self, folder_list):
        """生成Makefile文件"""
        # 拼接MF内容
        concatenated_text = ""

        # 去重：仅拼接唯一内容
        added_sections = set()
        for folder in folder_list:
            if folder in MF_TEXTS and MF_TEXTS[folder].strip() not in added_sections:
                concatenated_text += "\n\n" + MF_TEXTS[folder].strip()
                added_sections.add(MF_TEXTS[folder].strip())

        concatenated_text += "\n\n" + MF_TEXTS["base"].strip()
        # 输出拼接结果
        output_file = os.path.join(self.output_script_dir, "Makefile")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(concatenated_text)

        print(f"拼接完成，结果保存至: {output_file}")

    def process_files(self):
        """处理选中的文件夹"""
        selected = [folder for folder, var in self.selected_folders.items() if var.get()]
        if not selected:
            messagebox.showwarning("提示", "请选择至少一个子文件夹")
            return

        if os.path.exists(self.output_folder):
            shutil.rmtree(self.output_folder)
        else:
            os.makedirs(self.output_folder)

        # try:
            # 1. 拷贝子文件夹到output
        for folder_name in selected:
            subfolder_path = os.path.join(self.lib_folder, folder_name)
            def ignore_scripts(folder, contents):
                # 忽略名为 'scripts' 的文件夹
                if folder == subfolder_path:
                    return ["scripts"] if "scripts" in contents else []
                return []
            shutil.copytree(subfolder_path, os.path.join(self.output_folder, folder_name), dirs_exist_ok=True, ignore=ignore_scripts)

        # 2. 拼接Makefile
        self.generate_makefile(selected)

        # 3. 拷贝script到output
        for folder_name in selected:
            scripts_folder = os.path.join(self.lib_folder, folder_name, "scripts")
            if os.path.exists(scripts_folder) and os.path.isdir(scripts_folder):
                for file_name in os.listdir(scripts_folder):
                    if file_name.endswith(".cshrc"):
                        src_file = os.path.join(scripts_folder, file_name)
                        dst_file = os.path.join(self.output_script_dir, f"{os.path.basename(folder_name)}_setup.cshrc")
                        shutil.copy(src_file, dst_file)
            else:
                print(f"Scripts folder not found in {folder_name}")

        # for src_folder in src_folders:
        #     # Construct the path to the scripts folder
        #     scripts_folder = os.path.join(src_folder, "scripts")

        #     if os.path.exists(scripts_folder) and os.path.isdir(scripts_folder):
        #         # Find all .py files in the scripts folder
        #         for file_name in os.listdir(scripts_folder):
        #             if file_name.endswith(".py"):
        #                 # Construct full paths
        #                 src_file = os.path.join(scripts_folder, file_name)
        #                 dst_file = os.path.join(dst_folder, f"{os.path.basename(src_folder)}_test.py")

        #                 # Copy and rename the file
        #                 shutil.copy(src_file, dst_file)
        #                 print(f"Copied and renamed: {src_file} -> {dst_file}")
        #     else:
        #         print(f"Scripts folder not found in {src_folder}")``

        # 4
        # 5. 提示完成
        messagebox.showinfo("成功", "操作完成！文件已生成到output文件夹中")
        # except Exception as e:
        #     messagebox.showerror("错误", f"处理文件时出错：{e}")
        #     print("错误", f"处理文件时出错：{e}")

    def run(self):
        """运行程序"""
        self.root.mainloop()


if __name__ == "__main__":
    try:
        processor = LibProcessor()
        processor.run()
    except FileNotFoundError as e:
        messagebox.showerror("错误", str(e))
    except Exception as ex:
        print("意外错误", f"程序出现问题：{ex}")
