# -*- coding: utf-8 -*-
from .base import BaseTool
from .base import PrintUtils, CmdTask, FileUtils, AptUtils, ChooseTask
from .base import osversion, osarch
from .base import run_tool_file

start_clash_sh = """export CLASH_SERVER=\"{server_url}\"
cd {clash_home}
unset http_proxy
unset https_proxy
mkdir -p $HOME/.config/clash
wget $CLASH_SERVER -O $HOME/.config/clash/config.yaml
sed -i 's/127.0.0.1:9090/0.0.0.0:9090/g'  $HOME/.config/clash/config.yaml
sed -i 's/allow-lan: false/allow-lan: true/g'  $HOME/.config/clash/config.yaml
file_url=\"http://github.fishros.org/https://github.com/Dreamacro/maxmind-geoip/releases/download/20230912/Country.mmdb\"
target_dir=\"$HOME/.config/clash/\"
if [ ! -e \"${target_dir}Country.mmdb\" ]; then
    wget -O \"${target_dir}Country.mmdb\" \"$file_url\"
    if [ $? -eq 0 ]; then
        echo \"文件下载成功。\"
    else
        echo \"文件下载失败。\"
        exit 1
    fi
else
    echo \"文件已存在，无需下载。\"
fi
cd $HOME/.clash/public && python3 -m http.server --bind 0.0.0.0 8088 &
sleep 1
chmod +x ./clash
export http_proxy=\"http://127.0.0.1:7890\"
export https_proxy=\"http://127.0.0.1:7890\"
echo \"===============================================\"
echo \"终端通过环境变量设置: export http_proxy=http://127.0.0.1:7890 && export https_proxy=http://127.0.0.1:7890\"
echo \"系统设置默认代理方式: 系统设置->网络->网络代理->手动->HTTP(127.0.0.1 7890)->HTTPS(127.0.0.1 7890)\"
echo \"管理页面方法：https://fishros.org.cn/forum/topic/668 \"
echo \"===============================================\"
xdg-open http://127.0.0.1:8088/ >> /dev/null &
./clash
"""

start_clash_desktop = """[Desktop Entry]
Type=Application
Exec=gnome-terminal -e \"/bin/bash {script_path}\"
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name[zh_CN]=启动代理
Name=clash
Comment[zh_CN]=
Comment=
"""

class Tool(BaseTool):
    def __init__(self):
        self.name = "一键安装 Linux 代理科学上网工具"
        self.type = BaseTool.TYPE_INSTALL
        self.author = 'booq'

    def install_web_tool(self, clash_home):
        CmdTask('sudo apt update  && sudo apt install xz-utils -y', os_command=True).run()
        CmdTask('wget http://github.fishros.org/https://github.com/haishanh/yacd/releases/download/v0.3.8/yacd.tar.xz -O {}yacd.tar.xz'.format(clash_home), os_command=True).run()
        CmdTask('cd {} && tar -xf yacd.tar.xz'.format(clash_home), os_command=True).run()

    def install_proxy_tool(self):
        PrintUtils.print_info("开始根据系统架构下载 clash")
        user_home = FileUtils.getusershome()[0]
        clash_home = f"{user_home}/.clash/"
        CmdTask(f"mkdir -p {clash_home}", os_command=True).run()

        if osarch=='amd64':
            CmdTask('sudo wget http://github.fishros.org/https://raw.githubusercontent.com/tuomasiy/mlash/main/clash -O {}clash'.format(clash_home),os_command=True).run()
        elif osarch=='arm64':
            CmdTask('sudo wget https://down.clash.la/Clash/Core/Premium/clash-linux-arm64-latest.gz -O {}clash.gz'.format(clash_home),os_command=True).run()
        else:
            PrintUtils.print_error("未支持的架构")
            return False
        PrintUtils.print_info("下载完成~")
        check_file = f"{clash_home}clash"
        if not os.path.exists(check_file) or os.path.getsize(check_file) == 0:
            PrintUtils.print_error("clash 下载失败，请检查网络")
            return False

        CmdTask(f'chmod +x {check_file}', os_command=True).run()
        PrintUtils.print_warn("请输入 CLASH 订阅地址")
        serve_url = input("订阅地址:")

        self.install_web_tool(clash_home)
        FileUtils.new(path=clash_home, name="start_clash.sh", data=start_clash_sh.replace("{clash_home}", clash_home).replace("{server_url}", serve_url))
        CmdTask(f'chmod +x {clash_home}start_clash.sh', os_command=True).run()

        auto_start_path = f"{user_home}/.config/autostart/"
        dic = {1: "设置开机自启动", 2: "不设置开机自启动"}
        code, _ = ChooseTask(dic, "是否设置为开机自启动?").run()
        if code == 2:
            FileUtils.delete(auto_start_path + "start_clash.desktop")
        if code == 1:
            CmdTask('sudo apt install gnome-terminal -y', os_command=True).run()
            FileUtils.new(path=auto_start_path, name="start_clash.desktop", data=start_clash_desktop.replace("{script_path}", clash_home + "start_clash.sh"))
            CmdTask(f'chmod +x {auto_start_path}start_clash.desktop', os_command=True).run()

        PrintUtils.print_info("已配置 clash 启动脚本，可通过终端或桌面启动")

    def run(self):
        self.install_proxy_tool()