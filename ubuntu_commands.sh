sudo apt-get update
sudo apt install python3-pip
sudo apt install git
sudo cd airflow
sudo python -m venv.venv
sudo python source .venv/bin/activate
sudo pip install -r requirements.txt
sudo python airflow standalone