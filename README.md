# Backend

## Running application locally

```shell
pip install -r requirements.txt
```

```shell
python -m uvicorn app.main:app --reload
```

<div style="font-family: monospace; background-color: #f5; padding: 15px; border-radius: 5px;">
<pre>
couple_bot_backend/
├── app/
│   ├── __init__.py
│   ├── main.py         
│   ├── models.py        
│   ├── schemas.py       
│   ├── crud.py          
│   ├── database.py      
│   ├── routers/
│   │   ├── users.py     
│   │   ├── pairs.py     
│   │   ├── ideas.py     
│   │   └── events.py    
│   └── utils.py         
├── tests/              
├── .env               
├── requirements.txt     
└── README.md           
</pre>
</div>