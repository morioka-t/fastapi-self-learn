## 実行コマンド
```
apt install python39
sudo apt upgrade -y
pip install --upgrade pip     && pip install uvicorn fastapi     && pip install sqlalchemy     && pip install -r requirements.txt
pip install --upgrade pip
docker build . -t fastapi
sudo apt install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install docker-ce
sudo systemctl status docker
docker build . -t fastapi
docker image ls
docker run -p 8000:8000 -it bef70bec4e42
apt install python3-pip
pip3 install --upgrade pip
sudo apt update
pip install --upgrade pip
apt install python3.12-venv
python3 -m venv ~/mypy
source ~/mypy/bin/activate
pip install --upgrade pip
pip install uvicorn fastapi
pip install sqlalchemy
pip install -r requirements.txt
unicorn main:app --host 0.0.0.0 --port 8000 --reload
```
