# GPTMemoryBank

Work in progress

## How to launch

1. Create a virtual environment
```bash
python -m venv venv
```

2. Activate the virtual environment
```bash
PS: .\venv\Scripts\activate
Linux: source venv/bin/activate
```

3. Install the requirements
```bash
pip install -r requirements.txt
```

4. 

## Additional helpful things

python -m venv venv --clear
python -m pip list
python -m pip freeze > requirements.txt

ngrok http http://localhost:7000

## Elasticsearch related

$ openssl x509 -fingerprint -sha256 -noout -in /tmp/ca.crt | awk -F"=" {' print $2 '} | sed s/://g

$ cat /tmp/ca.crt