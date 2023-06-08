```!bash
brew install pip3
pip3 install virtualenv
cd golinks
virtualenv env
source env/bin/activate
pip3 install -r requirements.txt
uvicorn main:app reload
```

Go to http://localhost:8000/docs