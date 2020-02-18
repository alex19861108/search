WORK_DIR=$(cd $(dirname $0); pwd; cd - >/dev/null)
export PIP_CONFIG_FILE=$WORK_DIR/.pip/pip.conf
pip install -r requirements.txt
